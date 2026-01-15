"""
University of Saskatchewan degree program definitions.

Data sourced from: https://programs.usask.ca/
"""
from devvyn.degrees.models import (
    DegreeProgram,
    RequirementBlock,
    CourseRequirement,
    CoursePool,
    SubjectRequirement,
    CredentialType,
)


# =============================================================================
# Shared requirement blocks (used across multiple programs)
# =============================================================================

def _c1_college_15cu() -> RequirementBlock:
    """C1 College Requirement - 15 credit units (standard for 4-year degrees)."""
    return RequirementBlock(
        code="C1",
        name="College Requirement",
        total_credits=15.0,
        course_pools=[
            CoursePool(
                name="English Language Writing",
                pick_credits=6.0,
                courses=[
                    # Extensive list - these are common choices
                    CourseRequirement("ENG 110"),
                    CourseRequirement("ENG 111"),
                    CourseRequirement("ENG 112"),
                    CourseRequirement("ENG 113"),
                    CourseRequirement("ENG 114"),
                    CourseRequirement("HIST 115"),
                    CourseRequirement("PHIL 115"),
                ],
                notes="From designated English Writing courses",
            ),
            CoursePool(
                name="Indigenous Learning",
                pick_credits=3.0,
                courses=[
                    CourseRequirement("INDG 107"),
                    CourseRequirement("INDG 201"),
                    CourseRequirement("INDG 202"),
                ],
                notes="From designated Indigenous Learning courses",
            ),
            CoursePool(
                name="Quantitative Reasoning",
                pick_credits=3.0,
                courses=[
                    CourseRequirement("MATH 163"),
                    CourseRequirement("MATH 164"),
                ],
            ),
        ],
        notes="Shared across all Arts & Science programs",
    )


def _c1_college_9cu() -> RequirementBlock:
    """C1 College Requirement - 9 credit units (for double honours where Quant is in C4)."""
    return RequirementBlock(
        code="C1",
        name="College Requirement",
        total_credits=9.0,
        course_pools=[
            CoursePool(
                name="English Language Writing",
                pick_credits=6.0,
                courses=[
                    CourseRequirement("ENG 110"),
                    CourseRequirement("ENG 111"),
                    CourseRequirement("ENG 112"),
                ],
            ),
            CoursePool(
                name="Indigenous Learning",
                pick_credits=3.0,
                courses=[
                    CourseRequirement("INDG 107"),
                    CourseRequirement("INDG 201"),
                ],
            ),
        ],
        notes="Quantitative reasoning satisfied in major",
    )


def _c2_breadth() -> RequirementBlock:
    """C2 Breadth Requirement - 9 credit units."""
    return RequirementBlock(
        code="C2",
        name="Breadth Requirement",
        total_credits=9.0,
        subject_requirements=[
            SubjectRequirement(
                subjects=["Fine Arts", "Humanities", "Social Sciences"],
                credits=9.0,
                notes="Min 3cu from Humanities or Social Sciences",
            ),
        ],
        notes="From Fine Arts, Humanities, Social Sciences",
    )


# =============================================================================
# Computer Science Programs
# =============================================================================

