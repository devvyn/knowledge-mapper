"""
Data models for degree requirements.

Supports the complex requirement structures used by USask and other institutions:
- Required courses (must take specific course)
- Course pools (pick N from list)
- Level requirements (N credits at 300+ level)
- Subject requirements (N credits from CMPT/MATH/etc.)
- Nested requirements (AND/OR logic)
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CredentialType(Enum):
    """Type of credential awarded."""
    CERTIFICATE = "certificate"
    DIPLOMA = "diploma"
    MINOR = "minor"
    BACHELOR_3YR = "bachelor_3yr"
    BACHELOR_4YR = "bachelor_4yr"
    HONOURS = "honours"
    DOUBLE_HONOURS = "double_honours"
    MASTERS = "masters"
    PHD = "phd"


class RequirementType(Enum):
    """Type of requirement."""
    SPECIFIC_COURSE = "specific_course"      # Must take this exact course
    COURSE_POOL = "course_pool"              # Pick N from list
    SUBJECT_CREDITS = "subject_credits"      # N credits from subject(s)
    LEVEL_CREDITS = "level_credits"          # N credits at level X+
    ANY_CREDITS = "any_credits"              # Any approved credits
    NESTED = "nested"                        # Compound requirement (AND/OR)


@dataclass
class CourseRequirement:
    """
    A single course that may be required.

    Supports alternatives: "CMPT 116 or CMPT 141" becomes two CourseRequirements
    in a CoursePool with pick=1.
    """
    code: str                    # e.g., "CMPT 141"
    credits: float = 3.0         # Credit units
    notes: str = ""              # e.g., "recommended", "with lab"

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if isinstance(other, CourseRequirement):
            return self.code == other.code
        return False


@dataclass
class CoursePool:
    """
    A pool of courses from which students pick N.

    Examples:
    - "CMPT 116.3 or CMPT 141.3" -> pool with 2 courses, pick=1
    - "18 credits from CMPT 317, 332, 340..." -> pool with many courses, pick=6 (assuming 3cu each)
    """
    name: str                           # Descriptive name
    courses: list[CourseRequirement]    # Available courses
    pick_credits: float                 # Total credits to pick
    min_level: Optional[int] = None     # e.g., 300 for "300-level or higher"
    notes: str = ""

    @property
    def pick_count(self) -> int:
        """Approximate number of courses to pick (assuming 3cu each)."""
        return int(self.pick_credits / 3)


@dataclass
class SubjectRequirement:
    """Credits required from specific subject(s)."""
    subjects: list[str]          # e.g., ["CMPT", "CME"]
    credits: float               # Total credits needed
    min_level: Optional[int] = None
    max_per_subject: Optional[float] = None  # e.g., "max 6cu from one area"
    notes: str = ""


@dataclass
class RequirementBlock:
    """
    A block of requirements (e.g., C1 College, C4 Major).

    USask uses C1-C5 blocks:
    - C1: College (English, Indigenous, Quantitative)
    - C2: Breadth (Fine Arts, Humanities, Social Sciences)
    - C3: Cognate (related subjects)
    - C4: Major (program-specific)
    - C5: Electives
    """
    code: str                              # e.g., "C4"
    name: str                              # e.g., "Major Requirement"
    total_credits: float                   # Credits for this block

    # Different requirement types within the block
    required_courses: list[CourseRequirement] = field(default_factory=list)
    course_pools: list[CoursePool] = field(default_factory=list)
    subject_requirements: list[SubjectRequirement] = field(default_factory=list)

    notes: str = ""

    def all_possible_courses(self) -> set[str]:
        """Get all courses that could satisfy this block."""
        courses = {c.code for c in self.required_courses}
        for pool in self.course_pools:
            courses.update(c.code for c in pool.courses)
        return courses


@dataclass
class DegreeProgram:
    """
    A complete degree program with all requirements.

    Supports queries like:
    - What courses are required?
    - What courses can I choose from?
    - Given completed courses, what's my progress?
    - What other degrees share requirements with this one?
    """
    id: str                              # Unique identifier, e.g., "usask:bsc-4yr-cmpt"
    institution: str                     # e.g., "usask"
    name: str                            # e.g., "Bachelor of Science Four-year - Computer Science"
    credential: CredentialType
    total_credits: float                 # e.g., 120.0
    senior_credits: float = 0.0          # Credits at 200+ level required

    requirements: list[RequirementBlock] = field(default_factory=list)

    # Constraints
    residency_credits: float = 0.0       # Min credits from this institution
    min_gpa: float = 0.0                 # Minimum GPA to graduate

    url: str = ""                        # Source URL
    notes: str = ""

    def all_required_courses(self) -> set[str]:
        """Get courses that are absolutely required (no alternatives)."""
        required = set()
        for block in self.requirements:
            required.update(c.code for c in block.required_courses)
        return required

    def all_possible_courses(self) -> set[str]:
        """Get all courses that could count toward this degree."""
        courses = set()
        for block in self.requirements:
            courses.update(block.all_possible_courses())
        return courses

    def get_block(self, code: str) -> Optional[RequirementBlock]:
        """Get a requirement block by code (e.g., 'C4')."""
        for block in self.requirements:
            if block.code == code:
                return block
        return None

    def major_courses(self) -> set[str]:
        """Get courses specific to the major (C4/M4/J4)."""
        for block in self.requirements:
            if block.code in ("C4", "M4", "J4"):
                return block.all_possible_courses()
        return set()


@dataclass
class DegreeProgress:
    """
    Track progress toward a degree given completed courses.
    """
    program: DegreeProgram
    completed_courses: set[str]

    # Calculated fields
    credits_earned: float = 0.0
    credits_remaining: float = 0.0
    satisfied_requirements: list[str] = field(default_factory=list)
    remaining_requirements: list[str] = field(default_factory=list)
    completion_percentage: float = 0.0

    def __post_init__(self):
        # TODO: Calculate actual progress
        pass
