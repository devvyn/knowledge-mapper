"""
High-level queries across institutions.

This is the main entry point for cross-institution educational data queries.
"""
import asyncio
from dataclasses import dataclass
from typing import Optional

from devvyn.institutions.base import CourseReference, UnifiedCourse
from devvyn.institutions.registry import get_registry
from devvyn.institutions.transfers import (
    add_transfer_equivalencies,
    describe_transfer_path,
    get_agreements_from,
)
from devvyn.graph.unified import (
    UnifiedPrerequisiteGraph,
    build_unified_graph,
)


@dataclass
class PathwayResult:
    """Result of a pathway query."""
    source_institution: str
    source_program: str
    target_institution: str
    target_courses: list[str]
    total_credits: float
    description: str


async def build_saskatoon_graph() -> UnifiedPrerequisiteGraph:
    """
    Build a unified graph for Saskatoon post-secondary institutions.

    Includes:
    - USask Computer Science courses
    - SaskPolytech Computer Systems Technology
    - Transfer credit equivalencies
    """
    graph = await build_unified_graph(
        subjects={"usask": ["CMPT", "MATH"]},
        programs={"saskpolytech": ["CSTDP", "CENGDIPFD"]},
    )

    # Add transfer credit equivalencies
    add_transfer_equivalencies(graph)

    return graph


def build_saskatoon_graph_sync() -> UnifiedPrerequisiteGraph:
    """Synchronous wrapper for build_saskatoon_graph."""
    return asyncio.run(build_saskatoon_graph())


def what_can_i_take_after(
    graph: UnifiedPrerequisiteGraph,
    completed_courses: list[str],
    institution: Optional[str] = None
) -> list[UnifiedCourse]:
    """
    Find courses that can be taken after completing given courses.

    Args:
        graph: Unified prerequisite graph
        completed_courses: List of course codes (e.g., ["usask:CMPT 141", "saskpolytech:COSC 180"])
        institution: Optional filter for target institution

    Returns:
        List of courses whose prerequisites are satisfied
    """
    # Parse completed courses into references
    completed_refs = set()
    for code in completed_courses:
        if ":" in code:
            completed_refs.add(CourseReference.parse(code))
        else:
            # Assume we need to guess the institution
            for ref in graph.courses:
                if ref.code == code.upper():
                    completed_refs.add(ref)

    # Add equivalencies
    all_completed = completed_refs.copy()
    for ref in completed_refs:
        all_completed.update(graph.equivalents(ref))

    # Find courses whose prerequisites are satisfied
    available = []
    for ref in graph.courses:
        if institution and ref.institution != institution:
            continue
        if ref in all_completed:
            continue  # Already completed

        prereqs = graph.prerequisites_for(ref, transitive=False)
        if prereqs and prereqs.issubset(all_completed):
            course = graph.get_course(ref)
            if course:
                available.append(course)

    return available


def pathway_to_degree(
    source_program: str,
    source_institution: str = "saskpolytech",
    target_institution: str = "usask"
) -> PathwayResult:
    """
    Describe the pathway from a diploma/certificate to a degree.

    Args:
        source_program: Program code (e.g., "CSTDP")
        source_institution: Source institution
        target_institution: Target institution

    Returns:
        PathwayResult with transfer details
    """
    agreements = get_agreements_from(source_institution)
    matching = [
        a for a in agreements
        if a.source_program == source_program
        and a.target_institution == target_institution
    ]

    if not matching:
        return PathwayResult(
            source_institution=source_institution,
            source_program=source_program,
            target_institution=target_institution,
            target_courses=[],
            total_credits=0.0,
            description=f"No transfer agreement found for {source_program}",
        )

    agreement = matching[0]
    target_courses = [
        equiv.course_to.code for equiv in agreement.course_equivalencies
    ]

    return PathwayResult(
        source_institution=source_institution,
        source_program=source_program,
        target_institution=target_institution,
        target_courses=target_courses,
        total_credits=agreement.total_credits,
        description=describe_transfer_path(source_program, source_institution, target_institution),
    )


async def demo():
    """Demonstrate cross-institution queries."""
    print("=" * 60)
    print("SASKATOON POST-SECONDARY KNOWLEDGE MAP")
    print("=" * 60)

    print("\n[Building unified graph...]")
    graph = await build_saskatoon_graph()
    stats = graph.stats()
    print(f"Loaded {stats['total_courses']} courses from {len(stats['institutions'])} institutions")
    print(f"  USask: {stats['institutions'].get('usask', 0)} courses")
    print(f"  SaskPolytech: {stats['institutions'].get('saskpolytech', 0)} courses")
    print(f"  Transfer equivalencies: {stats['total_equivalencies']}")

    # Query 1: Transfer pathway
    print("\n" + "=" * 60)
    print("QUERY: What's the pathway from SaskPolytech CST to USask CS?")
    print("=" * 60)
    pathway = pathway_to_degree("CSTDP", "saskpolytech", "usask")
    print(f"\nTransfer credits: {pathway.total_credits}")
    print(f"USask courses granted: {', '.join(pathway.target_courses)}")

    # Query 2: Prerequisites with cross-institution context
    print("\n" + "=" * 60)
    print("QUERY: What USask courses can I take after SaskPolytech CST?")
    print("=" * 60)

    # After completing CST, you have equivalency for CMPT 141, 145, 214, 270, 350, 355
    cst_grants = ["usask:CMPT 141", "usask:CMPT 145", "usask:CMPT 214",
                  "usask:CMPT 270", "usask:CMPT 350", "usask:CMPT 355"]

    available = what_can_i_take_after(graph, cst_grants, institution="usask")
    print(f"\nWith CST transfer credits, you can take {len(available)} USask courses:")
    for course in sorted(available, key=lambda c: c.code)[:15]:
        print(f"  {course.code}: {course.title}")
    if len(available) > 15:
        print(f"  ... and {len(available) - 15} more")

    # Query 3: What does a specific course unlock across institutions?
    print("\n" + "=" * 60)
    print("QUERY: What does CMPT 270 unlock (including via transfer)?")
    print("=" * 60)

    ref = CourseReference("usask", "CMPT 270")
    unlocks = graph.unlocks(ref, cross_institution=True)
    print(f"\nCMPT 270 unlocks {len(unlocks)} courses:")
    by_inst = {}
    for u in unlocks:
        if u.institution not in by_inst:
            by_inst[u.institution] = []
        by_inst[u.institution].append(u.code)

    for inst, codes in sorted(by_inst.items()):
        print(f"  {inst}: {', '.join(sorted(codes)[:8])}")

    # Query 4: Entry points comparison
    print("\n" + "=" * 60)
    print("QUERY: Entry-level programming courses at each institution")
    print("=" * 60)

    for inst_id in ["usask", "saskpolytech"]:
        entry = [
            ref for ref in graph.courses_at(inst_id)
            if not graph.prerequisites_for(ref, transitive=False)
        ]
        programming = [
            ref for ref in entry
            if any(kw in (graph.get_course(ref).title or "").lower()
                   for kw in ["programming", "computer", "intro"])
        ]
        print(f"\n{inst_id}:")
        for ref in sorted(programming, key=lambda r: r.code)[:5]:
            course = graph.get_course(ref)
            if course:
                print(f"  {ref.code}: {course.title}")


if __name__ == "__main__":
    asyncio.run(demo())
