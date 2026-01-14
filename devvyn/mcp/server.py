"""
Saskatchewan Post-Secondary MCP Server.

Provides tools for querying:
- Course information across institutions
- Prerequisite relationships
- Transfer credit pathways
- "What can I take next?" recommendations
"""
import asyncio
from typing import Optional

from mcp.server.fastmcp import FastMCP

from devvyn.institutions.base import CourseReference, UnifiedCourse
from devvyn.institutions.registry import get_registry
from devvyn.institutions.transfers import (
    get_all_agreements,
    get_agreements_from,
    get_agreements_to,
    describe_transfer_path,
    COURSE_CONTENT_SIMILARITIES,
    COURSE_CONTENT_SIMILARITIES_UREGINA,
)
from devvyn.graph.unified import UnifiedPrerequisiteGraph, build_unified_graph
from devvyn.query import (
    build_saskatoon_graph,
    what_can_i_take_after,
    pathway_to_degree,
)

# Initialize MCP server
mcp = FastMCP("saskatchewan-postsecondary")

# Cached graph (built lazily)
_graph: Optional[UnifiedPrerequisiteGraph] = None


async def get_graph() -> UnifiedPrerequisiteGraph:
    """Get or build the unified prerequisite graph."""
    global _graph
    if _graph is None:
        _graph = await build_saskatoon_graph()
    return _graph


# =============================================================================
# Course Lookup Tools
# =============================================================================

@mcp.tool()
async def sk_course(institution: str, code: str) -> str:
    """
    Look up a course by institution and code.

    Args:
        institution: Institution ID (usask, saskpolytech, uregina)
        code: Course code (e.g., "CMPT 141", "COSC 180")

    Returns:
        Course details including title, credits, prerequisites, and what it unlocks.
    """
    graph = await get_graph()
    ref = CourseReference(institution.lower(), code.upper())
    course = graph.get_course(ref)

    if not course:
        return f"Course not found: {ref}"

    lines = [
        f"# {course.code}",
        f"**{course.title}**",
        f"Institution: {course.ref.institution}",
        f"Credits: {course.credits}",
    ]

    if course.description:
        lines.append(f"\n{course.description[:500]}...")

    # Prerequisites
    prereqs = graph.prerequisites_for(ref, transitive=False)
    if prereqs:
        lines.append(f"\n**Prerequisites:** {', '.join(str(p) for p in sorted(prereqs, key=str))}")

    # What it unlocks
    unlocks = graph.unlocks(ref, transitive=False)
    if unlocks:
        lines.append(f"\n**Unlocks:** {', '.join(str(u) for u in sorted(unlocks, key=str))}")

    # Equivalencies
    equivs = graph.equivalents(ref)
    if equivs:
        lines.append(f"\n**Transfer equivalents:** {', '.join(str(e) for e in equivs)}")

    return "\n".join(lines)


@mcp.tool()
async def sk_courses_by_subject(institution: str, subject: str) -> str:
    """
    List all courses for a subject at an institution.

    Args:
        institution: Institution ID (usask, saskpolytech)
        subject: Subject code (e.g., "CMPT", "MATH", "COSC")

    Returns:
        List of courses with codes and titles.
    """
    registry = get_registry()
    adapter = registry.get(institution.lower())

    if not adapter:
        return f"Unknown institution: {institution}. Known: {', '.join(registry.ids())}"

    async with adapter:
        courses = await adapter.get_courses_by_subject(subject.upper())

    if not courses:
        return f"No courses found for {subject} at {institution}"

    lines = [f"# {subject.upper()} courses at {institution}"]
    for course in sorted(courses, key=lambda c: c.code):
        lines.append(f"- **{course.code}**: {course.title}")

    return "\n".join(lines)


# =============================================================================
# Transfer Pathway Tools
# =============================================================================

@mcp.tool()
async def sk_transfer_pathways(
    from_program: Optional[str] = None,
    from_institution: str = "saskpolytech",
    to_institution: Optional[str] = None,
) -> str:
    """
    List transfer pathways between institutions.

    Args:
        from_program: Source program code (e.g., "CSTDP"). If not specified, lists all.
        from_institution: Source institution (default: saskpolytech)
        to_institution: Target institution filter (optional)

    Returns:
        Available transfer pathways with credit details.
    """
    agreements = get_all_agreements()

    # Filter by source institution
    agreements = [a for a in agreements if a.source_institution == from_institution.lower()]

    # Filter by program if specified
    if from_program:
        agreements = [a for a in agreements if a.source_program == from_program.upper()]

    # Filter by target institution if specified
    if to_institution:
        agreements = [a for a in agreements if a.target_institution == to_institution.lower()]

    if not agreements:
        return "No matching transfer pathways found."

    lines = ["# Transfer Pathways"]
    for a in agreements:
        lines.append(f"\n## {a.source_program} → {a.target_program}")
        lines.append(f"- **From:** {a.source_institution}")
        lines.append(f"- **To:** {a.target_institution}")
        lines.append(f"- **Credits transferred:** {a.total_credits}")
        if a.url:
            lines.append(f"- **Source:** {a.url}")
        if a.notes:
            # Truncate long notes
            notes = a.notes.strip()[:500]
            lines.append(f"\n{notes}")

    return "\n".join(lines)


