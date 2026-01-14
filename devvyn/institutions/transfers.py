"""
Transfer credit equivalencies between Saskatchewan institutions.

Based on official articulation agreements and transfer guides.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional

from devvyn.institutions.base import CourseReference
from devvyn.graph.unified import TransferEquivalency, UnifiedPrerequisiteGraph


@dataclass
class TransferAgreement:
    """
    A formal transfer agreement between institutions.

    Represents a block transfer where completing a program at one
    institution grants specific credits at another.
    """
    source_institution: str
    source_program: str
    target_institution: str
    target_program: str
    total_credits: float
    course_equivalencies: list[TransferEquivalency]
    effective_date: Optional[date] = None
    notes: str = ""
    url: str = ""


# =============================================================================
# Saskatchewan Polytechnic → University of Saskatchewan
# =============================================================================

# Computer Systems Technology → B.Sc. Computer Science
# Based on 2014 articulation agreement (renewed 2018)
# Source: https://artsandscience.usask.ca/students/documents/siast_computer_technology_renewal_agreement-2018.pdf

CST_TO_USASK_CMPT = TransferAgreement(
    source_institution="saskpolytech",
    source_program="CSTDP",  # Computer Systems Technology Diploma
    target_institution="usask",
    target_program="B.Sc. Computer Science",
    total_credits=54.0,
    effective_date=date(2014, 1, 1),
    notes="""
    Completion of the Saskatchewan Polytechnic Computer Systems Technology
    diploma program grants 54 credit units toward a B.Sc. in Computer Science.

    Students may complete a 4-year, Honours, or Honours (Software Engineering)
    degree in approximately 2 additional years of study ("Two+Two" arrangement).

    To maximize course selection, students should obtain credit for CMPT 215.3
    and CMPT 280.3 in the summer preceding their studies.

    Residency requirement: At least 42cu of senior (200+) courses from USask.
    """,
    url="https://artsandscience.usask.ca/students/documents/siast_computer_technology_renewal_agreement-2018.pdf",
    course_equivalencies=[
        # Direct CMPT equivalencies (24cu)
        # The diploma as a whole grants these credits - not 1:1 course mappings
        # These represent the USask courses that transfer students are deemed
        # to have completed.
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),  # Whole program
            course_to=CourseReference("usask", "CMPT 141"),
            notes="Intro to Computer Science (programming fundamentals)",
        ),
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("usask", "CMPT 145"),
            notes="Principles of Computer Science",
        ),
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("usask", "CMPT 214"),
            notes="Programming Principles and Practice",
        ),
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("usask", "CMPT 270"),
            notes="Developing Object-Oriented Systems",
        ),
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("usask", "CMPT 350"),
            notes="Introduction to Database Design",
        ),
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("usask", "CMPT 355"),
            notes="Computer Networks",
        ),
        # Non-major CMPT courses (6cu)
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("usask", "CMPT 100"),
            notes="Introduction to Computing (not in major)",
        ),
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("usask", "CMPT 281"),
            notes="Introduction to Software Engineering (not in major)",
        ),
    ],
)


# =============================================================================
# Saskatchewan Polytechnic → University of Regina
# =============================================================================

# Computer Systems Technology → Post-Diploma B.Sc. Computer Science
# Source: https://www.uregina.ca/science/computer-science/undergraduate-programs/bsc-post-diploma-cs.html

CST_TO_UREGINA_CS = TransferAgreement(
    source_institution="saskpolytech",
    source_program="CSTDP",  # Computer Systems Technology Diploma
    target_institution="uregina",
    target_program="Post-Diploma B.Sc. Computer Science",
    total_credits=60.0,
    effective_date=date(2017, 1, 1),  # Expanded agreement signed 2017
    notes="""
    Graduates of Saskatchewan Polytechnic's Computer Systems Technology diploma
    receive 60 credit hours toward the 120-credit B.Sc. in Computer Science.

    Remaining 20 courses required:
    - 9 Computer Science courses (Web/Database, Digital Systems, AI, Project)
    - 5 Mathematics courses (Calculus I & II, Linear Algebra, Proofs, +1 elective)
    - 2 English courses (Critical Reading and Writing I & II)
    - 4 Electives (2 Arts/Media, 2 Natural Science)

    Requirements:
    - Diploma completed within last 10 years
    - Minimum 70% graduating average
    - Math C30 or equivalent
    - Must maintain 65% GPA at U of R

    Typical completion time: 2 years.
    """,
    url="https://www.uregina.ca/science/computer-science/undergraduate-programs/bsc-post-diploma-cs.html",
    course_equivalencies=[
        # Block transfer - specific course equivalencies not published
        # U of R grants 60 credit hours as a block for the diploma
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("uregina", "CS 110"),
            notes="Programming and Problem Solving (block transfer)",
        ),
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("uregina", "CS 115"),
            notes="Object-Oriented Design (block transfer)",
        ),
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "CSTDP"),
            course_to=CourseReference("uregina", "CS 210"),
            notes="Data Structures and Abstractions (block transfer)",
        ),
    ],
)

# Business Information Systems → Post-Diploma B.Sc. Computer Science
BIS_TO_UREGINA_CS = TransferAgreement(
    source_institution="saskpolytech",
    source_program="BIS",  # Business Information Systems
    target_institution="uregina",
    target_program="Post-Diploma B.Sc. Computer Science",
    total_credits=60.0,
    effective_date=date(2017, 1, 1),
    notes="""
    Graduates of Saskatchewan Polytechnic's Business Information Systems diploma
    may also be eligible for the Post-Diploma B.Sc. in Computer Science.

    Same requirements as CST transfer:
    - 60 credit hours transferred
    - 20 courses (60 credits) remaining
    - Diploma within last 10 years, 70% average, Math C30
    """,
    url="https://www.uregina.ca/science/computer-science/undergraduate-programs/bsc-post-diploma-cs.html",
    course_equivalencies=[
        TransferEquivalency(
            course_from=CourseReference("saskpolytech", "BIS"),
            course_to=CourseReference("uregina", "CS 110"),
            notes="Programming fundamentals (block transfer)",
        ),
    ],
)

# Graphic Communications → Bachelor of Design
# Source: https://www.uregina.ca/news/2024/university-of-regina-and-saskatchewan-polytechnic-partner-to-enhance-new-pathways-for-creative-technologies-and-design-students.html

GRAPHIC_COMM_TO_UREGINA_DESIGN = TransferAgreement(
    source_institution="saskpolytech",
    source_program="GRAPHIC_COMM",  # Graphic Communications Diploma
    target_institution="uregina",
    target_program="Bachelor of Design",
    total_credits=60.0,
    effective_date=date(2024, 1, 1),
    notes="""
    Graduates of Saskatchewan Polytechnic's Graphic Communications diploma
    can transfer up to 60 credit hours (two years) toward the four-year
    Bachelor of Design degree at the University of Regina.

    Part of the expanded 2024 Creative Technologies and Design pathway.
    """,
    url="https://www.uregina.ca/news/2024/university-of-regina-and-saskatchewan-polytechnic-partner-to-enhance-new-pathways-for-creative-technologies-and-design-students.html",
    course_equivalencies=[],  # Block transfer, no specific course mappings
)

# Interactive Design and Technology → Bachelor of Design
IDT_TO_UREGINA_DESIGN = TransferAgreement(
    source_institution="saskpolytech",
    source_program="IDT",  # Interactive Design and Technology Diploma
    target_institution="uregina",
    target_program="Bachelor of Design",
    total_credits=60.0,
    effective_date=date(2024, 1, 1),
    notes="""
    Graduates of Saskatchewan Polytechnic's Interactive Design and Technology
    diploma can transfer up to 60 credit hours toward the Bachelor of Design.

    Part of the expanded 2024 Creative Technologies and Design pathway.
    """,
    url="https://www.uregina.ca/news/2024/university-of-regina-and-saskatchewan-polytechnic-partner-to-enhance-new-pathways-for-creative-technologies-and-design-students.html",
    course_equivalencies=[],
)

# Engineering Design and Drafting Technology → Bachelor of Design
EDDT_TO_UREGINA_DESIGN = TransferAgreement(
    source_institution="saskpolytech",
    source_program="EDDT",  # Engineering Design and Drafting Technology
    target_institution="uregina",
    target_program="Bachelor of Design",
    total_credits=60.0,
    effective_date=date(2024, 1, 1),
    notes="""
    Graduates of Saskatchewan Polytechnic's Engineering Design and Drafting
    Technology diploma can transfer up to 60 credit hours toward the
    Bachelor of Design degree.

    Part of the expanded 2024 Creative Technologies and Design pathway.
    """,
    url="https://www.uregina.ca/news/2024/university-of-regina-and-saskatchewan-polytechnic-partner-to-enhance-new-pathways-for-creative-technologies-and-design-students.html",
    course_equivalencies=[],
)


# Course-level equivalencies (approximate mappings based on content)
# These are INFORMAL suggestions based on similar course content
# Official credit is granted for the diploma as a whole, not individual courses

COURSE_CONTENT_SIMILARITIES = [
    # SaskPolytech → USask (based on course content similarity)
    ("COSC 180", "CMPT 141", "Both cover intro programming"),
    ("COSC 182", "CMPT 145", "Both cover intermediate programming concepts"),
    ("CDBM 280", "CMPT 350", "Both cover database management"),
    ("CNET 184", "CMPT 355", "Both cover networking fundamentals"),
    ("COSA 190", "CMPT 270", "Both cover software design/OO concepts"),
]

# SaskPolytech → U of R content similarities
COURSE_CONTENT_SIMILARITIES_UREGINA = [
    ("COSC 180", "CS 110", "Both cover intro programming"),
    ("COSC 182", "CS 115", "Both cover OO design"),
    ("COSC 286", "CS 210", "Both cover data structures"),
]


def get_all_agreements() -> list[TransferAgreement]:
    """Get all known transfer agreements."""
    return [
        # USask pathways
        CST_TO_USASK_CMPT,
        # U of R pathways
        CST_TO_UREGINA_CS,
        BIS_TO_UREGINA_CS,
        GRAPHIC_COMM_TO_UREGINA_DESIGN,
        IDT_TO_UREGINA_DESIGN,
        EDDT_TO_UREGINA_DESIGN,
    ]


def get_agreements_from(source_institution: str) -> list[TransferAgreement]:
    """Get all transfer agreements from a source institution."""
    return [
        a for a in get_all_agreements()
        if a.source_institution == source_institution
    ]


def get_agreements_to(target_institution: str) -> list[TransferAgreement]:
    """Get all transfer agreements to a target institution."""
    return [
        a for a in get_all_agreements()
        if a.target_institution == target_institution
    ]


def add_transfer_equivalencies(graph: UnifiedPrerequisiteGraph) -> None:
    """
    Add all known transfer equivalencies to a unified graph.

    This enables cross-institution prerequisite queries.
    """
    for agreement in get_all_agreements():
        for equiv in agreement.course_equivalencies:
            graph.add_equivalency(equiv)

    # Also add course content similarities as informal equivalencies
    for sp_code, usask_code, notes in COURSE_CONTENT_SIMILARITIES:
        graph.add_equivalency(TransferEquivalency(
            course_from=CourseReference("saskpolytech", sp_code),
            course_to=CourseReference("usask", usask_code),
            notes=f"Content similarity: {notes}",
            bidirectional=False,  # One-way: SP course prepares for USask
        ))

    # U of R content similarities
    for sp_code, uregina_code, notes in COURSE_CONTENT_SIMILARITIES_UREGINA:
        graph.add_equivalency(TransferEquivalency(
            course_from=CourseReference("saskpolytech", sp_code),
            course_to=CourseReference("uregina", uregina_code),
            notes=f"Content similarity: {notes}",
            bidirectional=False,
        ))


def describe_transfer_path(
    source_program: str,
    source_institution: str = "saskpolytech",
    target_institution: str = "usask"
) -> str:
    """
    Generate a human-readable description of a transfer path.

    Args:
        source_program: Program code at source (e.g., "CSTDP")
        source_institution: Source institution ID
        target_institution: Target institution ID

    Returns:
        Formatted description of transfer options
    """
    agreements = [
        a for a in get_all_agreements()
        if a.source_institution == source_institution
        and a.target_institution == target_institution
        and a.source_program == source_program
    ]

    if not agreements:
        return f"No transfer agreements found for {source_program}"

    lines = []
    for agreement in agreements:
        lines.append(f"=== {agreement.source_program} → {agreement.target_program} ===")
        lines.append(f"Total credits transferred: {agreement.total_credits}")
        lines.append("")
        lines.append("Course credits granted:")
        for equiv in agreement.course_equivalencies:
            lines.append(f"  • {equiv.course_to.code}: {equiv.notes}")
        lines.append("")
        lines.append(agreement.notes.strip())
        if agreement.url:
            lines.append(f"\nSource: {agreement.url}")

    return "\n".join(lines)


# Demo
if __name__ == "__main__":
    print(describe_transfer_path("CSTDP"))
