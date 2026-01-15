"""
Sample course completion data demonstrating textbooks, work requirements, and exams.

This file shows how to model a complete course with:
- Required textbooks and materials
- Assignments, labs, and projects
- Midterm and final exams as terminal nodes in the directed graph

The graph structure for a course like CMPT 141:

    Textbook (Zelle) ──────────────────────────────────────┐
         │                                                 │
         ▼                                                 │
    Reading Ch.1-3 ──► Assignment 1 ──┐                    │
                                      │                    │
    Reading Ch.4-6 ──► Assignment 2 ──┼──► Midterm ───┐    │
                           │          │               │    │
    Reading Ch.7-9 ──► Lab 1-4 ───────┘               │    │
                           │                          │    │
    Reading Ch.10-12 ──► Project ─────────────────────┼──► Final Exam
                                                      │
                           Midterm ───────────────────┘
"""
from devvyn.institutions.base import CourseReference
from devvyn.model.course_materials import (
    Textbook,
    TextbookReference,
    WorkRequirement,
    WorkRequirementRef,
    WorkRequirementType,
    FinalExam,
    ExamRef,
    CourseCompletion,
    MaterialType,
)


def create_cmpt141_completion() -> CourseCompletion:
    """
    Create a complete course model for CMPT 141 - Introduction to Computer Science.

    This demonstrates all the new model types working together.
    """
    course_ref = CourseReference(institution="usask", code="CMPT 141")

    # --- Textbooks ---
    zelle_textbook = Textbook(
        ref=TextbookReference(isbn="9781590282755"),
        title="Python Programming: An Introduction to Computer Science",
        authors=["John Zelle"],
        edition="3rd",
        publisher="Franklin, Beedle & Associates",
        year=2016,
        material_type=MaterialType.TEXTBOOK,
        chapters=[
            "Chapter 1: Computers and Programs",
            "Chapter 2: Writing Simple Programs",
            "Chapter 3: Computing with Numbers",
            "Chapter 4: Objects and Graphics",
            "Chapter 5: Sequences: Strings, Lists, and Files",
            "Chapter 6: Defining Functions",
            "Chapter 7: Decision Structures",
            "Chapter 8: Loop Structures and Booleans",
            "Chapter 9: Simulation and Design",
            "Chapter 10: Defining Classes",
            "Chapter 11: Data Collections",
            "Chapter 12: Object-Oriented Design",
        ],
        total_pages=552,
        url="https://fbeedle.com/our-books/13-python-programming-702.html",
    )

    # --- Readings (from textbook) ---
    def make_reading(chapters: str, week: int) -> WorkRequirement:
        """Helper to create reading requirements."""
        return WorkRequirement(
            ref=WorkRequirementRef(
                course_ref=course_ref,
                req_type=WorkRequirementType.READING,
                identifier=f"reading-week{week}",
            ),
            title=f"Reading: {chapters}",
            description=f"Complete readings from textbook: {chapters}",
            weight_percent=0,  # Readings not graded directly
            estimated_hours=3.0,
            textbook_readings=[(zelle_textbook.ref, chapters)],
            due_week=week,
        )

    readings = [
        make_reading("Chapters 1-3", week=2),
        make_reading("Chapters 4-5", week=4),
        make_reading("Chapters 6-7", week=6),
        make_reading("Chapters 8-9", week=8),
        make_reading("Chapters 10-11", week=10),
        make_reading("Chapter 12", week=12),
    ]

    # --- Assignments ---
    def make_assignment(num: int, title: str, week: int, prereq_reading_idx: int) -> WorkRequirement:
        """Helper to create assignments."""
        deps = [readings[prereq_reading_idx].ref] if prereq_reading_idx >= 0 else []
        return WorkRequirement(
            ref=WorkRequirementRef(
                course_ref=course_ref,
                req_type=WorkRequirementType.ASSIGNMENT,
                identifier=f"a{num}",
            ),
            title=f"Assignment {num}: {title}",
            description=f"Programming assignment covering {title.lower()}",
            weight_percent=5.0,  # Each assignment worth 5%
            estimated_hours=8.0,
            depends_on=deps,
            due_week=week,
        )

    assignments = [
        make_assignment(1, "Variables and Expressions", week=3, prereq_reading_idx=0),
        make_assignment(2, "Graphics and Objects", week=5, prereq_reading_idx=1),
        make_assignment(3, "Functions", week=7, prereq_reading_idx=2),
        make_assignment(4, "Loops and Conditionals", week=9, prereq_reading_idx=3),
        make_assignment(5, "Classes and Objects", week=11, prereq_reading_idx=4),
    ]

    # --- Labs ---
    def make_lab(num: int, topic: str, week: int) -> WorkRequirement:
        """Helper to create labs."""
        return WorkRequirement(
            ref=WorkRequirementRef(
                course_ref=course_ref,
                req_type=WorkRequirementType.LAB,
                identifier=f"lab{num}",
            ),
            title=f"Lab {num}: {topic}",
            description=f"Hands-on lab exercise: {topic}",
            weight_percent=2.0,  # Each lab worth 2%
            estimated_hours=2.0,
            due_week=week,
        )

    labs = [
        make_lab(1, "Python Setup and Basics", week=1),
        make_lab(2, "Variables and Input/Output", week=2),
        make_lab(3, "Graphics Programming", week=4),
        make_lab(4, "Functions and Decomposition", week=6),
        make_lab(5, "Conditionals", week=7),
        make_lab(6, "Loops", week=8),
        make_lab(7, "Lists and Strings", week=9),
        make_lab(8, "File I/O", week=10),
        make_lab(9, "Classes", week=11),
        make_lab(10, "Review and Practice", week=12),
    ]

    # --- Midterm ---
    midterm = FinalExam(
        ref=ExamRef(course_ref=course_ref, exam_type="midterm"),
        title="Midterm Examination",
        description="Covers Chapters 1-7: basics, graphics, functions, conditionals",
        weight_percent=20.0,
        duration_minutes=90,
        is_cumulative=False,
        has_multiple_choice=True,
        has_short_answer=True,
        has_coding_problems=True,
        required_work=[
            assignments[0].ref,
            assignments[1].ref,
            assignments[2].ref,
            labs[0].ref,
            labs[1].ref,
            labs[2].ref,
            labs[3].ref,
            labs[4].ref,
        ],
        topics=["Variables", "Expressions", "Graphics", "Functions", "Conditionals"],
        textbook_coverage=[(zelle_textbook.ref, "Chapters 1-7")],
        exam_period="October 2025",
    )

    # --- Final Exam ---
    final_exam = FinalExam(
        ref=ExamRef(course_ref=course_ref, exam_type="final"),
        title="Final Examination",
        description="Cumulative exam covering all course material",
        weight_percent=35.0,
        duration_minutes=180,
        is_cumulative=True,
        has_multiple_choice=True,
        has_short_answer=True,
        has_coding_problems=True,
        required_work=[
            a.ref for a in assignments
        ] + [
            l.ref for l in labs
        ] + [
            midterm.ref,
        ],
        topics=[
            "Variables and Expressions",
            "Graphics and Objects",
            "Functions",
            "Decision Structures",
            "Loop Structures",
            "Strings and Lists",
            "File I/O",
            "Classes and OOP",
            "Design and Testing",
        ],
        textbook_coverage=[(zelle_textbook.ref, "All Chapters (1-12)")],
        exam_period="December 2025",
        min_grade_percent=40.0,  # Must pass exam to pass course
    )

    # --- Assemble Course Completion ---
    return CourseCompletion(
        course_ref=course_ref,
        course_title="Introduction to Computer Science",
        required_textbooks=[zelle_textbook],
        assignments=assignments,
        labs=labs,
        readings=readings,
        midterms=[midterm],
        final_exam=final_exam,
    )


