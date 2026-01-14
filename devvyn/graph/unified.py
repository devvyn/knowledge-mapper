"""
Unified prerequisite graph spanning multiple institutions.

Enables queries like:
- What courses at any institution prepare me for X?
- What paths exist from entry-level to a target course/program?
- How do courses at one institution map to another?
"""
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from devvyn.institutions.base import CourseReference, UnifiedCourse, UnifiedProgram
from devvyn.institutions.registry import get_registry, InstitutionRegistry


@dataclass
class TransferEquivalency:
    """
    A transfer credit equivalency between institutions.

    Indicates that course_from at one institution is recognized as
    equivalent to course_to at another institution.
    """
    course_from: CourseReference
    course_to: CourseReference
    notes: str = ""
    bidirectional: bool = False  # If True, equivalency works both ways


@dataclass
class UnifiedPrerequisiteGraph:
    """
    Prerequisite graph spanning multiple institutions.

    Nodes are CourseReferences, edges are prerequisite relationships.
    Can also include transfer credit equivalencies as edges.
    """

    # course_ref → set of courses that depend on it
    _forward: dict[CourseReference, set[CourseReference]] = field(
        default_factory=lambda: defaultdict(set)
    )

    # course_ref → set of courses it depends on (prerequisites)
    _backward: dict[CourseReference, set[CourseReference]] = field(
        default_factory=lambda: defaultdict(set)
    )

    # All known courses
    _courses: dict[CourseReference, UnifiedCourse] = field(default_factory=dict)

    # Transfer equivalencies
    _equivalencies: list[TransferEquivalency] = field(default_factory=list)

    # Equivalency lookup: course_ref → set of equivalent courses
    _equiv_map: dict[CourseReference, set[CourseReference]] = field(
        default_factory=lambda: defaultdict(set)
    )

    def add_course(self, course: UnifiedCourse) -> None:
        """Add a course to the graph."""
        self._courses[course.ref] = course

        # Add prerequisite edges
        for prereq_ref in course.prerequisites:
            self._forward[prereq_ref].add(course.ref)
            self._backward[course.ref].add(prereq_ref)

    def add_equivalency(self, equiv: TransferEquivalency) -> None:
        """Add a transfer equivalency."""
        self._equivalencies.append(equiv)
        self._equiv_map[equiv.course_from].add(equiv.course_to)
        if equiv.bidirectional:
            self._equiv_map[equiv.course_to].add(equiv.course_from)

    def get_course(self, ref: CourseReference) -> Optional[UnifiedCourse]:
        """Get a course by reference."""
        return self._courses.get(ref)

    @property
    def courses(self) -> set[CourseReference]:
        """All course references in the graph."""
        return set(self._courses.keys())

    def courses_at(self, institution: str) -> set[CourseReference]:
        """Get all courses at a specific institution."""
        return {ref for ref in self._courses if ref.institution == institution}

    def prerequisites_for(
        self,
        ref: CourseReference,
        transitive: bool = True,
        cross_institution: bool = False
    ) -> set[CourseReference]:
        """
        Get prerequisites for a course.

        Args:
            ref: Course reference
            transitive: If True, include prerequisites of prerequisites
            cross_institution: If True, include equivalent courses at other institutions

        Returns:
            Set of prerequisite course references
        """
        if not transitive:
            prereqs = self._backward.get(ref, set()).copy()
            if cross_institution:
                for p in list(prereqs):
                    prereqs.update(self._equiv_map.get(p, set()))
            return prereqs

        # BFS for transitive prerequisites
        visited = set()
        queue = list(self._backward.get(ref, []))

        while queue:
            prereq = queue.pop(0)
            if prereq in visited:
                continue
            visited.add(prereq)
            queue.extend(self._backward.get(prereq, []))

            # Add equivalencies if requested
            if cross_institution:
                for equiv in self._equiv_map.get(prereq, []):
                    if equiv not in visited:
                        queue.append(equiv)

        return visited

    def unlocks(
        self,
        ref: CourseReference,
        transitive: bool = True,
        cross_institution: bool = False
    ) -> set[CourseReference]:
        """
        Get courses that this course unlocks.

        Args:
            ref: Course reference
            transitive: If True, include courses unlocked by unlocked courses
            cross_institution: If True, include courses at other institutions
                              that accept this course via transfer

        Returns:
            Set of course references that depend on this course
        """
        if not transitive:
            unlocked = self._forward.get(ref, set()).copy()
            if cross_institution:
                # Check if any equivalent courses unlock things
                for equiv in self._equiv_map.get(ref, []):
                    unlocked.update(self._forward.get(equiv, set()))
            return unlocked

        # BFS for transitive dependents
        visited = set()
        queue = list(self._forward.get(ref, []))

        # Also start from equivalent courses
        if cross_institution:
            for equiv in self._equiv_map.get(ref, []):
                queue.extend(self._forward.get(equiv, []))

        while queue:
            dependent = queue.pop(0)
            if dependent in visited:
                continue
            visited.add(dependent)
            queue.extend(self._forward.get(dependent, []))

            if cross_institution:
                for equiv in self._equiv_map.get(dependent, []):
                    if equiv not in visited:
                        queue.append(equiv)

        return visited

    def equivalents(self, ref: CourseReference) -> set[CourseReference]:
        """Get all courses equivalent to this one (at any institution)."""
        return self._equiv_map.get(ref, set()).copy()

    def find_paths(
        self,
        start_institution: str,
        end_ref: CourseReference,
        max_depth: int = 10
    ) -> list[list[CourseReference]]:
        """
        Find paths from entry-level courses at an institution to a target.

        Useful for answering: "How do I get from SaskPolytech to USask CMPT 280?"

        Args:
            start_institution: Institution to start from
            end_ref: Target course
            max_depth: Maximum path length

        Returns:
            List of paths, each path is a list of CourseReferences
        """
        # Find entry points at the start institution
        entry_points = [
            ref for ref in self.courses_at(start_institution)
            if not self._backward.get(ref)
        ]

        paths = []
        for entry in entry_points:
            self._find_paths_dfs(entry, end_ref, [entry], paths, max_depth)

        return paths

    def _find_paths_dfs(
        self,
        current: CourseReference,
        target: CourseReference,
        path: list[CourseReference],
        all_paths: list[list[CourseReference]],
        max_depth: int
    ) -> None:
        """DFS helper for finding paths."""
        if len(path) > max_depth:
            return

        if current == target:
            all_paths.append(path.copy())
            return

        # Follow forward edges
        for next_ref in self._forward.get(current, []):
            if next_ref not in path:
                path.append(next_ref)
                self._find_paths_dfs(next_ref, target, path, all_paths, max_depth)
                path.pop()

        # Also follow equivalency edges
        for equiv in self._equiv_map.get(current, []):
            if equiv not in path:
                path.append(equiv)
                self._find_paths_dfs(equiv, target, path, all_paths, max_depth)
                path.pop()

    def stats(self) -> dict:
        """Get graph statistics."""
        institutions = defaultdict(int)
        for ref in self._courses:
            institutions[ref.institution] += 1

        return {
            "total_courses": len(self._courses),
            "total_edges": sum(len(deps) for deps in self._forward.values()),
            "total_equivalencies": len(self._equivalencies),
            "institutions": dict(institutions),
        }