BSC_3YR_CMPT = DegreeProgram(
    id="usask:bsc-3yr-cmpt",
    institution="usask",
    name="Bachelor of Science Three-year - Computer Science",
    credential=CredentialType.BACHELOR_3YR,
    total_credits=90.0,
    senior_credits=42.0,
    requirements=[
        _c1_college_15cu(),
        _c2_breadth(),
        RequirementBlock(
            code="C3",
            name="Cognate Requirement",
            total_credits=12.0,
            subject_requirements=[
                SubjectRequirement(
                    subjects=["BIOL", "CHEM", "GEOL", "PHYS"],
                    credits=9.0,
                    max_per_subject=6.0,
                    notes="Junior level from sciences",
                ),
            ],
            course_pools=[
                CoursePool(
                    name="Math elective",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 110"),
                        CourseRequirement("MATH 133"),
                        CourseRequirement("MATH 176"),
                    ],
                ),
            ],
        ),
        RequirementBlock(
            code="C4",
            name="Major Requirement",
            total_credits=33.0,
            course_pools=[
                CoursePool(
                    name="Intro programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 116"),
                        CourseRequirement("CMPT 141"),
                    ],
                ),
                CoursePool(
                    name="Second programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 117"),
                        CourseRequirement("CMPT 145"),
                    ],
                ),
                CoursePool(
                    name="Systems programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 215"),
                        CourseRequirement("CME 331"),
                    ],
                ),
                CoursePool(
                    name="Discrete math",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 260"),
                        CourseRequirement("CMPT 263"),
                    ],
                ),
                CoursePool(
                    name="Senior CMPT electives",
                    pick_credits=9.0,
                    courses=[
                        CourseRequirement("CMPT 317"),
                        CourseRequirement("CMPT 332"),
                        CourseRequirement("CMPT 340"),
                        CourseRequirement("CMPT 353"),
                        CourseRequirement("CMPT 360"),
                        CourseRequirement("CMPT 370"),
                        CourseRequirement("CMPT 381"),
                    ],
                    min_level=300,
                ),
                CoursePool(
                    name="Statistics",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("STAT 242"),
                        CourseRequirement("STAT 245"),
                    ],
                ),
            ],
            required_courses=[
                CourseRequirement("CMPT 214"),
                CourseRequirement("CMPT 270"),
                CourseRequirement("CMPT 280"),
            ],
        ),
        RequirementBlock(
            code="C5",
            name="Electives",
            total_credits=21.0,
            notes="Arts and Science approved courses",
        ),
    ],
    url="https://programs.usask.ca/arts-and-science/computer-science/bsc-3-computer-science.php",
)


