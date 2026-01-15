#!/usr/bin/env python3
"""
Export REAL course data to graph-data.json for visualizations.
NO hardcoded degree models - only real API/scraped data.

Supports extended graph with:
- Courses (existing)
- Textbooks / Open educational resources (OER)
- Learning concepts
- Textbook sections
- Work requirements
- Exams as terminal nodes
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from devvyn.institutions.registry import get_registry
from devvyn.institutions.transfers import get_all_agreements, COURSE_CONTENT_SIMILARITIES
from devvyn.sources.openstax import (
    OpenStaxClient,
    get_chapters_for_book,
    KNOWN_CHAPTERS,
)
from devvyn.model.concepts import get_seed_concepts
from devvyn.model.course_materials import TextbookSection, TextbookReference


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

    # Load OpenStax textbooks
    print("Loading OpenStax textbooks...")
    textbook_count = 0
    section_count = 0
    try:
        async with OpenStaxClient() as client:
            books = await client.get_relevant_books()
            for book in books:
                # Use slug as ISBN-like identifier for OER
                book_id = f"openstax:{book.slug}"
                nodes.append({
                    "id": book_id,
                    "label": book.title[:30],
                    "title": book.title,
                    "type": "textbook",
                    "source": "openstax",
                    "subject": book.subject,
                    "is_free": True,
                    "license": book.license,
                    "url": book.source_url,
                })
                textbook_count += 1

                # Add sections for books with known chapter data
                chapters = get_chapters_for_book(book.slug)
                for chapter in chapters:
                    section_id = f"{book_id}:ch{chapter.number}"
                    nodes.append({
                        "id": section_id,
                        "label": f"Ch.{chapter.number}: {chapter.title[:20]}",
                        "title": f"Chapter {chapter.number}: {chapter.title}",
                        "type": "section",
                        "textbook": book_id,
                        "chapter": chapter.number,
                        "topics": chapter.sections,
                        "estimated_minutes": chapter.estimated_minutes,
                    })
                    section_count += 1

                    # Link section to textbook
                    links.append({
                        "source": book_id,
                        "target": section_id,
                        "type": "contains",
                    })

        print(f"  {textbook_count} textbooks, {section_count} sections")
    except Exception as e:
        print(f"  OpenStax: error - {e}")

    # Load learning concepts
    print("Loading learning concepts...")
    concepts = get_seed_concepts()
    for concept in concepts:
        nodes.append({
            "id": f"concept:{concept.id}",
            "label": concept.name,
            "title": concept.description,
            "type": "concept",
            "subject": concept.subject,
            "level": concept.level,
            "aliases": concept.aliases,
        })
    print(f"  {len(concepts)} concepts")

    # Link sections to concepts they teach (based on topic matching)
    concept_links = 0
    concept_map = {c.id: c for c in concepts}
    for node in nodes:
        if node.get("type") == "section" and "topics" in node:
            for topic in node["topics"]:
                # Try to match topic to concept
                topic_normalized = topic.lower().replace(" ", "-")
                if topic_normalized in concept_map:
                    links.append({
                        "source": node["id"],
                        "target": f"concept:{topic_normalized}",
                        "type": "teaches_concept",
                    })
                    concept_links += 1
                else:
                    # Fuzzy match: check if topic is in concept name/aliases
                    for concept in concepts:
                        if concept.matches(topic):
                            links.append({
                                "source": node["id"],
                                "target": f"concept:{concept.id}",
                                "type": "teaches_concept",
                            })
                            concept_links += 1
                            break
    print(f"  {concept_links} section→concept links")

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

    # Count by type
    node_counts = {}
    for node in nodes:
        t = node.get("type", "unknown")
        node_counts[t] = node_counts.get(t, 0) + 1

    link_counts = {}
    for link in valid_links:
        t = link.get("type", "unknown")
        link_counts[t] = link_counts.get(t, 0) + 1

    print(f"\nExported {len(nodes)} nodes and {len(valid_links)} links to {output}")
    print("Nodes:")
    for t, count in sorted(node_counts.items()):
        print(f"  - {count} {t}s")
    print("Links:")
    for t, count in sorted(link_counts.items()):
        print(f"  - {count} {t}")


if __name__ == "__main__":
    asyncio.run(export_graph_data())
