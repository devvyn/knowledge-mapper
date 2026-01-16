"""
USask degree program definitions.

Contains requirement structures for USask degrees.
TODO: Populate with actual program data from USask calendars.
"""
from typing import Optional

from devvyn.degrees.models import (
    DegreeProgram,
    RequirementBlock,
    CourseRequirement,
    CoursePool,
    CredentialType,
)


# Placeholder programs - need to be populated with actual USask requirements
_USASK_PROGRAMS: list[DegreeProgram] = [
    DegreeProgram(
        id="usask:bsc-4yr-cmpt",
        institution="usask",
        name="Bachelor of Science Four-year - Computer Science",
        credential=CredentialType.BACHELOR_4YR,
        total_credits=120.0,
        senior_credits=66.0,
        requirements=[
            RequirementBlock(
                code="C1",
                name="College Requirement",
                total_credits=15.0,
                required_courses=[
                    CourseRequirement("ENG 110", 6.0),
                ],
                course_pools=[
                    CoursePool(
                        name="Indigenous Learning",
                        courses=[CourseRequirement(c, 3.0) for c in [
                            "INDG 107", "INDG 108", "NURS 203"
                        ]],
                        pick_credits=3.0,
                    ),
                    CoursePool(
                        name="Quantitative Reasoning",
                        courses=[CourseRequirement(c, 3.0) for c in [
                            "MATH 110", "MATH 164", "STAT 245"
                        ]],
                        pick_credits=6.0,
                    ),
                ],
            ),
            RequirementBlock(
                code="C4",
                name="Major Requirement",
                total_credits=48.0,
                required_courses=[
                    CourseRequirement("CMPT 141", 3.0),
                    CourseRequirement("CMPT 145", 3.0),
                    CourseRequirement("CMPT 214", 3.0),
                    CourseRequirement("CMPT 260", 3.0),
                    CourseRequirement("CMPT 270", 3.0),
                    CourseRequirement("CMPT 280", 3.0),
                    CourseRequirement("CMPT 332", 3.0),
                    CourseRequirement("CMPT 360", 3.0),
                    CourseRequirement("MATH 110", 3.0),
                    CourseRequirement("MATH 116", 3.0),
                    CourseRequirement("STAT 245", 3.0),
                ],
                course_pools=[
                    CoursePool(
                        name="CMPT Electives",
                        courses=[CourseRequirement(c, 3.0) for c in [
                            "CMPT 317", "CMPT 340", "CMPT 350", "CMPT 353",
                            "CMPT 370", "CMPT 394", "CMPT 400", "CMPT 405",
                            "CMPT 411", "CMPT 412", "CMPT 416", "CMPT 434",
                        ]],
                        pick_credits=15.0,
                        min_level=300,
                    ),
                ],
            ),
        ],
        url="https://catalogue.usask.ca/computer-science",
    ),
    DegreeProgram(
        id="usask:bsc-3yr-cmpt",
        institution="usask",
        name="Bachelor of Science Three-year - Computer Science",
        credential=CredentialType.BACHELOR_3YR,
        total_credits=90.0,
        senior_credits=48.0,
        requirements=[
            RequirementBlock(
                code="C4",
                name="Major Requirement",
                total_credits=36.0,
                required_courses=[
                    CourseRequirement("CMPT 141", 3.0),
                    CourseRequirement("CMPT 145", 3.0),
                    CourseRequirement("CMPT 214", 3.0),
                    CourseRequirement("CMPT 260", 3.0),
                    CourseRequirement("CMPT 270", 3.0),
                    CourseRequirement("CMPT 280", 3.0),
                ],
                course_pools=[
                    CoursePool(
                        name="CMPT Electives",
                        courses=[CourseRequirement(c, 3.0) for c in [
                            "CMPT 317", "CMPT 332", "CMPT 340", "CMPT 350",
                            "CMPT 360", "CMPT 370",
                        ]],
                        pick_credits=12.0,
                        min_level=300,
                    ),
                ],
            ),
        ],
        url="https://catalogue.usask.ca/computer-science",
    ),
]


def get_usask_programs() -> list[DegreeProgram]:
    """Get all USask degree programs."""
    return _USASK_PROGRAMS


def get_program(program_id: str) -> Optional[DegreeProgram]:
    """Get a program by ID."""
    for p in _USASK_PROGRAMS:
        if p.id == program_id:
            return p
    return None