BSC_4YR_CMPT = DegreeProgram(
    id="usask:bsc-4yr-cmpt",
    institution="usask",
    name="Bachelor of Science Four-year - Computer Science",
    credential=CredentialType.BACHELOR_4YR,
    total_credits=120.0,
    senior_credits=66.0,
    requirements=[
        _c1_college_15cu(),
        _c2_breadth(),
        RequirementBlock(
            code="C3",
            name="Cognate Requirement",
            total_credits=15.0,
            subject_requirements=[
                SubjectRequirement(
                    subjects=["BIOL", "CHEM", "GEOL", "PHYS"],
                    credits=9.0,
                    max_per_subject=6.0,
                ),
            ],
            required_courses=[
                CourseRequirement("PHIL 232", notes="Ethics"),
            ],
            course_pools=[
                CoursePool(
                    name="Math elective",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 110"),
                        CourseRequirement("MATH 133"),
                        CourseRequirement("MATH 176"),
                    ],
                ),
            ],
        ),
        RequirementBlock(
            code="C4",
            name="Major Requirement",
            total_credits=57.0,
            course_pools=[
                CoursePool(
                    name="Intro programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 116"),
                        CourseRequirement("CMPT 141"),
                    ],
                ),
                CoursePool(
                    name="Second programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 117"),
                        CourseRequirement("CMPT 145"),
                    ],
                ),
                CoursePool(
                    name="Systems programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 215"),
                        CourseRequirement("CME 331"),
                    ],
                ),
                CoursePool(
                    name="Discrete math",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 260"),
                        CourseRequirement("CMPT 263"),
                    ],
                ),
                CoursePool(
                    name="Core CMPT electives",
                    pick_credits=18.0,
                    courses=[
                        CourseRequirement("CMPT 317"),
                        CourseRequirement("CMPT 332"),
                        CourseRequirement("CMPT 340"),
                        CourseRequirement("CMPT 353"),
                        CourseRequirement("CMPT 360"),
                        CourseRequirement("CMPT 370"),
                        CourseRequirement("CMPT 381"),
                    ],
                ),
                CoursePool(
                    name="400-level CMPT",
                    pick_credits=6.0,
                    courses=[
                        CourseRequirement("CMPT 411"),
                        CourseRequirement("CMPT 412"),
                        CourseRequirement("CMPT 413"),
                        CourseRequirement("CMPT 414"),
                        CourseRequirement("CMPT 415"),
                        CourseRequirement("CMPT 417"),
                        CourseRequirement("CMPT 423"),
                        CourseRequirement("CMPT 434"),
                        CourseRequirement("CMPT 440"),
                        CourseRequirement("CMPT 450"),
                        CourseRequirement("CMPT 480"),
                        CourseRequirement("CMPT 481"),
                        CourseRequirement("CMPT 489"),
                    ],
                    min_level=400,
                    notes="Excluding CMPT 400-409",
                ),
                CoursePool(
                    name="Senior CMPT/CME",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CME 341"),
                        CourseRequirement("CME 342"),
                    ],
                    min_level=300,
                ),
                CoursePool(
                    name="Statistics",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("STAT 242"),
                        CourseRequirement("STAT 245"),
                        CourseRequirement("EE 216"),
                    ],
                ),
                CoursePool(
                    name="Math electives",
                    pick_credits=6.0,
                    courses=[
                        CourseRequirement("MATH 116"),
                        CourseRequirement("MATH 134"),
                        CourseRequirement("MATH 177"),
                        CourseRequirement("MATH 211"),
                        CourseRequirement("MATH 223"),
                        CourseRequirement("MATH 225"),
                        CourseRequirement("MATH 266"),
                        CourseRequirement("MATH 276"),
                        CourseRequirement("MATH 327"),
                        CourseRequirement("MATH 328"),
                        CourseRequirement("MATH 361"),
                        CourseRequirement("MATH 362"),
                        CourseRequirement("MATH 364"),
                        CourseRequirement("STAT 241"),
                        CourseRequirement("STAT 344"),
                        CourseRequirement("STAT 345"),
                        CourseRequirement("STAT 348"),
                        CourseRequirement("PHIL 243"),
                    ],
                ),
            ],
            required_courses=[
                CourseRequirement("CMPT 214"),
                CourseRequirement("CMPT 270"),
                CourseRequirement("CMPT 280"),
            ],
        ),
        RequirementBlock(
            code="C5",
            name="Electives",
            total_credits=24.0,
            notes="Arts and Science approved courses",
        ),
    ],
    url="https://programs.usask.ca/arts-and-science/computer-science/bsc-4-computer-science.php",
)


