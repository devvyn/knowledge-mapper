"""
Extended curriculum graph supporting courses, materials, work requirements, and exams.

This graph extends the prerequisite graph to model complete course structures:
- Courses with their prerequisites (existing functionality)
- Textbooks associated with courses
- Work requirements (assignments, labs, projects) within courses
- Final exams as terminal nodes that depend on completing work

Graph Structure:
    ┌─────────────────────────────────────────────────────────────┐
    │                     COURSE LEVEL                            │
    │  Course_A ─────prerequisite────► Course_B                   │
    └─────────────────────────────────────────────────────────────┘
                           │
                           │ (course contains)
                           ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                   MATERIALS LEVEL                           │
    │                                                             │
    │  Textbook_1 ◄───uses──── Course_B ────uses───► Textbook_2   │
    │      │                       │                    │         │
    │      ▼                       ▼                    ▼         │
    │  [Chapters]            [Work Reqs]           [Chapters]     │
    └─────────────────────────────────────────────────────────────┘
                           │
                           │ (work dependencies)
                           ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                WORK REQUIREMENT LEVEL                       │
    │                                                             │
    │  Reading_Ch1 ──► Assignment_1 ──┐                           │
    │                                 │                           │
    │  Reading_Ch2 ──► Lab_1 ─────────┼──► Midterm_1              │
    │                                 │         │                 │
    │  Reading_Ch3 ──► Lab_2 ─────────┘         │                 │
    │       │                                   │                 │
    │       └───────► Project ──────────────────┼──► Final_Exam   │
    │                                           │                 │
    │                  Midterm_1 ───────────────┘                 │
    └─────────────────────────────────────────────────────────────┘
"""
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Union

from devvyn.institutions.base import CourseReference, UnifiedCourse
from devvyn.model.course_materials import (
    Textbook,
    TextbookReference,
    TextbookSection,
    WorkRequirement,
    WorkRequirementRef,
    FinalExam,
    ExamRef,
    CourseCompletion,
    GraphNode,
    GraphEdge,
    NodeType,
    EdgeType,
)
from devvyn.model.concepts import LearningConcept, ConceptSource
from devvyn.model.learning_path import LearningPath, LearningPathBuilder


# Type alias for any graph node reference
NodeRef = Union[CourseReference, TextbookReference, WorkRequirementRef, ExamRef, str]