def create_cmpt145_completion() -> CourseCompletion:
    """
    Create a complete course model for CMPT 145 - Principles of Computer Science.

    Builds on CMPT 141, demonstrating prerequisite relationships.
    """
    course_ref = CourseReference(institution="usask", code="CMPT 145")

    # Different textbook for data structures
    textbook = Textbook(
        ref=TextbookReference(isbn="9780134855684"),
        title="Data Structures and Algorithms in Python",
        authors=["Michael T. Goodrich", "Roberto Tamassia", "Michael H. Goldwasser"],
        edition="1st",
        publisher="Wiley",
        year=2013,
        material_type=MaterialType.TEXTBOOK,
        chapters=[
            "Chapter 1: Python Primer",
            "Chapter 2: Object-Oriented Programming",
            "Chapter 3: Algorithm Analysis",
            "Chapter 4: Recursion",
            "Chapter 5: Array-Based Sequences",
            "Chapter 6: Stacks, Queues, and Deques",
            "Chapter 7: Linked Lists",
            "Chapter 8: Trees",
        ],
        total_pages=748,
    )

    # Simplified - just show the final exam as terminal node
    assignments = [
        WorkRequirement(
            ref=WorkRequirementRef(course_ref, WorkRequirementType.ASSIGNMENT, f"a{i}"),
            title=f"Assignment {i}",
            weight_percent=6.0,
            estimated_hours=10.0,
            due_week=i * 2 + 1,
        )
        for i in range(1, 6)
    ]

    final_exam = FinalExam(
        ref=ExamRef(course_ref=course_ref, exam_type="final"),
        title="Final Examination",
        description="Comprehensive exam on data structures and algorithms",
        weight_percent=40.0,
        duration_minutes=180,
        is_cumulative=True,
        has_coding_problems=True,
        has_proofs=True,
        required_work=[a.ref for a in assignments],
        topics=["Recursion", "Algorithm Analysis", "Stacks", "Queues", "Linked Lists", "Trees"],
        textbook_coverage=[(textbook.ref, "All Chapters")],
        exam_period="December 2025",
    )

    return CourseCompletion(
        course_ref=course_ref,
        course_title="Principles of Computer Science",
        required_textbooks=[textbook],
        assignments=assignments,
        final_exam=final_exam,
    )