async def build_unified_graph(
    registry: Optional[InstitutionRegistry] = None,
    subjects: Optional[dict[str, list[str]]] = None,
    programs: Optional[dict[str, list[str]]] = None,
) -> UnifiedPrerequisiteGraph:
    """
    Build a unified graph from multiple institutions.

    Args:
        registry: Institution registry (uses global if not provided)
        subjects: Dict of institution_id → list of subject codes to load
                  e.g., {"usask": ["CMPT", "MATH"]}
        programs: Dict of institution_id → list of program codes to load
                  e.g., {"saskpolytech": ["CSTDP", "CENGDIPFD"]}

    Returns:
        UnifiedPrerequisiteGraph with courses from specified sources
    """
    if registry is None:
        registry = get_registry()

    graph = UnifiedPrerequisiteGraph()

    # Load subjects
    if subjects:
        for inst_id, subj_list in subjects.items():
            adapter = registry.get(inst_id)
            if not adapter:
                continue

            async with adapter:
                for subject in subj_list:
                    courses = await adapter.get_courses_by_subject(subject)
                    for course in courses:
                        graph.add_course(course)

    # Load programs
    if programs:
        for inst_id, prog_list in programs.items():
            adapter = registry.get(inst_id)
            if not adapter:
                continue

            async with adapter:
                for prog_code in prog_list:
                    program = await adapter.get_program(prog_code)
                    if program:
                        for course in program.courses:
                            graph.add_course(course)

    return graph


def build_unified_graph_sync(
    subjects: Optional[dict[str, list[str]]] = None,
    programs: Optional[dict[str, list[str]]] = None,
) -> UnifiedPrerequisiteGraph:
    """Synchronous wrapper for build_unified_graph."""
    return asyncio.run(build_unified_graph(subjects=subjects, programs=programs))


# --- Known Transfer Equivalencies ---
# These are manually curated based on transfer agreements

def add_known_equivalencies(graph: UnifiedPrerequisiteGraph) -> None:
    """
    Add known transfer credit equivalencies to the graph.

    Based on transfer agreements between Saskatchewan institutions.
    """
    # SaskPolytech CST → USask CMPT (common transfers)
    # These would need to be verified with actual transfer guides

    # Example equivalencies (placeholder - need actual data):
    # graph.add_equivalency(TransferEquivalency(
    #     course_from=CourseReference("saskpolytech", "COSC 180"),
    #     course_to=CourseReference("usask", "CMPT 140"),
    #     notes="Intro programming transfer"
    # ))

    pass  # TODO: Add actual equivalencies from transfer guides


async def demo():
    """Demo the unified graph."""
    print("Building unified graph...")
    print("  Loading USask CMPT courses...")
    print("  Loading SaskPolytech CST program...")

    graph = await build_unified_graph(
        subjects={"usask": ["CMPT"]},
        programs={"saskpolytech": ["CSTDP"]},
    )

    print(f"\nGraph stats: {graph.stats()}")

    # Show courses by institution
    print("\n=== Courses by Institution ===")
    for inst_id in ["usask", "saskpolytech"]:
        courses = graph.courses_at(inst_id)
        print(f"{inst_id}: {len(courses)} courses")

    # Query example
    print("\n=== USask CMPT 280 Prerequisites ===")
    ref = CourseReference("usask", "CMPT 280")
    prereqs = graph.prerequisites_for(ref)
    for p in sorted(prereqs, key=str):
        course = graph.get_course(p)
        title = course.title if course else "Unknown"
        print(f"  {p}: {title}")

    print("\n=== SaskPolytech PROJ 273 Prerequisites ===")
    ref = CourseReference("saskpolytech", "PROJ 273")
    prereqs = graph.prerequisites_for(ref)
    for p in sorted(prereqs, key=str):
        course = graph.get_course(p)
        title = course.title if course else "Unknown"
        print(f"  {p}: {title}")


if __name__ == "__main__":
    asyncio.run(demo())
