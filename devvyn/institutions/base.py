"""
Base interfaces for multi-institution support.

Defines the common abstractions that all institution adapters must implement.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol, runtime_checkable


class CredentialType(Enum):
    """Types of academic credentials."""
    CERTIFICATE = "certificate"
    DIPLOMA = "diploma"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    DOCTORATE = "doctorate"
    POST_GRAD_CERTIFICATE = "post_grad_certificate"
    POST_GRAD_DIPLOMA = "post_grad_diploma"
    OTHER = "other"

    @classmethod
    def from_string(cls, s: str) -> "CredentialType":
        """Parse credential type from string."""
        s = s.lower().strip()
        if "certificate" in s and "post" in s:
            return cls.POST_GRAD_CERTIFICATE
        if "diploma" in s and "post" in s:
            return cls.POST_GRAD_DIPLOMA
        if "certificate" in s:
            return cls.CERTIFICATE
        if "diploma" in s:
            return cls.DIPLOMA
        if "bachelor" in s:
            return cls.BACHELORS
        if "master" in s:
            return cls.MASTERS
        if "doctor" in s or "phd" in s:
            return cls.DOCTORATE
        return cls.OTHER


@dataclass(frozen=True)
class CourseReference:
    """
    Unique reference to a course across institutions.

    This is the canonical way to identify a course in cross-institution queries.
    """
    institution: str  # e.g., "usask", "saskpolytech"
    code: str         # e.g., "CMPT 141", "COSC 180"

    def __str__(self) -> str:
        return f"{self.institution}:{self.code}"

    @classmethod
    def parse(cls, s: str) -> "CourseReference":
        """Parse from 'institution:code' format."""
        if ":" not in s:
            raise ValueError(f"Invalid course reference: {s}")
        inst, code = s.split(":", 1)
        return cls(institution=inst.strip().lower(), code=code.strip().upper())


@dataclass
class UnifiedCourse:
    """
    Normalized course representation across institutions.

    All institution adapters convert their native course format to this.
    """
    # Identity
    ref: CourseReference
    title: str

    # Details
    description: str = ""
    credits: float = 0.0
    lecture_hours: float = 0.0
    lab_hours: float = 0.0

    # Prerequisites (as CourseReferences)
    prerequisites: list[CourseReference] = field(default_factory=list)
    corequisites: list[CourseReference] = field(default_factory=list)

    # Alternatives (any one satisfies prerequisite)
    # e.g., [[ref1, ref2], [ref3, ref4]] means "(ref1 OR ref2) AND (ref3 OR ref4)"
    prerequisite_alternatives: list[list[CourseReference]] = field(default_factory=list)

    # Textbooks (ISBNs of required/recommended books)
    textbook_isbns: list[str] = field(default_factory=list)

    # Course completion structure
    has_final_exam: bool = True
    has_midterm: bool = False
    has_labs: bool = False
    has_assignments: bool = True
    has_project: bool = False

    # Grading weights (if known)
    final_exam_weight: float = 0.0      # Percentage (e.g., 40.0 for 40%)
    midterm_weight: float = 0.0
    assignments_weight: float = 0.0
    labs_weight: float = 0.0
    project_weight: float = 0.0
    participation_weight: float = 0.0

    # Metadata
    url: str = ""
    fetched_at: Optional[datetime] = None

    @property
    def institution(self) -> str:
        return self.ref.institution

    @property
    def code(self) -> str:
        return self.ref.code

    def __str__(self) -> str:
        return f"{self.ref}: {self.title}"


@dataclass
class UnifiedProgram:
    """
    Normalized program representation across institutions.
    """
    # Identity
    institution: str
    code: str
    name: str

    # Details
    credential: CredentialType = CredentialType.OTHER
    description: str = ""
    duration_weeks: int = 0

    # Courses in the program
    courses: list[UnifiedCourse] = field(default_factory=list)

    # Metadata
    url: str = ""
    fetched_at: Optional[datetime] = None

    @property
    def course_refs(self) -> list[CourseReference]:
        """All course references in this program."""
        return [c.ref for c in self.courses]


@runtime_checkable
class Institution(Protocol):
    """
    Protocol for institution adapters.

    All institution adapters must implement this interface.
    """

    @property
    def id(self) -> str:
        """Unique identifier for this institution (e.g., 'usask')."""
        ...

    @property
    def name(self) -> str:
        """Human-readable name (e.g., 'University of Saskatchewan')."""
        ...

    @property
    def short_name(self) -> str:
        """Short name (e.g., 'USask')."""
        ...

    @property
    def location(self) -> str:
        """Primary location (e.g., 'Saskatoon, SK')."""
        ...

    async def get_course(self, code: str) -> Optional[UnifiedCourse]:
        """Get a specific course by code."""
        ...

    async def get_courses_by_subject(self, subject: str) -> list[UnifiedCourse]:
        """Get all courses in a subject area."""
        ...

    async def get_program(self, code: str) -> Optional[UnifiedProgram]:
        """Get a specific program by code."""
        ...

    async def get_programs(self) -> list[UnifiedProgram]:
        """Get all programs."""
        ...

    async def search_courses(self, query: str) -> list[UnifiedCourse]:
        """Search courses by keyword."""
        ...


class InstitutionAdapter(ABC):
    """
    Abstract base class for institution adapters.

    Provides common functionality and enforces the Institution protocol.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for this institution."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass

    @property
    @abstractmethod
    def short_name(self) -> str:
        """Short name."""
        pass

    @property
    @abstractmethod
    def location(self) -> str:
        """Primary location."""
        pass

    def make_ref(self, code: str) -> CourseReference:
        """Create a CourseReference for this institution."""
        return CourseReference(institution=self.id, code=code.upper())

    @abstractmethod
    async def get_course(self, code: str) -> Optional[UnifiedCourse]:
        """Get a specific course by code."""
        pass

    @abstractmethod
    async def get_courses_by_subject(self, subject: str) -> list[UnifiedCourse]:
        """Get all courses in a subject area."""
        pass

    @abstractmethod
    async def get_program(self, code: str) -> Optional[UnifiedProgram]:
        """Get a specific program by code."""
        pass

    @abstractmethod
    async def get_programs(self) -> list[UnifiedProgram]:
        """Get all programs."""
        pass

    async def search_courses(self, query: str) -> list[UnifiedCourse]:
        """
        Search courses by keyword.

        Default implementation returns empty list. Override for search support.
        """
        return []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.id}')"