def get_sample_completions() -> list[CourseCompletion]:
    """Get all sample course completions."""
    return [
        create_cmpt141_completion(),
        create_cmpt145_completion(),
    ]


if __name__ == "__main__":
    # Demo: Print the dependency graph for CMPT 141
    completion = create_cmpt141_completion()

    print(f"Course: {completion.course_title}")
    print(f"Course ID: {completion.course_ref}")
    print()

    print("Required Textbooks:")
    for tb in completion.required_textbooks:
        print(f"  - {tb}")
    print()

    print(f"Work Requirements ({len(completion.all_work_requirements)} total):")
    print(f"  - {len(completion.assignments)} assignments ({sum(a.weight_percent for a in completion.assignments)}%)")
    print(f"  - {len(completion.labs)} labs ({sum(l.weight_percent for l in completion.labs)}%)")
    print(f"  - {len(completion.readings)} readings")
    print()

    print("Exams:")
    for exam in completion.all_exams:
        print(f"  - {exam.title}: {exam.weight_percent}% (depends on {len(exam.required_work)} work items)")
    print()

    print("Final Exam (Terminal Node):")
    if completion.final_exam:
        print(f"  Title: {completion.final_exam.title}")
        print(f"  Weight: {completion.final_exam.weight_percent}%")
        print(f"  Duration: {completion.final_exam.duration_minutes} minutes")
        print(f"  Prerequisites: {len(completion.final_exam.required_work)} work requirements")
        print(f"  Topics: {', '.join(completion.final_exam.topics[:5])}...")
    print()

    print("Dependency Graph (work → exam):")
    graph = completion.build_dependency_graph()
    for node, deps in sorted(graph.items()):
        if deps:
            print(f"  {node}")
            for d in deps[:3]:
                print(f"    ← {d}")
            if len(deps) > 3:
                print(f"    ... and {len(deps) - 3} more")

    # Validate weights
    issues = completion.validate_weights()
    if issues:
        print("\nWeight validation issues:")
        for issue in issues:
            print(f"  ⚠ {issue}")
    else:
        print("\n✓ Weights sum to 100%")