BSC_HONOURS_CMPT = DegreeProgram(
    id="usask:bsc-honours-cmpt",
    institution="usask",
    name="Bachelor of Science Honours - Computer Science",
    credential=CredentialType.HONOURS,
    total_credits=120.0,
    senior_credits=66.0,
    min_gpa=70.0,
    requirements=[
        _c1_college_15cu(),
        _c2_breadth(),
        RequirementBlock(
            code="C3",
            name="Cognate Requirement",
            total_credits=15.0,
            subject_requirements=[
                SubjectRequirement(
                    subjects=["BIOL", "CHEM", "GEOL", "PHYS"],
                    credits=9.0,
                    max_per_subject=6.0,
                ),
            ],
            required_courses=[
                CourseRequirement("PHIL 232"),
            ],
            course_pools=[
                CoursePool(
                    name="Math elective",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 110"),
                        CourseRequirement("MATH 133"),
                        CourseRequirement("MATH 176"),
                    ],
                ),
            ],
        ),
        RequirementBlock(
            code="C4",
            name="Major Requirement",
            total_credits=60.0,
            required_courses=[
                CourseRequirement("CMPT 214"),
                CourseRequirement("CMPT 270"),
                CourseRequirement("CMPT 280"),
                CourseRequirement("CMPT 360"),
                CourseRequirement("CMPT 364"),
                CourseRequirement("CMPT 400"),  # Honours thesis/project
                CourseRequirement("STAT 241"),
            ],
            course_pools=[
                CoursePool(
                    name="Intro programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 116"),
                        CourseRequirement("CMPT 141"),
                    ],
                ),
                CoursePool(
                    name="Second programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 117"),
                        CourseRequirement("CMPT 145"),
                    ],
                ),
                CoursePool(
                    name="Systems programming",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 215"),
                        CourseRequirement("CME 331"),
                    ],
                ),
                CoursePool(
                    name="Discrete math",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 260"),
                        CourseRequirement("CMPT 263"),
                    ],
                ),
                CoursePool(
                    name="Core CMPT electives",
                    pick_credits=15.0,
                    courses=[
                        CourseRequirement("CMPT 317"),
                        CourseRequirement("CMPT 332"),
                        CourseRequirement("CMPT 340"),
                        CourseRequirement("CMPT 353"),
                        CourseRequirement("CMPT 370"),
                        CourseRequirement("CMPT 381"),
                    ],
                ),
                CoursePool(
                    name="410+ level CMPT",
                    pick_credits=6.0,
                    courses=[
                        CourseRequirement("CMPT 411"),
                        CourseRequirement("CMPT 412"),
                        CourseRequirement("CMPT 413"),
                        CourseRequirement("CMPT 414"),
                        CourseRequirement("CME 433"),
                        CourseRequirement("CME 435"),
                    ],
                    min_level=410,
                ),
                CoursePool(
                    name="Math/Stat elective",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 116"),
                        CourseRequirement("MATH 134"),
                        CourseRequirement("MATH 177"),
                    ],
                ),
                CoursePool(
                    name="Statistics",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("STAT 242"),
                        CourseRequirement("STAT 245"),
                    ],
                ),
            ],
        ),
        RequirementBlock(
            code="C5",
            name="Electives",
            total_credits=21.0,
            notes="Arts and Science approved courses",
        ),
    ],
    url="https://programs.usask.ca/arts-and-science/computer-science/bsc-honours-computer-science.php",
)


# =============================================================================
# Mathematics Programs
# =============================================================================

BSC_3YR_MATH = DegreeProgram(
    id="usask:bsc-3yr-math",
    institution="usask",
    name="Bachelor of Science Three-year - Mathematics",
    credential=CredentialType.BACHELOR_3YR,
    total_credits=90.0,
    senior_credits=42.0,
    requirements=[
        _c1_college_15cu(),
        _c2_breadth(),
        RequirementBlock(
            code="C3",
            name="Cognate Requirement",
            total_credits=15.0,
            subject_requirements=[
                SubjectRequirement(
                    subjects=["BIOL", "CHEM", "CMPT", "GEOL", "PHYS"],
                    credits=15.0,
                    notes="CMPT recommended for 6cu",
                ),
            ],
        ),
        RequirementBlock(
            code="C4",
            name="Major Requirement",
            total_credits=33.0,
            required_courses=[
                CourseRequirement("MATH 163"),
                CourseRequirement("MATH 164"),
                CourseRequirement("MATH 266"),
                CourseRequirement("STAT 241"),
            ],
            course_pools=[
                CoursePool(
                    name="Calculus I alternative",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 110"),
                        CourseRequirement("MATH 176"),
                    ],
                ),
                CoursePool(
                    name="Calculus II alternative",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 116"),
                        CourseRequirement("MATH 177"),
                    ],
                ),
                CoursePool(
                    name="Linear Algebra I alternative",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 225"),
                        CourseRequirement("MATH 276"),
                    ],
                ),
                CoursePool(
                    name="Linear Algebra II alternative",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 226"),
                        CourseRequirement("MATH 277"),
                    ],
                ),
                CoursePool(
                    name="Additional MATH",
                    pick_credits=9.0,
                    courses=[
                        CourseRequirement("MATH 211"),
                        CourseRequirement("MATH 238"),
                        CourseRequirement("MATH 258"),
                        CourseRequirement("MATH 327"),
                        CourseRequirement("MATH 328"),
                        CourseRequirement("MATH 361"),
                        CourseRequirement("MATH 362"),
                        CourseRequirement("STAT 242"),
                    ],
                    min_level=300,
                    notes="At least 6cu at 300-level",
                ),
            ],
        ),
        RequirementBlock(
            code="C5",
            name="Electives",
            total_credits=24.0,
        ),
    ],
    url="https://programs.usask.ca/arts-and-science/mathematics/bsc-3-math.php",
)


