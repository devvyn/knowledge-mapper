#!/usr/bin/env python3
"""
REST API for dynamic graph exploration.
Serves REAL data from USask and SaskPolytech APIs.
NO hardcoded degree models.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify, request
from flask_cors import CORS

from devvyn.institutions.registry import get_registry
from devvyn.institutions.transfers import get_all_agreements

app = Flask(__name__)
CORS(app)

# Cache for loaded data
_cache = {
    "courses": {},  # inst:code -> course dict
    "subjects": {},  # inst -> {subject -> count}
    "prerequisites": [],  # list of {from, to}
    "transfers": [],  # list of transfer pathways
    "textbooks": {},  # isbn -> textbook dict
    "work_requirements": {},  # ref_id -> work requirement dict
    "exams": {},  # ref_id -> exam dict
    "loaded": False,
}


def _load_graph_data():
    """Load course data from graph-data.json as fallback."""
    import json
    graph_path = Path(__file__).parent.parent / "viz" / "graph-data.json"
    if graph_path.exists():
        with open(graph_path) as f:
            return json.load(f)
    return {"nodes": [], "links": []}


def ensure_cache():
    """Ensure cache is populated from real data sources."""
    if _cache["loaded"]:
        return

    # Load from graph-data.json which has real scraped data
    data = _load_graph_data()

    # Process nodes
    subjects_by_inst = {}
    for node in data.get("nodes", []):
        node_type = node.get("type", "course")

        if node_type == "course":
            inst = node.get("institution", "unknown")
            code = node.get("label", "")
            subject = node.get("subject", code.split()[0] if code else "")

            _cache["courses"][node["id"]] = {
                "id": node["id"],
                "code": code,
                "title": node.get("title", code),
                "subject": subject,
                "institution": inst,
                "credits": node.get("credits", 3.0),
            }

            if inst not in subjects_by_inst:
                subjects_by_inst[inst] = {}
            if subject not in subjects_by_inst[inst]:
                subjects_by_inst[inst][subject] = 0
            subjects_by_inst[inst][subject] += 1

        elif node_type == "textbook":
            _cache["textbooks"][node["id"]] = {
                "id": node["id"],
                "isbn": node.get("isbn", ""),
                "title": node.get("title", node.get("label", "")),
                "authors": node.get("authors", []),
            }

        elif node_type == "work_requirement":
            _cache["work_requirements"][node["id"]] = {
                "id": node["id"],
                "title": node.get("label", ""),
                "description": node.get("title", ""),
                "work_type": node.get("work_type", "assignment"),
                "weight": node.get("weight", 0),
                "course": node.get("course", ""),
                "institution": node.get("institution", ""),
            }

        elif node_type == "exam":
            _cache["exams"][node["id"]] = {
                "id": node["id"],
                "title": node.get("label", "Final Examination"),
                "description": node.get("title", ""),
                "weight": node.get("weight", 0),
                "duration_minutes": node.get("duration_minutes", 180),
                "course": node.get("course", ""),
                "institution": node.get("institution", ""),
            }

    _cache["subjects"] = subjects_by_inst

    # Process links (all edge types)
    for link in data.get("links", []):
        link_type = link.get("type", "prerequisite")
        if link_type == "prerequisite":
            _cache["prerequisites"].append({
                "from": link["source"],
                "to": link["target"],
            })

    # Load transfer agreements
    try:
        agreements = get_all_agreements()
        for a in agreements:
            _cache["transfers"].append({
                "from_program": a.source_program,
                "from_institution": a.source_institution,
                "to_institution": a.target_institution,
                "to_program": a.target_program,
                "credits": a.total_credits,
            })
    except Exception:
        pass

    _cache["loaded"] = True


@app.route("/api/institutions")
def list_institutions():
    """List all institutions with course data."""
    ensure_cache()
    institutions = {}
    for course in _cache["courses"].values():
        inst = course["institution"]
        if inst not in institutions:
            institutions[inst] = {"id": inst, "course_count": 0}
        institutions[inst]["course_count"] += 1

    return jsonify(list(institutions.values()))


@app.route("/api/subjects")
def list_subjects():
    """List all subjects with course counts."""
    ensure_cache()
    institution = request.args.get("institution")

    subjects = {}
    for inst, subj_counts in _cache["subjects"].items():
        if institution and inst != institution:
            continue
        for subj, count in subj_counts.items():
            if subj not in subjects:
                subjects[subj] = {"subject": subj, "count": 0, "institutions": []}
            subjects[subj]["count"] += count
            if inst not in subjects[subj]["institutions"]:
                subjects[subj]["institutions"].append(inst)

    return jsonify(sorted(subjects.values(), key=lambda x: -x["count"]))


@app.route("/api/courses")
def list_courses():
    """List courses, optionally filtered."""
    ensure_cache()
    subject = request.args.get("subject")
    institution = request.args.get("institution")

    courses = []
    for course in _cache["courses"].values():
        if subject and course["subject"] != subject.upper():
            continue
        if institution and course["institution"] != institution:
            continue
        courses.append(course)

    return jsonify(sorted(courses, key=lambda x: x["code"]))


@app.route("/api/course/<path:course_id>")
def get_course(course_id: str):
    """Get details for a specific course."""
    ensure_cache()

    # Handle both "usask:CMPT 141" and "CMPT 141" formats
    if ":" not in course_id:
        course_id = f"usask:{course_id}"

    course = _cache["courses"].get(course_id)
    if not course:
        return jsonify({"error": f"Course not found: {course_id}"}), 404

    # Find prerequisites
    prereqs = [p["from"] for p in _cache["prerequisites"] if p["to"] == course_id]

    # Find what this course unlocks
    unlocks = [p["to"] for p in _cache["prerequisites"] if p["from"] == course_id]

    return jsonify({
        **course,
        "prerequisites": prereqs,
        "unlocks": unlocks,
    })


@app.route("/api/prerequisites")
def list_prerequisites():
    """List all prerequisite relationships."""
    ensure_cache()
    institution = request.args.get("institution")

    prereqs = _cache["prerequisites"]
    if institution:
        prereqs = [
            p for p in prereqs
            if institution in p["from"] or institution in p["to"]
        ]

    return jsonify(prereqs)


@app.route("/api/transfers")
def list_transfers():
    """List transfer pathways between institutions."""
    ensure_cache()
    return jsonify(_cache["transfers"])


@app.route("/api/stats")
def get_stats():
    """Get overall statistics."""
    ensure_cache()

    institutions = set()
    subjects = set()
    for course in _cache["courses"].values():
        institutions.add(course["institution"])
        subjects.add(course["subject"])

    return jsonify({
        "courses": len(_cache["courses"]),
        "institutions": len(institutions),
        "subjects": len(subjects),
        "prerequisites": len(_cache["prerequisites"]),
        "transfers": len(_cache["transfers"]),
        "textbooks": len(_cache["textbooks"]),
        "work_requirements": len(_cache["work_requirements"]),
        "exams": len(_cache["exams"]),
    })


# --- Textbook Endpoints ---

@app.route("/api/textbooks")
def list_textbooks():
    """List all textbooks."""
    ensure_cache()
    course_id = request.args.get("course")

    textbooks = list(_cache["textbooks"].values())

    # If filtering by course, find textbooks linked to that course
    if course_id:
        # Would require edge data - for now return all
        pass

    return jsonify(sorted(textbooks, key=lambda x: x.get("title", "")))


@app.route("/api/textbook/<path:textbook_id>")
def get_textbook(textbook_id: str):
    """Get details for a specific textbook."""
    ensure_cache()

    textbook = _cache["textbooks"].get(textbook_id)
    if not textbook:
        return jsonify({"error": f"Textbook not found: {textbook_id}"}), 404

    return jsonify(textbook)


# --- Work Requirement Endpoints ---

@app.route("/api/work-requirements")
def list_work_requirements():
    """List work requirements, optionally filtered by course."""
    ensure_cache()
    course_id = request.args.get("course")
    work_type = request.args.get("type")

    requirements = []
    for req in _cache["work_requirements"].values():
        if course_id and req.get("course") != course_id:
            continue
        if work_type and req.get("work_type") != work_type:
            continue
        requirements.append(req)

    return jsonify(sorted(requirements, key=lambda x: x.get("title", "")))


@app.route("/api/work-requirement/<path:req_id>")
def get_work_requirement(req_id: str):
    """Get details for a specific work requirement."""
    ensure_cache()

    req = _cache["work_requirements"].get(req_id)
    if not req:
        return jsonify({"error": f"Work requirement not found: {req_id}"}), 404

    return jsonify(req)


# --- Exam Endpoints ---

@app.route("/api/exams")
def list_exams():
    """List all exams, optionally filtered."""
    ensure_cache()
    course_id = request.args.get("course")
    institution = request.args.get("institution")

    exams = []
    for exam in _cache["exams"].values():
        if course_id and exam.get("course") != course_id:
            continue
        if institution and exam.get("institution") != institution:
            continue
        exams.append(exam)

    return jsonify(sorted(exams, key=lambda x: x.get("title", "")))


@app.route("/api/exam/<path:exam_id>")
def get_exam(exam_id: str):
    """Get details for a specific exam."""
    ensure_cache()

    exam = _cache["exams"].get(exam_id)
    if not exam:
        return jsonify({"error": f"Exam not found: {exam_id}"}), 404

    # Find dependencies (work requirements that lead to this exam)
    dependencies = []
    # This would require edge data - placeholder for now

    return jsonify({
        **exam,
        "dependencies": dependencies,
    })


# --- Course Completion Endpoint ---

@app.route("/api/course/<path:course_id>/completion")
def get_course_completion(course_id: str):
    """
    Get complete course requirements including textbooks, work, and exams.

    This endpoint returns the full directed graph of what's needed to
    complete a course, with the final exam as the terminal node.
    """
    ensure_cache()

    # Normalize course ID
    if ":" not in course_id:
        course_id = f"usask:{course_id}"

    course = _cache["courses"].get(course_id)
    if not course:
        return jsonify({"error": f"Course not found: {course_id}"}), 404

    # Find associated data
    work_reqs = [
        req for req in _cache["work_requirements"].values()
        if req.get("course") == course_id
    ]

    exams = [
        exam for exam in _cache["exams"].values()
        if exam.get("course") == course_id
    ]

    # Find final exam (terminal node)
    final_exam = None
    midterms = []
    for exam in exams:
        if "final" in exam.get("title", "").lower():
            final_exam = exam
        else:
            midterms.append(exam)

    return jsonify({
        "course": course,
        "work_requirements": work_reqs,
        "midterms": midterms,
        "final_exam": final_exam,
        "graph": {
            "description": "Final exam depends on completing all work requirements",
            "terminal_node": final_exam["id"] if final_exam else None,
            "work_nodes": [w["id"] for w in work_reqs],
        }
    })


if __name__ == "__main__":
    print("Starting API server on http://localhost:5050")
    print("Serving REAL data only - no hardcoded degree models")
    print("\nEndpoints:")
    print("  GET /api/stats")
    print("  GET /api/institutions")
    print("  GET /api/subjects")
    print("  GET /api/courses?subject=CMPT&institution=usask")
    print("  GET /api/course/<id>")
    print("  GET /api/course/<id>/completion  (full course requirements graph)")
    print("  GET /api/prerequisites")
    print("  GET /api/transfers")
    print("\nNew - Course Materials & Completion:")
    print("  GET /api/textbooks")
    print("  GET /api/textbook/<id>")
    print("  GET /api/work-requirements?course=<id>&type=<type>")
    print("  GET /api/work-requirement/<id>")
    print("  GET /api/exams?course=<id>&institution=<inst>")
    print("  GET /api/exam/<id>")
    app.run(debug=True, port=5050)
