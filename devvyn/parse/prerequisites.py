"""
Parse prerequisite information from USask course 'tech' field HTML.

Patterns handled:
- Simple: "CMPT 270" or "CMPT 270.3"
- Multiple required: "X and Y", "X; and Y"
- Alternatives: "One of (X, Y, Z)", "X or Y"
- Grade requirements: "60% in CMPT 141"
- Corequisites: "(can be taken concurrently)"
- High school: "Mathematics B30", "Computer Science 30"
"""
import re
from dataclasses import dataclass, field
from html import unescape
from typing import Optional


# Course code pattern: 2-4 uppercase letters, space, 3-digit number, optional .digit
COURSE_PATTERN = re.compile(
    r'\b([A-Z]{2,4})\s*(\d{3})(?:\.(\d))?\b'
)

# High school course pattern
HS_PATTERN = re.compile(
    r'\b((?:Mathematics|Foundations of Mathematics|Pre-Calculus|Computer Science)\s+\d{2})\b',
    re.IGNORECASE
)


@dataclass
class Prerequisites:
    """Structured prerequisite data for a course."""

    # Required courses (all must be taken)
    required: list[str] = field(default_factory=list)

    # Alternative groups (one from each group must be taken)
    # e.g., [["CMPT 141", "CMPT 142"], ["MATH 110", "MATH 163"]]
    one_of: list[list[str]] = field(default_factory=list)

    # Courses that can be taken concurrently
    corequisites: list[str] = field(default_factory=list)

    # High school prerequisites
    high_school: list[str] = field(default_factory=list)

    # Grade requirements: {course: min_percentage}
    grade_requirements: dict[str, int] = field(default_factory=dict)

    # Special notes (permission required, restrictions, etc.)
    notes: list[str] = field(default_factory=list)

    # Raw text for reference
    raw: str = ""

    def __bool__(self) -> bool:
        """True if any prerequisites exist."""
        return bool(
            self.required or self.one_of or self.corequisites or
            self.high_school or self.grade_requirements
        )

    @property
    def all_courses(self) -> set[str]:
        """All university course codes mentioned."""
        courses = set(self.required)
        for group in self.one_of:
            courses.update(group)
        courses.update(self.corequisites)
        courses.update(self.grade_requirements.keys())
        return courses


def strip_html(text: str) -> str:
    """Remove HTML tags and unescape entities."""
    # Remove tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Unescape HTML entities
    text = unescape(text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_course_codes(text: str) -> list[str]:
    """Extract all course codes from text."""
    matches = COURSE_PATTERN.findall(text)
    return [f"{subj} {num}" for subj, num, _ in matches]


def extract_high_school(text: str) -> list[str]:
    """Extract high school course requirements."""
    return [m.group(1) for m in HS_PATTERN.finditer(text)]


def parse_prerequisites(tech_html: Optional[str]) -> Prerequisites:
    """
    Parse the 'tech' field HTML into structured prerequisite data.

    Args:
        tech_html: Raw HTML from the course API's 'tech' field

    Returns:
        Prerequisites dataclass with parsed data
    """
    if not tech_html:
        return Prerequisites()

    prereqs = Prerequisites(raw=tech_html)
    text = strip_html(tech_html)

    # Extract prerequisite section
    prereq_match = re.search(
        r'Prerequisite\(?s?\)?:\s*(.+?)(?=(?:Note:|Restriction|$))',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not prereq_match:
        return prereqs

    prereq_text = prereq_match.group(1).strip()

    # Extract high school courses first
    prereqs.high_school = extract_high_school(prereq_text)

    # Look for corequisites
    coreq_match = re.search(r'\(can be taken concurrently\)', prereq_text, re.IGNORECASE)
    if coreq_match:
        # Find courses near this phrase
        before = prereq_text[:coreq_match.start()]
        # Look for the last course mentioned before "can be taken concurrently"
        nearby = extract_course_codes(before[-50:] if len(before) > 50 else before)
        prereqs.corequisites.extend(nearby)

    # Look for "One of" patterns
    one_of_pattern = re.compile(
        r'[Oo]ne of\s*\(?([^)]+)\)?',
        re.IGNORECASE
    )

    for match in one_of_pattern.finditer(prereq_text):
        group_text = match.group(1)
        courses = extract_course_codes(group_text)
        # Also check for high school alternatives
        hs = extract_high_school(group_text)
        if courses or hs:
            prereqs.one_of.append(courses + hs)

    # Look for grade requirements
    grade_pattern = re.compile(
        r'(\d+)%\s*(?:or higher\s*)?(?:in\s+)?([A-Z]{2,4}\s*\d{3})',
        re.IGNORECASE
    )

    for match in grade_pattern.finditer(prereq_text):
        pct = int(match.group(1))
        course = match.group(2).upper()
        # Normalize spacing
        course = re.sub(r'\s+', ' ', course)
        prereqs.grade_requirements[course] = pct

    # Extract remaining required courses (not in one_of groups)
    all_courses = extract_course_codes(prereq_text)
    one_of_courses = set()
    for group in prereqs.one_of:
        one_of_courses.update(c for c in group if not c[0].isdigit())

    # Courses that appear with "and" connector are required
    # Simple heuristic: courses not in one_of groups
    for course in all_courses:
        if course not in one_of_courses and course not in prereqs.corequisites:
            prereqs.required.append(course)

    # Deduplicate required (keep order)
    seen = set()
    prereqs.required = [c for c in prereqs.required if not (c in seen or seen.add(c))]

    # Extract notes (restrictions, permissions)
    if 'permission' in text.lower():
        prereqs.notes.append("Permission may be required")
    if 'restriction' in text.lower():
        restriction_match = re.search(r'Restriction\(?s?\)?:\s*([^.]+)', text, re.IGNORECASE)
        if restriction_match:
            prereqs.notes.append(restriction_match.group(1).strip())

    return prereqs


def demo():
    """Demo the parser with sample tech fields."""
    samples = [
        # CMPT 141
        '<B>Prerequisite(s):</B> One of (Computer Science 30, CMPT 140.3, BINF 151.3) and one of (Mathematics B30, Foundations of Mathematics 30, Pre-Calculus 30); or MATH 110.3, MATH 123.3, MATH 125.3, MATH 133.4, MATH 163.3, or MATH 176.3 (can be taken concurrently).<BR>',
        # CMPT 145
        '<B>Prerequisite(s):</B> (60% in CMPT 141.3 or CMPT 142.3) or (60% in CMPT 111.3 and permission of the department).<BR>',
        # CMPT 215
        '<B>Prerequisite(s):</B> CMPT 214.3; and one of MATH 163.3 or CMPT 260.3.<BR>',
        # CMPT 280
        '<B>Prerequisite(s):</B> CMPT 270.<BR>',
    ]

    for i, tech in enumerate(samples, 1):
        print(f"=== Sample {i} ===")
        prereqs = parse_prerequisites(tech)
        print(f"Required: {prereqs.required}")
        print(f"One of: {prereqs.one_of}")
        print(f"Corequisites: {prereqs.corequisites}")
        print(f"High school: {prereqs.high_school}")
        print(f"Grade reqs: {prereqs.grade_requirements}")
        print(f"Notes: {prereqs.notes}")
        print(f"All courses: {prereqs.all_courses}")
        print()


if __name__ == "__main__":
    demo()