BSC_4YR_MATH = DegreeProgram(
    id="usask:bsc-4yr-math",
    institution="usask",
    name="Bachelor of Science Four-year - Mathematics",
    credential=CredentialType.BACHELOR_4YR,
    total_credits=120.0,
    senior_credits=66.0,
    requirements=[
        _c1_college_15cu(),
        _c2_breadth(),
        RequirementBlock(
            code="C3",
            name="Cognate Requirement",
            total_credits=15.0,
            subject_requirements=[
                SubjectRequirement(
                    subjects=["BIOL", "CHEM", "CMPT", "GEOL", "PHYS"],
                    credits=15.0,
                    notes="CMPT recommended for 6cu",
                ),
            ],
        ),
        RequirementBlock(
            code="C4",
            name="Major Requirement",
            total_credits=45.0,
            required_courses=[
                CourseRequirement("MATH 163"),
                CourseRequirement("MATH 164"),
                CourseRequirement("MATH 266"),
                CourseRequirement("STAT 241"),
            ],
            course_pools=[
                CoursePool(
                    name="Calculus I",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 110"),
                        CourseRequirement("MATH 176"),
                    ],
                ),
                CoursePool(
                    name="Calculus II",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 116"),
                        CourseRequirement("MATH 177"),
                    ],
                ),
                CoursePool(
                    name="Linear Algebra I",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 225"),
                        CourseRequirement("MATH 276"),
                    ],
                ),
                CoursePool(
                    name="Linear Algebra II",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 226"),
                        CourseRequirement("MATH 277"),
                    ],
                ),
                CoursePool(
                    name="200+ level",
                    pick_credits=6.0,
                    courses=[
                        CourseRequirement("MATH 211"),
                        CourseRequirement("MATH 223"),
                        CourseRequirement("MATH 238"),
                        CourseRequirement("MATH 258"),
                    ],
                    min_level=200,
                ),
                CoursePool(
                    name="300+ level",
                    pick_credits=12.0,
                    courses=[
                        CourseRequirement("MATH 327"),
                        CourseRequirement("MATH 328"),
                        CourseRequirement("MATH 361"),
                        CourseRequirement("MATH 362"),
                        CourseRequirement("MATH 364"),
                        CourseRequirement("MATH 371"),
                        CourseRequirement("MATH 379"),
                        CourseRequirement("STAT 344"),
                        CourseRequirement("STAT 345"),
                    ],
                    min_level=300,
                ),
            ],
        ),
        RequirementBlock(
            code="C5",
            name="Electives",
            total_credits=42.0,
        ),
    ],
    url="https://programs.usask.ca/arts-and-science/mathematics/bsc-4-math.php",
)


# =============================================================================
# Double Honours Programs
# =============================================================================

