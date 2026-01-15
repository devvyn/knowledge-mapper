#!/usr/bin/env python3
"""
REST API for dynamic graph exploration.
Wraps the degree models and course data for visualization frontends.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify, request
from flask_cors import CORS

from devvyn.degrees.usask import get_usask_programs, get_program

app = Flask(__name__)
CORS(app)  # Allow viz pages to fetch


@app.route("/api/programs")
def list_programs():
    """List all available degree programs."""
    programs = get_usask_programs()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "credential": p.credential.value,
            "credits": p.total_credits,
            "institution": p.institution,
        }
        for p in programs
    ])


@app.route("/api/program/<path:program_id>")
def get_program_details(program_id: str):
    """Get detailed requirements for a program."""
    prog = get_program(program_id)
    if not prog:
        return jsonify({"error": f"Unknown program: {program_id}"}), 404

    return jsonify({
        "id": prog.id,
        "name": prog.name,
        "credential": prog.credential.value,
        "credits": prog.total_credits,
        "institution": prog.institution,
        "courses": list(prog.all_possible_courses()),
        "required": list(prog.all_required_courses()),
        "blocks": [
            {
                "code": b.code,
                "name": b.name,
                "credits": b.total_credits,
                "courses": list(b.all_possible_courses()),
            }
            for b in prog.requirements
        ],
    })


@app.route("/api/courses")
def list_courses():
    """List courses, optionally filtered by subject or program."""
    subject = request.args.get("subject")
    program_id = request.args.get("program")

    # Collect all courses from all programs
    all_courses = set()
    for prog in get_usask_programs():
        all_courses.update(prog.all_possible_courses())

    courses = []
    for code in sorted(all_courses):
        parts = code.split()
        subj = parts[0] if parts else ""

        if subject and subj != subject.upper():
            continue

        if program_id:
            prog = get_program(program_id)
            if prog and code not in prog.all_possible_courses():
                continue

        courses.append({
            "id": f"usask:{code}",
            "code": code,
            "subject": subj,
            "institution": "usask",
        })

    return jsonify(courses)


@app.route("/api/course/<path:code>")
def get_course(code: str):
    """Get details for a specific course."""
    # Find which programs this course counts toward
    satisfies = []
    for prog in get_usask_programs():
        if code in prog.all_possible_courses():
            satisfies.append({
                "id": prog.id,
                "name": prog.name,
                "required": code in prog.all_required_courses(),
            })

    parts = code.split()
    return jsonify({
        "id": f"usask:{code}",
        "code": code,
        "subject": parts[0] if parts else "",
        "institution": "usask",
        "satisfies": satisfies,
    })


@app.route("/api/subjects")
def list_subjects():
    """List all subjects with course counts."""
    subjects = {}
    for prog in get_usask_programs():
        for code in prog.all_possible_courses():
            subj = code.split()[0] if code.split() else "UNKNOWN"
            subjects[subj] = subjects.get(subj, 0) + 1

    return jsonify([
        {"subject": s, "count": c}
        for s, c in sorted(subjects.items())
    ])


if __name__ == "__main__":
    print("Starting API server on http://localhost:5050")
    print("Endpoints:")
    print("  GET /api/programs")
    print("  GET /api/program/<id>")
    print("  GET /api/courses?subject=BIOL")
    print("  GET /api/course/CMPT 141")
    print("  GET /api/subjects")
    app.run(debug=True, port=5050)