@mcp.tool()
async def sk_pathway_details(
    program: str,
    from_institution: str = "saskpolytech",
    to_institution: str = "usask",
) -> str:
    """
    Get detailed transfer pathway information.

    Args:
        program: Source program code (e.g., "CSTDP")
        from_institution: Source institution
        to_institution: Target institution

    Returns:
        Detailed pathway including courses granted and requirements.
    """
    return describe_transfer_path(
        program.upper(),
        from_institution.lower(),
        to_institution.lower(),
    )


# =============================================================================
# Prerequisite & Planning Tools
# =============================================================================

@mcp.tool()
async def sk_prerequisites(
    institution: str,
    code: str,
    include_transitive: bool = True,
) -> str:
    """
    Get prerequisites for a course.

    Args:
        institution: Institution ID
        code: Course code
        include_transitive: If True, include prerequisites of prerequisites

    Returns:
        List of prerequisite courses.
    """
    graph = await get_graph()
    ref = CourseReference(institution.lower(), code.upper())

    prereqs = graph.prerequisites_for(ref, transitive=include_transitive)

    if not prereqs:
        return f"{ref} has no prerequisites."

    lines = [f"# Prerequisites for {ref}"]
    if include_transitive:
        lines.append("(includes transitive prerequisites)")

    for p in sorted(prereqs, key=str):
        course = graph.get_course(p)
        title = course.title if course else "Unknown"
        lines.append(f"- **{p}**: {title}")

    return "\n".join(lines)


@mcp.tool()
async def sk_what_next(
    completed: list[str],
    target_institution: Optional[str] = None,
) -> str:
    """
    Find courses available after completing given courses.

    Args:
        completed: List of completed course codes (e.g., ["usask:CMPT 141", "MATH 110"])
        target_institution: Optional filter for which institution's courses to show

    Returns:
        Courses whose prerequisites are now satisfied.
    """
    graph = await get_graph()
    available = what_can_i_take_after(graph, completed, target_institution)

    if not available:
        return "No additional courses available with current prerequisites."

    lines = [f"# Courses Now Available ({len(available)} total)"]
    if target_institution:
        lines.append(f"Filtered to: {target_institution}")

    for course in sorted(available, key=lambda c: c.code)[:25]:
        lines.append(f"- **{course.code}**: {course.title}")

    if len(available) > 25:
        lines.append(f"\n... and {len(available) - 25} more")

    return "\n".join(lines)


@mcp.tool()
async def sk_path_to(
    target_institution: str,
    target_code: str,
    from_institution: Optional[str] = None,
) -> str:
    """
    Find paths from entry-level courses to a target course.

    Args:
        target_institution: Institution of target course
        target_code: Target course code
        from_institution: Starting institution (optional, defaults to same as target)

    Returns:
        Possible prerequisite chains to reach the target course.
    """
    graph = await get_graph()
    target = CourseReference(target_institution.lower(), target_code.upper())
    start_inst = from_institution.lower() if from_institution else target_institution.lower()

    paths = graph.find_paths(start_inst, target, max_depth=8)

    if not paths:
        return f"No paths found to {target} from {start_inst}"

    lines = [f"# Paths to {target}"]
    lines.append(f"Starting from entry-level courses at {start_inst}")

    # Show shortest paths first
    paths.sort(key=len)
    for i, path in enumerate(paths[:5]):
        lines.append(f"\n**Path {i+1}** ({len(path)} courses):")
        for ref in path:
            course = graph.get_course(ref)
            title = course.title if course else ""
            lines.append(f"  → {ref}: {title}")

    if len(paths) > 5:
        lines.append(f"\n... and {len(paths) - 5} more paths")

    return "\n".join(lines)


# =============================================================================
# Overview Tools
# =============================================================================

@mcp.tool()
async def sk_institutions() -> str:
    """
    List all known Saskatchewan post-secondary institutions.

    Returns:
        Institutions with their coverage status.
    """
    registry = get_registry()

    lines = ["# Saskatchewan Post-Secondary Institutions"]
    lines.append("\n## Fully Integrated (course data + prerequisites)")
    for adapter in registry:
        lines.append(f"- **{adapter.name}** (`{adapter.id}`): {adapter.location}")

    lines.append("\n## Transfer Pathways Only (no course data)")
    lines.append("- **University of Regina** (`uregina`): Regina, SK")
    lines.append("  - Banner system requires authentication")
    lines.append("  - Transfer agreements from SaskPolytech documented")

    lines.append("\n## Not Yet Covered")
    lines.append("- Saskatchewan Indian Institute of Technologies (SIIT)")
    lines.append("- Great Plains College")
    lines.append("- Carlton Trail College")
    lines.append("- Other regional colleges")

    return "\n".join(lines)


@mcp.tool()
async def sk_stats() -> str:
    """
    Get statistics about the knowledge base.

    Returns:
        Course counts, transfer pathways, and coverage info.
    """
    graph = await get_graph()
    stats = graph.stats()
    agreements = get_all_agreements()

    lines = ["# Saskatchewan Post-Secondary Knowledge Base"]
    lines.append(f"\n**Total courses:** {stats['total_courses']}")
    lines.append(f"**Prerequisite relationships:** {stats['total_edges']}")
    lines.append(f"**Transfer equivalencies:** {stats['total_equivalencies']}")
    lines.append(f"**Transfer agreements:** {len(agreements)}")

    lines.append("\n## Courses by Institution")
    for inst, count in sorted(stats['institutions'].items()):
        lines.append(f"- {inst}: {count} courses")

    lines.append("\n## Transfer Pathways")
    for a in agreements:
        lines.append(f"- {a.source_institution}:{a.source_program} → {a.target_institution} ({a.total_credits} credits)")

    return "\n".join(lines)


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
