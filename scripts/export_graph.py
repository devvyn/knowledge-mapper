#!/usr/bin/env python3
"""
Export REAL course data to graph-data.json for visualizations.
NO hardcoded degree models - only real API/scraped data.

Supports extended graph with:
- Courses (existing)
- Textbooks (new)
- Work requirements (new)
- Exams as terminal nodes (new)
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

    # Add course completion data (textbooks, work requirements, exams)
    print("Loading course completion data...")
    try:
        from devvyn.data.sample_course_completion import get_sample_completions

        completions = get_sample_completions()
        textbook_count = 0
        work_count = 0
        exam_count = 0

        for completion in completions:
            course_id = f"{completion.course_ref.institution}:{completion.course_ref.code}"

            # Add textbooks
            for textbook in completion.required_textbooks + completion.recommended_textbooks:
                tb_id = str(textbook.ref)
                nodes.append({
                    "id": tb_id,
                    "label": textbook.title[:30] + "..." if len(textbook.title) > 30 else textbook.title,
                    "title": str(textbook),
                    "type": "textbook",
                    "isbn": textbook.isbn,
                    "authors": textbook.authors,
                })
                textbook_count += 1

                # Link course to textbook
                links.append({
                    "source": course_id,
                    "target": tb_id,
                    "type": "uses_textbook",
                })

            # Add work requirements
            for work in completion.all_work_requirements:
                work_id = str(work.ref)
                nodes.append({
                    "id": work_id,
                    "label": work.title,
                    "title": work.description,
                    "type": "work_requirement",
                    "work_type": work.req_type.value,
                    "weight": work.weight_percent,
                    "course": course_id,
                    "institution": completion.course_ref.institution,
                })
                work_count += 1

                # Add dependency links
                for dep in work.depends_on:
                    links.append({
                        "source": str(dep),
                        "target": work_id,
                        "type": "depends_on",
                    })

            # Add exams (including midterms and final)
            for exam in completion.all_exams:
                exam_id = str(exam.ref)
                nodes.append({
                    "id": exam_id,
                    "label": exam.title,
                    "title": exam.description,
                    "type": "exam",
                    "weight": exam.weight_percent,
                    "duration_minutes": exam.duration_minutes,
                    "course": course_id,
                    "institution": completion.course_ref.institution,
                })
                exam_count += 1

                # Add links from work requirements to exam
                for work_ref in exam.required_work:
                    links.append({
                        "source": str(work_ref),
                        "target": exam_id,
                        "type": "leads_to_exam",
                    })

        print(f"  {len(completions)} course completions")
        print(f"  {textbook_count} textbooks")
        print(f"  {work_count} work requirements")
        print(f"  {exam_count} exams (terminal nodes)")
    except ImportError:
        print("  (sample data not available)")
    except Exception as e:
        print(f"  Error: {e}")

    # Filter out links referencing missing nodes
    node_ids = set(n["id"] for n in nodes)
    valid_links = []
    for link in links:
        if link["source"] in node_ids and link["target"] in node_ids:
            valid_links.append(link)

    # Count node types
    course_nodes = len([n for n in nodes if n.get("type") == "course"])
    textbook_nodes = len([n for n in nodes if n.get("type") == "textbook"])
    work_nodes = len([n for n in nodes if n.get("type") == "work_requirement"])
    exam_nodes = len([n for n in nodes if n.get("type") == "exam"])

    data = {
        "nodes": nodes,
        "links": valid_links,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nExported {len(nodes)} nodes and {len(valid_links)} links to {output}")
    print(f"  - {course_nodes} courses (REAL DATA)")
    print(f"  - {textbook_nodes} textbooks")
    print(f"  - {work_nodes} work requirements")
    print(f"  - {exam_nodes} exams (terminal nodes)")
    print(f"  - {len([l for l in valid_links if l['type'] == 'prerequisite'])} prerequisites")
    print(f"  - {len([l for l in valid_links if l['type'] == 'transfer'])} transfers")
    print(f"  - {len([l for l in valid_links if l['type'] == 'leads_to_exam'])} exam dependencies")


if __name__ == "__main__":
    asyncio.run(export_graph_data())