BSC_DOUBLE_HONOURS_CMPT_MATH = DegreeProgram(
    id="usask:bsc-dbl-honours-cmpt-math",
    institution="usask",
    name="Bachelor of Science Double Honours - Computer Science and Mathematics",
    credential=CredentialType.DOUBLE_HONOURS,
    total_credits=120.0,
    senior_credits=66.0,
    min_gpa=70.0,
    requirements=[
        _c1_college_9cu(),  # Reduced because quant is in C4
        _c2_breadth(),
        RequirementBlock(
            code="C3",
            name="Cognate Requirement",
            total_credits=9.0,
            subject_requirements=[
                SubjectRequirement(
                    subjects=["BIOL", "CHEM", "GEOL", "PHYS"],
                    credits=9.0,
                    max_per_subject=6.0,
                ),
            ],
        ),
        RequirementBlock(
            code="C4",
            name="Combined Major Requirement",
            total_credits=84.0,
            notes="Integrated CS + Math requirements",
            required_courses=[
                # CMPT core
                CourseRequirement("CMPT 214"),
                CourseRequirement("CMPT 270"),
                CourseRequirement("CMPT 280"),
                CourseRequirement("CMPT 360"),
                CourseRequirement("CMPT 364"),
                CourseRequirement("CMPT 400"),
                # MATH core
                CourseRequirement("MATH 163"),
                CourseRequirement("MATH 164"),
                CourseRequirement("MATH 238"),
                CourseRequirement("MATH 266"),
                CourseRequirement("MATH 276"),
                CourseRequirement("MATH 277"),
                CourseRequirement("MATH 361"),
                CourseRequirement("MATH 362"),
                CourseRequirement("MATH 371"),
                CourseRequirement("MATH 379"),
                # Shared
                CourseRequirement("STAT 241"),
            ],
            course_pools=[
                CoursePool(
                    name="Intro CS",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 116"),
                        CourseRequirement("CMPT 142"),
                    ],
                ),
                CoursePool(
                    name="Second CS",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 117"),
                        CourseRequirement("CMPT 145"),
                        CourseRequirement("CMPT 146"),
                    ],
                ),
                CoursePool(
                    name="Systems",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 215"),
                        CourseRequirement("CME 331"),
                    ],
                ),
                CoursePool(
                    name="Discrete",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 260"),
                        CourseRequirement("CMPT 263"),
                    ],
                ),
                CoursePool(
                    name="Calculus I",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 110"),
                        CourseRequirement("MATH 133"),
                        CourseRequirement("MATH 176"),
                    ],
                ),
                CoursePool(
                    name="Calculus II",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("MATH 116"),
                        CourseRequirement("MATH 134"),
                        CourseRequirement("MATH 177"),
                    ],
                ),
                CoursePool(
                    name="CMPT electives",
                    pick_credits=9.0,
                    courses=[
                        CourseRequirement("CMPT 317"),
                        CourseRequirement("CMPT 332"),
                        CourseRequirement("CMPT 340"),
                        CourseRequirement("CMPT 353"),
                        CourseRequirement("CMPT 370"),
                        CourseRequirement("CMPT 381"),
                    ],
                ),
                CoursePool(
                    name="Senior CMPT",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 411"),
                        CourseRequirement("CMPT 412"),
                        CourseRequirement("CMPT 413"),
                    ],
                    min_level=410,
                ),
                CoursePool(
                    name="Additional MATH/STAT",
                    pick_credits=6.0,
                    courses=[
                        CourseRequirement("MATH 211"),
                        CourseRequirement("MATH 327"),
                        CourseRequirement("MATH 328"),
                        CourseRequirement("STAT 344"),
                        CourseRequirement("STAT 345"),
                    ],
                    min_level=300,
                ),
            ],
        ),
        RequirementBlock(
            code="C5",
            name="Electives",
            total_credits=9.0,
        ),
    ],
    url="https://programs.usask.ca/arts-and-science/computer-science/bsc-double-honours-computer-science-and-math-1-and-2.php",
)


# =============================================================================
# Minors
# =============================================================================

