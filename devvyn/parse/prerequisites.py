"""
Parse prerequisite information from USask course 'tech' field HTML.

Patterns handled:
- Simple required: "CMPT 270"
- Multiple required: "X and Y", "X; and Y"
- Explicit alternatives: "One of (X, Y, Z)"
- Implicit alternatives: "X or Y or Z"
- Grade requirements: "60% in CMPT 141"
- Corequisites: "(can be taken concurrently)"
- High school: "Mathematics B30", "Computer Science 30"
"""
import re
from dataclasses import dataclass, field
from html import unescape
from typing import Optional


# Course code pattern: 2-4 uppercase letters, optional space, 3-digit number, optional .digit
COURSE_PATTERN = re.compile(
    r'\b([A-Z]{2,4})\s*(\d{3})(?:\.(\d))?\b'
)

# High school course pattern
HS_PATTERN = re.compile(
    r'\b((?:Mathematics|Foundations of Mathematics|Pre-Calculus|Computer Science)\s+[ABC]?\d{2})\b',
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

    # High school prerequisites (alternative group)
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
        """All university course codes mentioned (for reference)."""
        courses = set(self.required)
        for group in self.one_of:
            courses.update(c for c in group if is_university_course(c))
        courses.update(self.corequisites)
        courses.update(self.grade_requirements.keys())
        return courses

    @property
    def required_courses(self) -> set[str]:
        """Only truly required courses (not alternatives)."""
        return set(self.required)

    @property
    def alternative_groups(self) -> list[list[str]]:
        """Alternative groups with only university courses."""
        return [
            [c for c in group if is_university_course(c)]
            for group in self.one_of
        ]


def is_university_course(code: str) -> bool:
    """Check if code looks like a university course (not high school)."""
    if not code:
        return False
    # High school courses contain words or "B30" style patterns
    if any(w in code.lower() for w in ['mathematics', 'calculus', 'computer science']):
        return False
    # University courses are like "CMPT 141"
    return bool(re.match(r'^[A-Z]{2,4}\s*\d{3}', code))


def strip_html(text: str) -> str:
    """Remove HTML tags and unescape entities."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_course(code: str) -> str:
    """Normalize course code format: 'CMPT141' -> 'CMPT 141'."""
    code = code.upper().strip()
    # Remove credit suffix
    code = re.sub(r'\.\d$', '', code)
    # Ensure space between subject and number
    code = re.sub(r'([A-Z]+)(\d)', r'\1 \2', code)
    return code


def extract_course_codes(text: str) -> list[str]:
    """Extract all course codes from text, normalized."""
    matches = COURSE_PATTERN.findall(text)
    return [normalize_course(f"{subj}{num}") for subj, num, _ in matches]


def extract_high_school(text: str) -> list[str]:
    """Extract high school course requirements."""
    return [m.group(1) for m in HS_PATTERN.finditer(text)]


def split_by_and(text: str) -> list[str]:
    """Split text by 'and' connectors, respecting parentheses."""
    # Split on '; and', ' and ', but not inside parentheses
    parts = re.split(r';\s*and\s+|\s+and\s+', text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def parse_or_group(text: str) -> list[str]:
    """Parse a group of alternatives connected by 'or'."""
    # Split by 'or' and commas
    parts = re.split(r'\s+or\s+|,\s*', text, flags=re.IGNORECASE)
    courses = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Extract course codes from this part
        codes = extract_course_codes(part)
        courses.extend(codes)
        # Also check for high school
        hs = extract_high_school(part)
        courses.extend(hs)
    return courses


def has_or_connector(text: str) -> bool:
    """Check if text contains 'or' connecting courses."""
    return bool(re.search(r'\b(or)\b', text, re.IGNORECASE))


def parse_prerequisites(tech_html: Optional[str]) -> Prerequisites:
    """
    Parse the 'tech' field HTML into structured prerequisite data.

    Distinguishes between:
    - Required courses (connected by 'and')
    - Alternative groups (connected by 'or' or 'One of')
    """
    if not tech_html:
        return Prerequisites()

    prereqs = Prerequisites(raw=tech_html)
    text = strip_html(tech_html)

    # Extract prerequisite section only
    prereq_match = re.search(
        r'Prerequisite\(?s?\)?:\s*(.+?)(?=(?:Note:|Restriction|$))',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not prereq_match:
        return prereqs

    prereq_text = prereq_match.group(1).strip()

    # Track which courses we've assigned
    assigned_courses = set()

    # 1. Extract explicit "One of" groups
    one_of_pattern = re.compile(
        r'[Oo]ne of\s*\(([^)]+)\)|[Oo]ne of\s+([^;.]+?)(?=;|\.|and\s|$)',
        re.IGNORECASE
    )

    for match in one_of_pattern.finditer(prereq_text):
        group_text = match.group(1) or match.group(2)
        if group_text:
            alternatives = parse_or_group(group_text)
            if alternatives:
                prereqs.one_of.append(alternatives)
                assigned_courses.update(normalize_course(c) for c in alternatives if is_university_course(c))

    # 2. Extract high school requirements
    prereqs.high_school = extract_high_school(prereq_text)

    # 3. Look for corequisites
    coreq_match = re.search(r'\(can be taken concurrently\)', prereq_text, re.IGNORECASE)
    if coreq_match:
        before = prereq_text[:coreq_match.start()]
        # Get courses immediately before this phrase
        nearby = extract_course_codes(before[-80:] if len(before) > 80 else before)
        for c in nearby:
            if c not in assigned_courses:
                prereqs.corequisites.append(c)
                assigned_courses.add(c)

    # 4. Extract grade requirements
    grade_pattern = re.compile(
        r'(\d+)%\s*(?:or higher\s*)?(?:in\s+)?([A-Z]{2,4}\s*\d{3})',
        re.IGNORECASE
    )

    for match in grade_pattern.finditer(prereq_text):
        pct = int(match.group(1))
        course = normalize_course(match.group(2))
        prereqs.grade_requirements[course] = pct

    # 5. Process remaining text for required vs alternative
    # Remove already-processed "One of" sections
    remaining = one_of_pattern.sub(' ', prereq_text)

    # Split by "and" to find independent requirements
    and_parts = split_by_and(remaining)

    for part in and_parts:
        part = part.strip('() ')
        if not part:
            continue

        courses_in_part = extract_course_codes(part)

        # If this part has "or", it's an alternative group
        if has_or_connector(part) and len(courses_in_part) > 1:
            alternatives = [c for c in courses_in_part if c not in assigned_courses]
            if len(alternatives) > 1:
                prereqs.one_of.append(alternatives)
                assigned_courses.update(alternatives)
            elif len(alternatives) == 1:
                prereqs.required.append(alternatives[0])
                assigned_courses.add(alternatives[0])
        else:
            # No "or" - these are all required
            for c in courses_in_part:
                if c not in assigned_courses:
                    prereqs.required.append(c)
                    assigned_courses.add(c)

    # 6. Extract notes
    if 'permission' in text.lower():
        prereqs.notes.append("Permission may be required")
    restriction_match = re.search(r'Restriction\(?s?\)?:\s*([^.]+)', text, re.IGNORECASE)
    if restriction_match:
        prereqs.notes.append(restriction_match.group(1).strip())

    return prereqs


def demo():
    """Demo the parser with sample tech fields."""
    samples = [
        (
            "CMPT 141",
            '<B>Prerequisite(s):</B> One of (Computer Science 30, CMPT 140.3, BINF 151.3) and one of (Mathematics B30, Foundations of Mathematics 30, Pre-Calculus 30); or MATH 110.3, MATH 123.3, MATH 125.3, MATH 133.4, MATH 163.3, or MATH 176.3 (can be taken concurrently).<BR>'
        ),
        (
            "CMPT 145",
            '<B>Prerequisite(s):</B> (60% in CMPT 141.3 or CMPT 142.3) or (60% in CMPT 111.3 and permission of the department).<BR>'
        ),
        (
            "CMPT 215",
            '<B>Prerequisite(s):</B> CMPT 214.3; and one of MATH 163.3 or CMPT 260.3.<BR>'
        ),
        (
            "CMPT 280",
            '<B>Prerequisite(s):</B> CMPT 270.<BR>'
        ),
        (
            "MATH 116",
            '<B>Prerequisite(s):</B> MATH 110.3 or MATH 176.3 or MATH 133.4.<BR>'
        ),
        (
            "MATH 211",
            '<B>Prerequisite(s):</B> MATH 116.3 or MATH 177.3 or MATH 124.3 or MATH 134.3 or MATH 164.3.<BR>'
        ),
    ]

    for name, tech in samples:
        print(f"=== {name} ===")
        prereqs = parse_prerequisites(tech)
        print(f"  Required: {prereqs.required}")
        print(f"  One of groups: {prereqs.one_of}")
        print(f"  Corequisites: {prereqs.corequisites}")
        print(f"  High school: {prereqs.high_school}")
        print(f"  Grade reqs: {prereqs.grade_requirements}")
        if prereqs.notes:
            print(f"  Notes: {prereqs.notes}")
        print()


if __name__ == "__main__":
    demo()
