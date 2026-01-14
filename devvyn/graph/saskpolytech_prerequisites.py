"""
Prerequisite graph for SaskPolytech program course dependencies.

Build a directed graph from program courses and query:
- What courses are needed for X (transitive)?
- What courses does X unlock?
- What's the recommended path through a program?
"""
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field

from devvyn.api.saskpolytech import SaskPolytechClient, SaskPolytechProgram


@dataclass
class ProgramPrerequisiteGraph:
    """
    Directed graph of course prerequisites within a program.

    Edges point from prerequisite → dependent course.
    (e.g., COSC 180 → COSC 182 means "180 is a prerequisite for 182")
    """

    program_code: str
    program_name: str = ""

    # course_id → set of courses that depend on it
    _forward: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    # course_id → set of courses it depends on (prerequisites)
    _backward: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    # All known courses
    _courses: set[str] = field(default_factory=set)

    # Course metadata
    _course_info: dict[str, dict] = field(default_factory=dict)

    def add_edge(self, prereq: str, course: str) -> None:
        """Add a prerequisite relationship."""
        prereq = self._normalize(prereq)
        course = self._normalize(course)
        self._forward[prereq].add(course)
        self._backward[course].add(prereq)
        self._courses.add(prereq)
        self._courses.add(course)

    def add_course(self, code: str, title: str = "", semester: str = "") -> None:
        """Add a course to the graph (even if it has no prerequisites)."""
        code = self._normalize(code)
        self._courses.add(code)
        self._course_info[code] = {"title": title, "semester": semester}

    def _normalize(self, course: str) -> str:
        """Normalize course code format."""
        course = course.upper().strip()
        # Ensure space between subject and number
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

    def get_title(self, course: str) -> str:
        """Get course title."""
        return self._course_info.get(self._normalize(course), {}).get("title", "")

    def get_semester(self, course: str) -> str:
        """Get course semester."""
        return self._course_info.get(self._normalize(course), {}).get("semester", "")

    def prerequisites_for(self, course: str, transitive: bool = True) -> set[str]:
        """
        Get prerequisites for a course.

        Args:
            course: Course code (e.g., "COSC 182")
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

    def entry_courses(self) -> set[str]:
        """Courses with no prerequisites (starting points)."""
        return {c for c in self._courses if not self._backward.get(c)}

    def terminal_courses(self) -> set[str]:
        """Courses that don't unlock anything (endpoints)."""
        return {c for c in self._courses if not self._forward.get(c)}

    def by_semester(self) -> dict[str, list[str]]:
        """Group courses by semester."""
        semesters: dict[str, list[str]] = defaultdict(list)
        for code in self._courses:
            semester = self.get_semester(code)
            semesters[semester].append(code)
        return dict(semesters)

    def stats(self) -> dict:
        """Get graph statistics."""
        in_degrees = {c: len(self._backward.get(c, [])) for c in self._courses}
        out_degrees = {c: len(self._forward.get(c, [])) for c in self._courses}

        return {
            "program": self.program_code,
            "total_courses": len(self._courses),
            "total_edges": sum(len(deps) for deps in self._forward.values()),
            "entry_courses": sum(1 for d in in_degrees.values() if d == 0),
            "terminal_courses": sum(1 for d in out_degrees.values() if d == 0),
            "max_prerequisites": max(in_degrees.values()) if in_degrees else 0,
            "max_dependents": max(out_degrees.values()) if out_degrees else 0,
        }


async def build_graph_for_program(program_code: str) -> ProgramPrerequisiteGraph:
    """
    Build a prerequisite graph for a SaskPolytech program.

    Args:
        program_code: Program code (e.g., "CSTDP")

    Returns:
        ProgramPrerequisiteGraph with all prerequisite relationships
    """
    graph = ProgramPrerequisiteGraph(program_code=program_code)

    async with SaskPolytechClient() as client:
        program = await client.get_program_with_courses(program_code)
        graph.program_name = program.name

        for course in program.courses:
            # Add course to graph
            graph.add_course(course.code, course.title, course.semester)

            # Add prerequisite edges
            for prereq in course.prerequisites:
                graph.add_edge(prereq, course.code)

    return graph


def build_graph_for_program_sync(program_code: str) -> ProgramPrerequisiteGraph:
    """Synchronous wrapper for build_graph_for_program."""
    return asyncio.run(build_graph_for_program(program_code))


def demo():
    """Demo the prerequisite graph."""
    print("Building prerequisite graph for CST (Computer Systems Technology)...")
    graph = build_graph_for_program_sync("CSTDP")

    print(f"\n{graph.program_name}")
    print(f"Stats: {graph.stats()}")

    print("\n=== Entry courses (no prerequisites) ===")
    for code in sorted(graph.entry_courses()):
        title = graph.get_title(code)
        semester = graph.get_semester(code)
        print(f"  {code}: {title} ({semester})")

    print("\n=== What COSC 180 unlocks ===")
    unlocks = graph.unlocks("COSC 180")
    print(f"Courses depending on COSC 180: {sorted(unlocks)}")

    print("\n=== Prerequisites for PROJ 273 (Capstone 3) ===")
    prereqs = graph.prerequisites_for("PROJ 273")
    print(f"All prerequisites: {sorted(prereqs)}")

    print("\n=== Courses by semester ===")
    for semester, courses in sorted(graph.by_semester().items()):
        print(f"\n{semester}:")
        for code in sorted(courses):
            prereqs = graph.prerequisites_for(code, transitive=False)
            prereq_str = f" <- {', '.join(sorted(prereqs))}" if prereqs else ""
            print(f"  {code}: {graph.get_title(code)}{prereq_str}")


if __name__ == "__main__":
    demo()
