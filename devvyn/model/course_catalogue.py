"""
Course catalogue model.

The model must be able to:

- Find official course description online, given only a course code.
- Understand course codes in various formats:
  - PSY 120
  - PSY-120
  - PSY 120.3
  - PSY-120.3
- Parse course prerequisite descriptions, producing:
  - list of course codes mentioned
  - remaining content fragments that could not be parsed
"""
import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from devvyn.api.usask_catalogue import USaskCatalogueClient, CachedResponse
from devvyn.parse.prerequisites import Prerequisites, parse_prerequisites


class Code:
    """ Course code parser. """

    def __init__(self, code: str):
        course_code = parse_course_code(code)
        if not course_code:
            raise ValueError(
                f'`code` value "{code}" is not of format "ABCD-120[.3]" '
                f'or "ABCD 120".')
        groups = course_code.groups()
        self.subject, self.number, self.credit = groups

    def __repr__(self):
        credit = f'.{self.credit}' if self.credit else ''
        return f'{self.subject}-{self.number}{credit}'

    @property
    def id(self) -> str:
        """Course ID as used by API (e.g., 'CMPT141')."""
        return f"{self.subject}{self.number}"


def parse_course_code(code):
    subject_pattern = r'(?P<subject>[A-Z]+)'
    credit_pattern = r'(?P<credit>\d)'
    number_pattern = r'(?P<number>\d{2,3})'
    code_pattern = (
        fr'{subject_pattern}[- ]?{number_pattern}'
        fr'(?:(?:[.]){credit_pattern})?')
    r = re.compile(code_pattern, re.IGNORECASE)
    return re.match(r, code.upper())


@dataclass
class Course:
    """
    Course with data from USask API.

    Supports lazy loading - data is fetched on first access.
    """
    code: Code
    _data: Optional[dict] = field(default=None, repr=False)
    _fetched_at: Optional[datetime] = field(default=None, repr=False)

    def __init__(self, code: str | Code):
        if isinstance(code, str):
            code = Code(code)
        self.code = code
        self._data = None
        self._fetched_at = None

    def _ensure_loaded(self) -> None:
        """Ensure course data is loaded."""
        if self._data is None:
            self._load_sync()

    def _load_sync(self) -> None:
        """Synchronously load course data."""
        asyncio.run(self._load_async())

    async def _load_async(self) -> None:
        """Asynchronously load course data."""
        async with USaskCatalogueClient() as client:
            response = await client.get_course(
                self.code.subject,
                self.code.number
            )
            courses = response.data.get("courses", [])
            if courses:
                self._data = courses[0]
            else:
                self._data = {}
            self._fetched_at = response.fetched_at

    @property
    def title(self) -> str:
        """Course title."""
        self._ensure_loaded()
        return self._data.get("title", "")

    @property
    def description(self) -> str:
        """Course description."""
        self._ensure_loaded()
        return self._data.get("description", "")

    @property
    def credits(self) -> str:
        """Credit units."""
        self._ensure_loaded()
        return self._data.get("credit_units", "")

    @property
    def college(self) -> str:
        """College name."""
        self._ensure_loaded()
        return self._data.get("college_name", "")

    @property
    def department(self) -> str:
        """Department name."""
        self._ensure_loaded()
        return self._data.get("department_name", "")

    @property
    def hours(self) -> str:
        """Hours description."""
        self._ensure_loaded()
        return self._data.get("hours", "")

    @property
    def tech_raw(self) -> str:
        """Raw tech field (prerequisites, notes, restrictions)."""
        self._ensure_loaded()
        return self._data.get("tech", "")

    @property
    def prerequisites(self) -> Prerequisites:
        """Parsed prerequisite structure."""
        return parse_prerequisites(self.tech_raw)

    @property
    def fetched_at(self) -> Optional[datetime]:
        """When the data was fetched."""
        self._ensure_loaded()
        return self._fetched_at

    @property
    def raw_data(self) -> dict:
        """Full raw API response data."""
        self._ensure_loaded()
        return self._data or {}

    def __repr__(self) -> str:
        return f"Course({self.code})"


async def get_course_async(course_code: str) -> Course:
    """
    Get a course by code, asynchronously.

    Args:
        course_code: e.g., "CMPT 141", "CMPT-141", "CMPT141"

    Returns:
        Course object with lazy-loaded data
    """
    course = Course(course_code)
    await course._load_async()
    return course


def get_course(course_code: str) -> Course:
    """
    Get a course by code, synchronously.

    Args:
        course_code: e.g., "CMPT 141", "CMPT-141", "CMPT141"

    Returns:
        Course object with lazy-loaded data
    """
    return Course(course_code)


async def get_all_courses_async(subject: str) -> list[Course]:
    """
    Get all courses for a subject.

    Args:
        subject: e.g., "CMPT", "MATH"

    Returns:
        List of Course objects
    """
    async with USaskCatalogueClient() as client:
        response = await client.get_courses_by_subject(subject)
        courses = []
        for data in response.data.get("courses", []):
            code = Code(data["id"])
            course = Course(code)
            course._data = data
            course._fetched_at = response.fetched_at
            courses.append(course)
        return courses


def get_all_courses(subject: str) -> list[Course]:
    """Get all courses for a subject, synchronously."""
    return asyncio.run(get_all_courses_async(subject))


def demo():
    """Demo the course model."""
    print("=== Single course ===")
    course = get_course("CMPT 141")
    print(f"Code: {course.code}")
    print(f"Title: {course.title}")
    print(f"Credits: {course.credits}")
    print(f"Department: {course.department}")
    print(f"Prerequisites: {course.prerequisites.all_courses}")
    print(f"Fetched at: {course.fetched_at}")

    print("\n=== All CMPT courses ===")
    courses = get_all_courses("CMPT")
    print(f"Found {len(courses)} courses")
    for c in courses[:5]:
        print(f"  {c.code}: {c.title}")


if __name__ == "__main__":
    demo()
