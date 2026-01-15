#!/usr/bin/env python3
"""
Export course and degree data to graph-data.json for visualizations.
"""
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from devvyn.degrees.usask import get_usask_programs


def export_graph_data(output_path: str = "viz/graph-data.json"):
    """Export all courses and degrees to JSON for D3 visualizations."""
    nodes = []
    links = []
    seen_courses = set()

    programs = get_usask_programs()

    # Add degree nodes
    for prog in programs:
        nodes.append({
            "id": prog.id,
            "label": prog.name.split(" - ")[-1] if " - " in prog.name else prog.name,
            "title": prog.name,
            "institution": prog.institution,
            "credits": prog.total_credits,
            "type": "degree",
            "credential": prog.credential.value,
        })

        # Collect courses from this program
        for course_code in prog.all_possible_courses():
            if course_code not in seen_courses:
                seen_courses.add(course_code)
                # Parse subject from course code
                parts = course_code.split()
                subject = parts[0] if parts else "UNKNOWN"

                nodes.append({
                    "id": f"usask:{course_code}",
                    "label": course_code,
                    "title": course_code,  # Would need API to get real titles
                    "institution": "usask",
                    "credits": 3.0,
                    "type": "course",
                    "subject": subject,
                })

            # Link course to degree
            links.append({
                "source": f"usask:{course_code}",
                "target": prog.id,
                "type": "satisfies",
            })

    # TODO: Add prerequisite links (would need course data)

    data = {
        "nodes": nodes,
        "links": links,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Exported {len(nodes)} nodes and {len(links)} links to {output}")
    print(f"  - {len([n for n in nodes if n['type'] == 'degree'])} degrees")
    print(f"  - {len([n for n in nodes if n['type'] == 'course'])} courses")


if __name__ == "__main__":
    export_graph_data()