MINOR_CMPT = DegreeProgram(
    id="usask:minor-cmpt",
    institution="usask",
    name="Computer Science Minor",
    credential=CredentialType.MINOR,
    total_credits=18.0,
    senior_credits=3.0,  # Min 3cu at 300+
    requirements=[
        RequirementBlock(
            code="M1",
            name="Minor Requirement",
            total_credits=18.0,
            course_pools=[
                CoursePool(
                    name="Intro (max 3cu)",
                    pick_credits=3.0,
                    courses=[
                        CourseRequirement("CMPT 100"),
                        CourseRequirement("CMPT 102"),
                        CourseRequirement("CMPT 105"),
                        CourseRequirement("CMPT 111"),
                        CourseRequirement("CMPT 113"),
                        CourseRequirement("CMPT 115"),
                        CourseRequirement("CMPT 116"),
                        CourseRequirement("CMPT 140"),
                        CourseRequirement("CMPT 141"),
                        CourseRequirement("CMPT 175"),
                    ],
                    notes="Maximum 3cu from introductory courses",
                ),
                CoursePool(
                    name="Additional CMPT",
                    pick_credits=15.0,
                    courses=[
                        CourseRequirement("CMPT 145"),
                        CourseRequirement("CMPT 214"),
                        CourseRequirement("CMPT 215"),
                        CourseRequirement("CMPT 260"),
                        CourseRequirement("CMPT 270"),
                        CourseRequirement("CMPT 280"),
                        CourseRequirement("CMPT 317"),
                        CourseRequirement("CMPT 332"),
                        CourseRequirement("CMPT 340"),
                        CourseRequirement("CMPT 353"),
                        CourseRequirement("CMPT 360"),
                        CourseRequirement("CMPT 370"),
                        CourseRequirement("CMPT 381"),
                    ],
                    notes="Min 3cu at 300+ level",
                ),
            ],
        ),
    ],
    notes="Cannot combine with Major in Applied Computing",
    url="https://programs.usask.ca/arts-and-science/computer-science/minor-computer-science.php",
)


MINOR_MATH = DegreeProgram(
    id="usask:minor-math",
    institution="usask",
    name="Mathematics Minor",
    credential=CredentialType.MINOR,
    total_credits=18.0,
    senior_credits=3.0,
    requirements=[
        RequirementBlock(
            code="M1",
            name="Minor Requirement",
            total_credits=18.0,
            course_pools=[
                CoursePool(
                    name="MATH courses",
                    pick_credits=18.0,
                    courses=[
                        CourseRequirement("MATH 110"),
                        CourseRequirement("MATH 116"),
                        CourseRequirement("MATH 163"),
                        CourseRequirement("MATH 164"),
                        CourseRequirement("MATH 176"),
                        CourseRequirement("MATH 177"),
                        CourseRequirement("MATH 211"),
                        CourseRequirement("MATH 225"),
                        CourseRequirement("MATH 226"),
                        CourseRequirement("MATH 238"),
                        CourseRequirement("MATH 266"),
                        CourseRequirement("MATH 276"),
                        CourseRequirement("MATH 277"),
                        CourseRequirement("MATH 327"),
                        CourseRequirement("MATH 328"),
                        CourseRequirement("MATH 361"),
                        CourseRequirement("MATH 362"),
                    ],
                    notes="Min 3cu at 300+ level. Excludes MATH 101, 102, 104, 125, 150",
                ),
            ],
        ),
    ],
    url="https://programs.usask.ca/arts-and-science/mathematics/mathematics-minor.php",
)


# =============================================================================
# Registry
# =============================================================================

_ALL_PROGRAMS: list[DegreeProgram] = [
    # CS
    BSC_3YR_CMPT,
    BSC_4YR_CMPT,
    BSC_HONOURS_CMPT,
    # Math
    BSC_3YR_MATH,
    BSC_4YR_MATH,
    # Double Honours
    BSC_DOUBLE_HONOURS_CMPT_MATH,
    # Minors
    MINOR_CMPT,
    MINOR_MATH,
]


def get_usask_programs() -> list[DegreeProgram]:
    """Get all USask degree programs."""
    return _ALL_PROGRAMS.copy()


def get_program(program_id: str) -> DegreeProgram | None:
    """Get a specific program by ID."""
    for program in _ALL_PROGRAMS:
        if program.id == program_id:
            return program
    return None


def get_programs_by_credential(credential: CredentialType) -> list[DegreeProgram]:
    """Get all programs of a given credential type."""
    return [p for p in _ALL_PROGRAMS if p.credential == credential]
