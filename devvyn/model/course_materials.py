"""
Data models for course materials, work requirements, and examinations.

Extends the knowledge graph to include:
- Textbooks and learning resources
- Work requirements (assignments, labs, projects, readings)
- Final exams as culmination nodes in the directed graph

These form a directed graph where:
  Course → Textbooks (readings)
  Course → WorkRequirements (assignments, labs, projects)
  WorkRequirements → FinalExam (exam depends on completing work)
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from devvyn.institutions.base import CourseReference


class WorkRequirementType(Enum):
    """Types of work requirements for course completion."""
    ASSIGNMENT = "assignment"           # Written or coding assignments
    LAB = "lab"                         # Laboratory exercises
    PROJECT = "project"                 # Larger project work
    READING = "reading"                 # Required reading from textbook
    QUIZ = "quiz"                       # In-class or online quizzes
    PARTICIPATION = "participation"     # Class participation
    PRESENTATION = "presentation"       # Oral presentations
    TUTORIAL = "tutorial"               # Tutorial attendance/work
    MIDTERM = "midterm"                 # Midterm examination
    FINAL_EXAM = "final_exam"           # Final examination


class MaterialType(Enum):
    """Types of learning materials."""
    TEXTBOOK = "textbook"
    REFERENCE_BOOK = "reference_book"
    ONLINE_RESOURCE = "online_resource"
    LECTURE_NOTES = "lecture_notes"
    VIDEO_SERIES = "video_series"
    SOFTWARE_TOOL = "software_tool"


@dataclass(frozen=True)
class TextbookReference:
    """
    Unique reference to a textbook.

    Uses ISBN-13 as primary identifier when available.
    """
    isbn: str                    # ISBN-13 (or ISBN-10)
    institution: str = ""        # Optional: institution-specific ID

    def __str__(self) -> str:
        if self.institution:
            return f"{self.institution}:isbn:{self.isbn}"
        return f"isbn:{self.isbn}"

    @classmethod
    def parse(cls, s: str) -> "TextbookReference":
        """Parse from 'isbn:...' or 'institution:isbn:...' format."""
        parts = s.split(":")
        if len(parts) == 2 and parts[0] == "isbn":
            return cls(isbn=parts[1])
        if len(parts) == 3 and parts[1] == "isbn":
            return cls(institution=parts[0], isbn=parts[2])
        raise ValueError(f"Invalid textbook reference: {s}")


@dataclass
class Textbook:
    """
    A textbook or learning resource used in courses.

    Can be shared across multiple courses and institutions.
    """
    ref: TextbookReference
    title: str
    authors: list[str] = field(default_factory=list)
    edition: str = ""
    publisher: str = ""
    year: int = 0
    material_type: MaterialType = MaterialType.TEXTBOOK

    # Content organization
    chapters: list[str] = field(default_factory=list)  # Chapter titles
    total_pages: int = 0

    # Metadata
    url: str = ""                       # Publisher or bookstore URL
    cover_image_url: str = ""

    @property
    def isbn(self) -> str:
        return self.ref.isbn

    def __str__(self) -> str:
        author_str = ", ".join(self.authors[:2])
        if len(self.authors) > 2:
            author_str += " et al."
        return f"{author_str} - {self.title}"


@dataclass(frozen=True)
class WorkRequirementRef:
    """
    Unique reference to a work requirement within a course.

    Format: institution:course_code:type:identifier
    Example: usask:CMPT141:assignment:a1
    """
    course_ref: CourseReference
    req_type: WorkRequirementType
    identifier: str              # e.g., "a1", "lab03", "project"

    def __str__(self) -> str:
        return f"{self.course_ref}:{self.req_type.value}:{self.identifier}"

    @classmethod
    def parse(cls, s: str) -> "WorkRequirementRef":
        """Parse from 'institution:course:type:id' format."""
        parts = s.split(":")
        if len(parts) != 4:
            raise ValueError(f"Invalid work requirement reference: {s}")
        course_ref = CourseReference(institution=parts[0], code=parts[1])
        req_type = WorkRequirementType(parts[2])
        return cls(course_ref=course_ref, req_type=req_type, identifier=parts[3])


@dataclass
class WorkRequirement:
    """
    A work requirement for course completion.

    Represents assignments, labs, projects, readings, etc. that students
    must complete as part of a course.
    """
    ref: WorkRequirementRef
    title: str
    description: str = ""

    # Weight and effort
    weight_percent: float = 0.0         # Percentage of final grade
    estimated_hours: float = 0.0        # Estimated time to complete

    # Dependencies within the course (e.g., lab2 requires lab1)
    depends_on: list[WorkRequirementRef] = field(default_factory=list)

    # Associated readings from textbook(s)
    textbook_readings: list[tuple[TextbookReference, str]] = field(default_factory=list)
    # Each tuple is (textbook_ref, chapter/section specifier)
    # e.g., (isbn_ref, "Chapter 3"), (isbn_ref, "Sections 4.1-4.3")

    # Scheduling
    due_week: Optional[int] = None      # Week of term when due
    is_group_work: bool = False

    @property
    def course_ref(self) -> CourseReference:
        return self.ref.course_ref

    @property
    def req_type(self) -> WorkRequirementType:
        return self.ref.req_type

    def __str__(self) -> str:
        return f"{self.ref.req_type.value}: {self.title}"


@dataclass(frozen=True)
class ExamRef:
    """
    Unique reference to an exam.

    Format: institution:course_code:exam_type
    Example: usask:CMPT141:final_exam
    """
    course_ref: CourseReference
    exam_type: str = "final"     # "final", "midterm1", "midterm2"

    def __str__(self) -> str:
        return f"{self.course_ref}:exam:{self.exam_type}"

    @classmethod
    def parse(cls, s: str) -> "ExamRef":
        """Parse from 'institution:course:exam:type' format."""
        parts = s.split(":")
        if len(parts) != 4 or parts[2] != "exam":
            raise ValueError(f"Invalid exam reference: {s}")
        course_ref = CourseReference(institution=parts[0], code=parts[1])
        return cls(course_ref=course_ref, exam_type=parts[3])


@dataclass
class FinalExam:
    """
    A final examination for a course.

    In the directed graph model, the final exam is a terminus node that:
    - Depends on all work requirements being completed
    - Depends on textbook readings being done
    - Represents the culmination of course learning

    Graph relationships:
        WorkRequirement_1 ──┐
        WorkRequirement_2 ──┼──► FinalExam
        TextbookReading_N ──┘
    """
    ref: ExamRef
    title: str = "Final Examination"
    description: str = ""

    # Exam characteristics
    weight_percent: float = 0.0         # Percentage of final grade (often 30-50%)
    duration_minutes: int = 180         # Exam length
    is_cumulative: bool = True          # Covers all course material

    # Exam format
    has_multiple_choice: bool = False
    has_short_answer: bool = False
    has_long_answer: bool = False
    has_coding_problems: bool = False
    has_proofs: bool = False

    # Prerequisites for writing the exam (graph edges)
    # These are the work requirements that must be done before the exam
    required_work: list[WorkRequirementRef] = field(default_factory=list)

    # Topics covered (maps to textbook sections)
    topics: list[str] = field(default_factory=list)
    textbook_coverage: list[tuple[TextbookReference, str]] = field(default_factory=list)

    # Scheduling
    exam_period: str = ""               # e.g., "December 2025", "April 2026"

    # Minimum requirements
    min_grade_percent: float = 0.0      # Minimum grade needed on exam to pass course

    @property
    def course_ref(self) -> CourseReference:
        return self.ref.course_ref

    def __str__(self) -> str:
        return f"{self.course_ref}: {self.title}"


@dataclass
class CourseCompletion:
    """
    Aggregates all completion requirements for a course.

    This model ties together:
    - The course itself
    - Required textbooks and materials
    - All work requirements (assignments, labs, projects)
    - The final exam as the terminal node

    The directed graph structure:

        ┌── Textbook ──────────────────────────┐
        │       │                              │
        │       ▼                              ▼
        │   Reading 1 ──► Assignment 1 ──┐
        │                                │
    Course   Reading 2 ──► Lab 1 ────────┼──► FinalExam
        │                                │
        │   Reading 3 ──► Project ───────┘
        │       │
        └───────┴──────────────────────────────┘
    """
    course_ref: CourseReference
    course_title: str = ""

    # Materials
    required_textbooks: list[Textbook] = field(default_factory=list)
    recommended_textbooks: list[Textbook] = field(default_factory=list)

    # Work requirements
    assignments: list[WorkRequirement] = field(default_factory=list)
    labs: list[WorkRequirement] = field(default_factory=list)
    projects: list[WorkRequirement] = field(default_factory=list)
    readings: list[WorkRequirement] = field(default_factory=list)
    quizzes: list[WorkRequirement] = field(default_factory=list)
    other_work: list[WorkRequirement] = field(default_factory=list)

    # Midterm exams (not final)
    midterms: list[FinalExam] = field(default_factory=list)

    # Terminal node
    final_exam: Optional[FinalExam] = None

    # Calculated totals
    total_work_weight: float = 0.0      # Sum of all work requirement weights
    exam_weight: float = 0.0            # Sum of all exam weights

    @property
    def all_work_requirements(self) -> list[WorkRequirement]:
        """Get all work requirements in order."""
        return (
            self.readings +
            self.assignments +
            self.labs +
            self.quizzes +
            self.projects +
            self.other_work
        )

    @property
    def all_exams(self) -> list[FinalExam]:
        """Get all exams including midterms and final."""
        exams = list(self.midterms)
        if self.final_exam:
            exams.append(self.final_exam)
        return exams

    def __post_init__(self):
        """Calculate weight totals."""
        self.total_work_weight = sum(w.weight_percent for w in self.all_work_requirements)
        self.exam_weight = sum(e.weight_percent for e in self.all_exams)

    def build_dependency_graph(self) -> dict[str, list[str]]:
        """
        Build a dependency graph of work requirements leading to the final exam.

        Returns dict mapping node IDs to their dependencies.
        """
        graph: dict[str, list[str]] = {}

        # Add work requirements
        for work in self.all_work_requirements:
            node_id = str(work.ref)
            deps = [str(d) for d in work.depends_on]
            # Also add implicit dependency on readings
            for textbook_ref, section in work.textbook_readings:
                reading_id = f"{textbook_ref}:{section}"
                if reading_id not in deps:
                    deps.append(reading_id)
            graph[node_id] = deps

        # Add final exam as terminal node
        if self.final_exam:
            exam_id = str(self.final_exam.ref)
            # Final exam depends on all required work
            deps = [str(w) for w in self.final_exam.required_work]
            # If no explicit dependencies, depend on all work
            if not deps:
                deps = [str(w.ref) for w in self.all_work_requirements]
            graph[exam_id] = deps

        return graph

    def validate_weights(self) -> list[str]:
        """Validate that weights sum to approximately 100%."""
        total = self.total_work_weight + self.exam_weight
        issues = []
        if total < 99.0:
            issues.append(f"Total weight is only {total:.1f}% (missing {100-total:.1f}%)")
        elif total > 101.0:
            issues.append(f"Total weight exceeds 100% ({total:.1f}%)")
        return issues


# --- Graph Node Types ---

class NodeType(Enum):
    """Types of nodes in the knowledge graph."""
    COURSE = "course"
    TEXTBOOK = "textbook"
    WORK_REQUIREMENT = "work_requirement"
    EXAM = "exam"
    PROGRAM = "program"


@dataclass
class GraphNode:
    """
    A node in the extended knowledge graph.

    Allows representing courses, textbooks, work requirements, and exams
    in a unified graph structure.
    """
    id: str                      # Unique identifier (e.g., "usask:CMPT141:exam:final")
    node_type: NodeType
    label: str                   # Display label
    title: str = ""              # Full title
    institution: str = ""        # Associated institution

    # Type-specific data
    course_ref: Optional[CourseReference] = None
    textbook_ref: Optional[TextbookReference] = None
    work_ref: Optional[WorkRequirementRef] = None
    exam_ref: Optional[ExamRef] = None

    # For visualization
    weight: float = 1.0          # Node importance/size
    group: str = ""              # Grouping for layout

    @classmethod
    def from_course(cls, course_ref: CourseReference, title: str = "") -> "GraphNode":
        return cls(
            id=str(course_ref),
            node_type=NodeType.COURSE,
            label=course_ref.code,
            title=title,
            institution=course_ref.institution,
            course_ref=course_ref,
            group="course"
        )

    @classmethod
    def from_textbook(cls, textbook: Textbook) -> "GraphNode":
        return cls(
            id=str(textbook.ref),
            node_type=NodeType.TEXTBOOK,
            label=textbook.title[:30] + "..." if len(textbook.title) > 30 else textbook.title,
            title=str(textbook),
            textbook_ref=textbook.ref,
            group="textbook"
        )

    @classmethod
    def from_work_requirement(cls, work: WorkRequirement) -> "GraphNode":
        return cls(
            id=str(work.ref),
            node_type=NodeType.WORK_REQUIREMENT,
            label=work.title,
            title=work.description,
            institution=work.course_ref.institution,
            work_ref=work.ref,
            weight=work.weight_percent / 10,  # Scale for visualization
            group=work.req_type.value
        )

    @classmethod
    def from_exam(cls, exam: FinalExam) -> "GraphNode":
        return cls(
            id=str(exam.ref),
            node_type=NodeType.EXAM,
            label=exam.title,
            title=exam.description,
            institution=exam.course_ref.institution,
            exam_ref=exam.ref,
            weight=exam.weight_percent / 10,
            group="exam"
        )


class EdgeType(Enum):
    """Types of edges in the knowledge graph."""
    PREREQUISITE = "prerequisite"         # Course → Course
    COREQUISITE = "corequisite"           # Course ↔ Course
    USES_TEXTBOOK = "uses_textbook"       # Course → Textbook
    REQUIRES_READING = "requires_reading" # WorkReq → Textbook section
    DEPENDS_ON = "depends_on"             # WorkReq → WorkReq
    LEADS_TO_EXAM = "leads_to_exam"       # WorkReq → Exam
    TRANSFER = "transfer"                 # Course → Course (cross-institution)


@dataclass
class GraphEdge:
    """
    An edge in the extended knowledge graph.
    """
    source: str                  # Source node ID
    target: str                  # Target node ID
    edge_type: EdgeType
    label: str = ""              # Optional label
    weight: float = 1.0          # Edge weight for visualization

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.edge_type.value,
            "label": self.label,
            "weight": self.weight
        }