@dataclass
class CurriculumGraph:
    """
    A comprehensive curriculum graph that models courses, materials, work, and exams.

    This extends the prerequisite graph to support fine-grained modeling of
    what's required to complete a course or program.
    """

    # All nodes by type
    _courses: dict[CourseReference, UnifiedCourse] = field(default_factory=dict)
    _textbooks: dict[TextbookReference, Textbook] = field(default_factory=dict)
    _work_requirements: dict[WorkRequirementRef, WorkRequirement] = field(default_factory=dict)
    _exams: dict[ExamRef, FinalExam] = field(default_factory=dict)
    _course_completions: dict[CourseReference, CourseCompletion] = field(default_factory=dict)

    # OER/Learning path nodes
    _concepts: dict[str, LearningConcept] = field(default_factory=dict)
    _sections: dict[str, TextbookSection] = field(default_factory=dict)
    _concept_sources: dict[str, list[ConceptSource]] = field(default_factory=lambda: defaultdict(list))

    # Forward edges: node → set of nodes that depend on it
    _forward: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    # Backward edges: node → set of nodes it depends on
    _backward: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    # Edge metadata
    _edge_types: dict[tuple[str, str], EdgeType] = field(default_factory=dict)

    # --- Node Operations ---

    def add_course(self, course: UnifiedCourse) -> None:
        """Add a course to the graph."""
        self._courses[course.ref] = course

        # Add prerequisite edges
        for prereq_ref in course.prerequisites:
            self._add_edge(str(prereq_ref), str(course.ref), EdgeType.PREREQUISITE)

        # Add corequisite edges (bidirectional)
        for coreq_ref in course.corequisites:
            self._add_edge(str(coreq_ref), str(course.ref), EdgeType.COREQUISITE)
            self._add_edge(str(course.ref), str(coreq_ref), EdgeType.COREQUISITE)

    def add_textbook(self, textbook: Textbook) -> None:
        """Add a textbook to the graph."""
        self._textbooks[textbook.ref] = textbook

    def add_work_requirement(self, work: WorkRequirement) -> None:
        """Add a work requirement to the graph."""
        self._work_requirements[work.ref] = work

        # Add edges for dependencies
        for dep_ref in work.depends_on:
            self._add_edge(str(dep_ref), str(work.ref), EdgeType.DEPENDS_ON)

        # Add edges for textbook readings
        for textbook_ref, section in work.textbook_readings:
            reading_node = f"{textbook_ref}:{section}"
            self._add_edge(reading_node, str(work.ref), EdgeType.REQUIRES_READING)

    def add_exam(self, exam: FinalExam) -> None:
        """Add an exam to the graph."""
        self._exams[exam.ref] = exam

        # Add edges from work requirements to exam
        for work_ref in exam.required_work:
            self._add_edge(str(work_ref), str(exam.ref), EdgeType.LEADS_TO_EXAM)

    def add_course_completion(self, completion: CourseCompletion) -> None:
        """
        Add complete course requirements including materials and exams.

        This is the main entry point for adding rich course data.
        """
        self._course_completions[completion.course_ref] = completion

        # Add textbooks
        for textbook in completion.required_textbooks + completion.recommended_textbooks:
            self.add_textbook(textbook)
            # Link course to textbook
            self._add_edge(
                str(completion.course_ref),
                str(textbook.ref),
                EdgeType.USES_TEXTBOOK
            )

        # Add work requirements
        for work in completion.all_work_requirements:
            self.add_work_requirement(work)

        # Add exams
        for exam in completion.all_exams:
            self.add_exam(exam)

    def _add_edge(self, source: str, target: str, edge_type: EdgeType) -> None:
        """Add a directed edge to the graph."""
        self._forward[source].add(target)
        self._backward[target].add(source)
        self._edge_types[(source, target)] = edge_type

    # --- OER/Concept Operations ---

    def add_concept(self, concept: LearningConcept) -> None:
        """Add a learning concept to the graph."""
        self._concepts[concept.id] = concept

    def add_section(self, section: TextbookSection) -> None:
        """Add a textbook section to the graph."""
        section_id = section.id
        self._sections[section_id] = section

        # Ensure the textbook exists
        if section.textbook_ref not in self._textbooks:
            # Create minimal textbook entry
            pass  # Textbook should be added separately

    def link_section_teaches_concept(
        self,
        section: TextbookSection,
        concept_id: str,
        coverage: str = "full"
    ) -> None:
        """
        Link a textbook section to a concept it teaches.

        Args:
            section: The textbook section
            concept_id: ID of the concept being taught
            coverage: "full", "partial", or "introduction"
        """
        section_id = section.id

        # Ensure both exist in graph
        if section_id not in self._sections:
            self.add_section(section)
        if concept_id not in self._concepts:
            # Concept should exist - log warning in production
            return

        # Add edge: section teaches concept
        self._add_edge(section_id, f"concept:{concept_id}", EdgeType.TEACHES_CONCEPT)

        # Track source
        source = ConceptSource(
            concept_id=concept_id,
            section=section,
            coverage=coverage
        )
        self._concept_sources[concept_id].append(source)

    def link_course_requires_concept(
        self,
        course_ref: CourseReference,
        concept_id: str
    ) -> None:
        """
        Link a course to a concept it requires as prerequisite knowledge.

        Args:
            course_ref: The course reference
            concept_id: ID of the required concept
        """
        self._add_edge(
            f"concept:{concept_id}",
            str(course_ref),
            EdgeType.REQUIRES_CONCEPT
        )

    def link_section_prerequisite(
        self,
        section: TextbookSection,
        prereq_section: TextbookSection
    ) -> None:
        """Link section to a prerequisite section (read this first)."""
        self._add_edge(
            prereq_section.id,
            section.id,
            EdgeType.SECTION_PREREQ
        )

    # --- Query Operations ---

    def get_course(self, ref: CourseReference) -> Optional[UnifiedCourse]:
        """Get a course by reference."""
        return self._courses.get(ref)

    def get_textbook(self, ref: TextbookReference) -> Optional[Textbook]:
        """Get a textbook by reference."""
        return self._textbooks.get(ref)

    def get_work_requirement(self, ref: WorkRequirementRef) -> Optional[WorkRequirement]:
        """Get a work requirement by reference."""
        return self._work_requirements.get(ref)

    def get_exam(self, ref: ExamRef) -> Optional[FinalExam]:
        """Get an exam by reference."""
        return self._exams.get(ref)

    def get_course_completion(self, ref: CourseReference) -> Optional[CourseCompletion]:
        """Get full course completion requirements."""
        return self._course_completions.get(ref)

    def dependencies_for(self, node_id: str, transitive: bool = True) -> set[str]:
        """
        Get all nodes that this node depends on.

        Args:
            node_id: Node identifier
            transitive: If True, include transitive dependencies

        Returns:
            Set of node IDs this node depends on
        """
        if not transitive:
            return self._backward.get(node_id, set()).copy()

        # BFS for transitive dependencies
        visited = set()
        queue = list(self._backward.get(node_id, []))

        while queue:
            dep = queue.pop(0)
            if dep in visited:
                continue
            visited.add(dep)
            queue.extend(self._backward.get(dep, []))

        return visited

    def dependents_of(self, node_id: str, transitive: bool = True) -> set[str]:
        """
        Get all nodes that depend on this node.

        Args:
            node_id: Node identifier
            transitive: If True, include transitive dependents

        Returns:
            Set of node IDs that depend on this node
        """
        if not transitive:
            return self._forward.get(node_id, set()).copy()

        # BFS for transitive dependents
        visited = set()
        queue = list(self._forward.get(node_id, []))

        while queue:
            dep = queue.pop(0)
            if dep in visited:
                continue
            visited.add(dep)
            queue.extend(self._forward.get(dep, []))

        return visited

    def path_to_exam(self, exam_ref: ExamRef) -> list[list[str]]:
        """
        Find all paths from entry-level work to a final exam.

        Useful for visualizing what needs to be done to prepare for an exam.
        """
        exam_id = str(exam_ref)
        paths = []

        # Find entry points (nodes with no dependencies in this course)
        course_ref = exam_ref.course_ref
        entry_points = []

        for work_ref in self._work_requirements:
            if work_ref.course_ref == course_ref:
                work_id = str(work_ref)
                # Entry point if no dependencies or only textbook dependencies
                deps = self._backward.get(work_id, set())
                if not deps or all("isbn:" in d for d in deps):
                    entry_points.append(work_id)

        # DFS from each entry point to exam
        for entry in entry_points:
            self._find_paths_dfs(entry, exam_id, [entry], paths, max_depth=20)

        return paths

    def _find_paths_dfs(
        self,
        current: str,
        target: str,
        path: list[str],
        all_paths: list[list[str]],
        max_depth: int
    ) -> None:
        """DFS helper for finding paths."""
        if len(path) > max_depth:
            return

        if current == target:
            all_paths.append(path.copy())
            return

        for next_node in self._forward.get(current, []):
            if next_node not in path:
                path.append(next_node)
                self._find_paths_dfs(next_node, target, path, all_paths, max_depth)
                path.pop()

    def get_final_exams(self, institution: Optional[str] = None) -> list[FinalExam]:
        """Get all final exams, optionally filtered by institution."""
        exams = list(self._exams.values())
        if institution:
            exams = [e for e in exams if e.course_ref.institution == institution]
        return exams

    def get_work_for_course(self, course_ref: CourseReference) -> list[WorkRequirement]:
        """Get all work requirements for a course."""
        return [
            w for w in self._work_requirements.values()
            if w.course_ref == course_ref
        ]

    def get_textbooks_for_course(self, course_ref: CourseReference) -> list[Textbook]:
        """Get all textbooks used by a course."""
        course_id = str(course_ref)
        textbooks = []
        for target in self._forward.get(course_id, []):
            if target.startswith("isbn:"):
                # Parse textbook ref
                try:
                    ref = TextbookReference.parse(target)
                    if ref in self._textbooks:
                        textbooks.append(self._textbooks[ref])
                except ValueError:
                    pass
        return textbooks

    # --- Concept Query Operations ---

    def get_concept(self, concept_id: str) -> Optional[LearningConcept]:
        """Get a concept by ID."""
        return self._concepts.get(concept_id)

    def get_section(self, section_id: str) -> Optional[TextbookSection]:
        """Get a textbook section by ID."""
        return self._sections.get(section_id)

    def all_concepts(self) -> list[LearningConcept]:
        """Get all learning concepts in the graph."""
        return list(self._concepts.values())

    def all_sections(self) -> list[TextbookSection]:
        """Get all textbook sections in the graph."""
        return list(self._sections.values())

    def sections_for_concept(self, concept_id: str) -> list[TextbookSection]:
        """
        Get all textbook sections that teach a concept.

        Args:
            concept_id: The concept to find teaching sources for

        Returns:
            List of TextbookSections that teach this concept
        """
        sources = self._concept_sources.get(concept_id, [])
        return [source.section for source in sources]

    def textbooks_teaching(self, concept_id: str) -> list[Textbook]:
        """
        Get all textbooks that contain sections teaching a concept.

        Args:
            concept_id: The concept to find textbooks for

        Returns:
            List of Textbooks with chapters covering this concept
        """
        sections = self.sections_for_concept(concept_id)
        textbook_refs = {s.textbook_ref for s in sections}
        return [
            self._textbooks[ref]
            for ref in textbook_refs
            if ref in self._textbooks
        ]

    def concepts_taught_by_section(self, section_id: str) -> list[LearningConcept]:
        """Get concepts taught by a specific section."""
        concept_ids = []
        for target in self._forward.get(section_id, []):
            if target.startswith("concept:"):
                concept_id = target.replace("concept:", "")
                concept_ids.append(concept_id)
        return [
            self._concepts[cid]
            for cid in concept_ids
            if cid in self._concepts
        ]

    def paths_to_concept(self, concept_id: str) -> list[LearningPath]:
        """
        Find learning paths to a concept through open textbooks.

        Generates paths from entry-level sections to sections that teach
        the target concept, following section prerequisites.

        Args:
            concept_id: Target concept to learn

        Returns:
            List of possible LearningPaths, ordered by estimated time
        """
        # Get sections that teach this concept
        teaching_sections = self.sections_for_concept(concept_id)
        if not teaching_sections:
            return []

        paths = []

        for target_section in teaching_sections:
            # Build path backwards from target section
            path_sections = self._build_section_path(target_section)

            if path_sections:
                builder = LearningPathBuilder(concept_id)
                for section in path_sections:
                    builder.add_section(section)

                path = builder.build()
                paths.append(path)

        # Sort by estimated hours (shortest first)
        return sorted(paths, key=lambda p: p.estimated_hours)

    def _build_section_path(self, target: TextbookSection) -> list[TextbookSection]:
        """
        Build ordered path of sections leading to a target section.

        Follows section prerequisites backwards, then reverses for learning order.
        """
        path = []
        visited = set()
        queue = [target]

        while queue:
            current = queue.pop(0)
            if current.id in visited:
                continue
            visited.add(current.id)
            path.append(current)

            # Find prerequisite sections
            for prereq_id in self._backward.get(current.id, []):
                if prereq_id in self._sections:
                    prereq = self._sections[prereq_id]
                    queue.append(prereq)

        # Reverse to get learning order (prerequisites first)
        path.reverse()
        return path

    def find_concepts_matching(self, query: str) -> list[LearningConcept]:
        """
        Search for concepts matching a query string.

        Matches against concept name, ID, aliases, and topics.
        """
        return [c for c in self._concepts.values() if c.matches(query)]

    # --- Export for Visualization ---

    def to_graph_data(self) -> dict:
        """
        Export graph in format compatible with visualization.

        Returns dict with 'nodes' and 'links' arrays.
        """
        nodes = []
        links = []

        # Add course nodes
        for ref, course in self._courses.items():
            nodes.append({
                "id": str(ref),
                "label": ref.code,
                "title": course.title,
                "institution": ref.institution,
                "type": NodeType.COURSE.value,
                "credits": course.credits,
            })

        # Add textbook nodes
        for ref, textbook in self._textbooks.items():
            nodes.append({
                "id": str(ref),
                "label": textbook.title[:30],
                "title": str(textbook),
                "type": NodeType.TEXTBOOK.value,
                "authors": textbook.authors,
                "isbn": textbook.isbn,
            })

        # Add work requirement nodes
        for ref, work in self._work_requirements.items():
            nodes.append({
                "id": str(ref),
                "label": work.title,
                "title": work.description,
                "institution": ref.course_ref.institution,
                "type": NodeType.WORK_REQUIREMENT.value,
                "work_type": ref.req_type.value,
                "weight": work.weight_percent,
                "course": str(ref.course_ref),
            })

        # Add exam nodes
        for ref, exam in self._exams.items():
            nodes.append({
                "id": str(ref),
                "label": exam.title,
                "title": exam.description,
                "institution": ref.course_ref.institution,
                "type": NodeType.EXAM.value,
                "weight": exam.weight_percent,
                "duration_minutes": exam.duration_minutes,
                "course": str(ref.course_ref),
            })

        # Add concept nodes
        for concept_id, concept in self._concepts.items():
            nodes.append({
                "id": f"concept:{concept_id}",
                "label": concept.name,
                "title": concept.description,
                "type": NodeType.CONCEPT.value,
                "subject": concept.subject,
                "level": concept.level,
                "aliases": concept.aliases,
            })

        # Add section nodes
        for section_id, section in self._sections.items():
            nodes.append({
                "id": section_id,
                "label": f"Ch.{section.chapter}: {section.title[:20]}",
                "title": section.title,
                "type": NodeType.SECTION.value,
                "chapter": section.chapter,
                "textbook": str(section.textbook_ref),
                "topics": section.topics,
                "estimated_minutes": section.estimated_minutes,
            })

        # Add all edges
        for source, targets in self._forward.items():
            for target in targets:
                edge_type = self._edge_types.get((source, target), EdgeType.DEPENDS_ON)
                links.append({
                    "source": source,
                    "target": target,
                    "type": edge_type.value,
                })

        return {"nodes": nodes, "links": links}

    def stats(self) -> dict:
        """Get graph statistics."""
        return {
            "total_courses": len(self._courses),
            "total_textbooks": len(self._textbooks),
            "total_work_requirements": len(self._work_requirements),
            "total_exams": len(self._exams),
            "total_concepts": len(self._concepts),
            "total_sections": len(self._sections),
            "total_edges": sum(len(targets) for targets in self._forward.values()),
            "edge_types": {
                et.value: sum(1 for e in self._edge_types.values() if e == et)
                for et in EdgeType
            },
        }


def build_curriculum_from_courses(
    courses: list[UnifiedCourse],
    completions: Optional[list[CourseCompletion]] = None
) -> CurriculumGraph:
    """
    Build a curriculum graph from courses and optional completion data.

    Args:
        courses: List of courses to add
        completions: Optional list of course completion data

    Returns:
        CurriculumGraph with all data added
    """
    graph = CurriculumGraph()

    for course in courses:
        graph.add_course(course)

    if completions:
        for completion in completions:
            graph.add_course_completion(completion)

    return graph
