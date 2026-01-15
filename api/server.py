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
        if node.get("type") == "course":
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

    _cache["subjects"] = subjects_by_inst

    # Process prerequisite links
    for link in data.get("links", []):
        if link.get("type") == "prerequisite":
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
    print("  GET /api/prerequisites")
    print("  GET /api/transfers")
    app.run(debug=True, port=5050)
