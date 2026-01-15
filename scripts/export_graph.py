#!/usr/bin/env python3
"""
Export REAL course data to graph-data.json for visualizations.
NO hardcoded degree models - only real API/scraped data.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from devvyn.institutions.registry import get_registry
from devvyn.institutions.transfers import get_all_agreements, COURSE_CONTENT_SIMILARITIES


async def export_graph_data(output_path: str = "viz/graph-data.json"):
    """Export all courses and prerequisites to JSON for D3 visualizations."""
    nodes = []
    links = []
    seen_courses = set()

    registry = get_registry()

    # Load USask courses
    print("Loading USask courses...")
    usask = registry.get("usask")
    if usask:
        async with usask:
            # Load common subjects
            subjects = ["CMPT", "MATH", "STAT", "PHYS", "CHEM", "BIOL", "ENG", "PHIL"]
            for subject in subjects:
                try:
                    courses = await usask.get_courses_by_subject(subject)
                    print(f"  {subject}: {len(courses)} courses")
                    for course in courses:
                        course_id = f"{course.ref.institution}:{course.ref.code}"
                        if course_id not in seen_courses:
                            seen_courses.add(course_id)
                            nodes.append({
                                "id": course_id,
                                "label": course.ref.code,
                                "title": course.title or course.ref.code,
                                "institution": course.ref.institution,
                                "credits": course.credits or 3.0,
                                "type": "course",
                                "subject": subject,
                            })

                            # Add prerequisite links
                            for prereq in course.prerequisites:
                                prereq_id = f"{prereq.institution}:{prereq.code}"
                                links.append({
                                    "source": prereq_id,
                                    "target": course_id,
                                    "type": "prerequisite",
                                })
                except Exception as e:
                    print(f"  {subject}: error - {e}")

    # Load SaskPolytech courses
    print("Loading SaskPolytech courses...")
    saskpoly = registry.get("saskpolytech")
    if saskpoly:
        async with saskpoly:
            try:
                program = await saskpoly.get_program("CSTDP")
                if program:
                    print(f"  CSTDP: {len(program.courses)} courses")
                    for course in program.courses:
                        course_id = f"{course.ref.institution}:{course.ref.code}"
                        if course_id not in seen_courses:
                            seen_courses.add(course_id)
                            subject = course.ref.code.split()[0] if course.ref.code else "CST"
                            nodes.append({
                                "id": course_id,
                                "label": course.ref.code,
                                "title": course.title or course.ref.code,
                                "institution": course.ref.institution,
                                "credits": course.credits or 3.0,
                                "type": "course",
                                "subject": subject,
                            })

                            for prereq in course.prerequisites:
                                prereq_id = f"{prereq.institution}:{prereq.code}"
                                links.append({
                                    "source": prereq_id,
                                    "target": course_id,
                                    "type": "prerequisite",
                                })
            except Exception as e:
                print(f"  CSTDP: error - {e}")

    # Add transfer links from course content similarities
    print("Loading transfer equivalencies...")
    try:
        for sp_code, usask_code, notes in COURSE_CONTENT_SIMILARITIES:
            links.append({
                "source": f"saskpolytech:{sp_code}",
                "target": f"usask:{usask_code}",
                "type": "transfer",
            })
        print(f"  {len(COURSE_CONTENT_SIMILARITIES)} transfer equivalencies")
    except Exception as e:
        print(f"  Transfers: error - {e}")

    # Filter out links referencing missing nodes
    node_ids = set(n["id"] for n in nodes)
    valid_links = []
    for link in links:
        if link["source"] in node_ids and link["target"] in node_ids:
            valid_links.append(link)

    data = {
        "nodes": nodes,
        "links": valid_links,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nExported {len(nodes)} nodes and {len(valid_links)} links to {output}")
    print(f"  - {len(nodes)} courses (REAL DATA)")
    print(f"  - {len([l for l in valid_links if l['type'] == 'prerequisite'])} prerequisites")
    print(f"  - {len([l for l in valid_links if l['type'] == 'transfer'])} transfers")
    print(f"  - 0 fake degree models")


if __name__ == "__main__":
    asyncio.run(export_graph_data())
