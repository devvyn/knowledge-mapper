"""
Prerequisite graph for course dependency analysis.

Build a directed graph from course prerequisites and query:
- What courses are needed for X (transitive)?
- What courses does X unlock?
- What's the path from entry-level to X?
"""
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from devvyn.api.usask_catalogue import USaskCatalogueClient
from devvyn.parse.prerequisites import parse_prerequisites


@dataclass
class PrerequisiteGraph:
    """
    Directed graph of course prerequisites.

    Edges point from prerequisite → dependent course.
    (e.g., CMPT 141 → CMPT 145 means "141 is a prerequisite for 145")
    """

    # course_id → set of courses that depend on it
    _forward: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    # course_id → set of courses it depends on (prerequisites)
    _backward: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    # All known courses
    _courses: set[str] = field(default_factory=set)

    def add_edge(self, prereq: str, course: str) -> None:
        """Add a prerequisite relationship."""
        prereq = self._normalize(prereq)
        course = self._normalize(course)
        self._forward[prereq].add(course)
        self._backward[course].add(prereq)
        self._courses.add(prereq)
        self._courses.add(course)

    def _normalize(self, course: str) -> str:
        """Normalize course code format."""
        # Remove credit suffix (.3), normalize spacing
        course = course.upper().strip()
        if "." in course:
            course = course.split(".")[0]
        # Ensure space between subject and number: "CMPT141" → "CMPT 141"
        if " " not in course:
            for i, c in enumerate(course):
                if c.isdigit():
                    course = course[:i] + " " + course[i:]
                    break
        return course

    @property
    def courses(self) -> set[str]:
        """All courses in the graph."""
        return self._courses.copy()

    def prerequisites_for(self, course: str, transitive: bool = True) -> set[str]:
        """
        Get prerequisites for a course.

        Args:
            course: Course code (e.g., "CMPT 145")
            transitive: If True, include prerequisites of prerequisites

        Returns:
            Set of prerequisite course codes
        """
        course = self._normalize(course)
        if not transitive:
            return self._backward.get(course, set()).copy()

        # BFS for transitive prerequisites
        visited = set()
        queue = list(self._backward.get(course, []))

        while queue:
            prereq = queue.pop(0)
            if prereq in visited:
                continue
            visited.add(prereq)
            queue.extend(self._backward.get(prereq, []))

        return visited

    def unlocks(self, course: str, transitive: bool = True) -> set[str]:
        """
        Get courses that this course unlocks (is a prerequisite for).

        Args:
            course: Course code
            transitive: If True, include courses unlocked by unlocked courses

        Returns:
            Set of course codes that depend on this course
        """
        course = self._normalize(course)
        if not transitive:
            return self._forward.get(course, set()).copy()

        # BFS for transitive dependents
        visited = set()
        queue = list(self._forward.get(course, []))

        while queue:
            dependent = queue.pop(0)
            if dependent in visited:
                continue
            visited.add(dependent)
            queue.extend(self._forward.get(dependent, []))

        return visited

    def path_to(self, course: str) -> list[list[str]]:
        """
        Find paths from entry-level courses to the target.

        Returns list of paths, where each path is a list of courses
        in order from entry (no prerequisites) to target.
        """
        course = self._normalize(course)

        # Find all entry points (courses with no prerequisites in our graph)
        prereqs = self.prerequisites_for(course)
        if not prereqs:
            return [[course]]

        entry_points = [p for p in prereqs if not self._backward.get(p)]
        if not entry_points:
            # All prereqs have prereqs themselves - just pick the deepest
            entry_points = list(prereqs)

        # Build paths using DFS
        paths = []
        for entry in entry_points:
            self._find_paths(entry, course, [entry], paths)

        return paths

    def _find_paths(
        self,
        current: str,
        target: str,
        path: list[str],
        all_paths: list[list[str]]
    ) -> None:
        """DFS helper to find all paths to target."""
        if current == target:
            all_paths.append(path.copy())
            return

        for next_course in self._forward.get(current, []):
            if next_course in path:  # Avoid cycles
                continue
            if next_course == target or next_course in self.prerequisites_for(target):
                path.append(next_course)
                self._find_paths(next_course, target, path, all_paths)
                path.pop()

    def detect_cycles(self) -> list[list[str]]:
        """
        Detect cycles in the prerequisite graph.

        Returns list of cycles found (each cycle is a list of courses).
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(course: str, path: list[str]) -> None:
            visited.add(course)
            rec_stack.add(course)
            path.append(course)

            for prereq in self._backward.get(course, []):
                if prereq not in visited:
                    dfs(prereq, path)
                elif prereq in rec_stack:
                    # Found cycle
                    cycle_start = path.index(prereq)
                    cycles.append(path[cycle_start:] + [prereq])

            path.pop()
            rec_stack.remove(course)

        for course in self._courses:
            if course not in visited:
                dfs(course, [])

        return cycles

    def stats(self) -> dict:
        """Get graph statistics."""
        in_degrees = {c: len(self._backward.get(c, [])) for c in self._courses}
        out_degrees = {c: len(self._forward.get(c, [])) for c in self._courses}

        return {
            "total_courses": len(self._courses),
            "total_edges": sum(len(deps) for deps in self._forward.values()),
            "entry_courses": sum(1 for d in in_degrees.values() if d == 0),
            "terminal_courses": sum(1 for d in out_degrees.values() if d == 0),
            "max_prerequisites": max(in_degrees.values()) if in_degrees else 0,
            "max_dependents": max(out_degrees.values()) if out_degrees else 0,
        }


async def build_graph_for_subject(subject: str) -> PrerequisiteGraph:
    """
    Build a prerequisite graph for all courses in a subject.

    Args:
        subject: Subject code (e.g., "CMPT")

    Returns:
        PrerequisiteGraph with all prerequisite relationships
    """
    graph = PrerequisiteGraph()

    async with USaskCatalogueClient() as client:
        response = await client.get_courses_by_subject(subject)

        for course_data in response.data.get("courses", []):
            course_id = course_data.get("id", "")
            tech = course_data.get("tech", "")

            prereqs = parse_prerequisites(tech)
            course_code = f"{course_data['subject']} {course_data['course_number']}"

            # Add edges only for required prerequisites (not alternatives)
            for prereq in prereqs.required_courses:
                # Skip high school courses
                if any(hs in prereq for hs in ["Mathematics", "Computer Science", "Pre-Calculus", "Foundations"]):
                    continue
                graph.add_edge(prereq, course_code)

    return graph


def build_graph_for_subject_sync(subject: str) -> PrerequisiteGraph:
    """Synchronous wrapper for build_graph_for_subject."""
    return asyncio.run(build_graph_for_subject(subject))


def demo():
    """Demo the prerequisite graph."""
    print("Building prerequisite graph for CMPT...")
    graph = build_graph_for_subject_sync("CMPT")

    print(f"\nGraph stats: {graph.stats()}")

    print("\n=== Prerequisites for CMPT 280 ===")
    prereqs = graph.prerequisites_for("CMPT 280")
    print(f"Direct + transitive: {sorted(prereqs)}")

    print("\n=== What CMPT 141 unlocks ===")
    unlocks = graph.unlocks("CMPT 141")
    print(f"Courses depending on CMPT 141: {sorted(unlocks)}")

    print("\n=== Path to CMPT 280 ===")
    paths = graph.path_to("CMPT 280")
    for i, path in enumerate(paths[:3], 1):
        print(f"Path {i}: {' → '.join(path)}")

    print("\n=== Cycle detection ===")
    cycles = graph.detect_cycles()
    if cycles:
        print(f"Found {len(cycles)} cycles:")
        for cycle in cycles:
            print(f"  {' → '.join(cycle)}")
    else:
        print("No cycles found")


if __name__ == "__main__":
    demo()
