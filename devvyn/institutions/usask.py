"""
University of Saskatchewan adapter for unified institution interface.
"""
from typing import Optional

from devvyn.api.usask_catalogue import USaskCatalogueClient
from devvyn.institutions.base import (
    CourseReference,
    CredentialType,
    InstitutionAdapter,
    UnifiedCourse,
    UnifiedProgram,
)
from devvyn.parse.prerequisites import parse_prerequisites


class USaskAdapter(InstitutionAdapter):
    """
    Adapter for University of Saskatchewan course catalogue.

    Wraps the USask API client and converts responses to unified format.
    """

    def __init__(self):
        self._client: Optional[USaskCatalogueClient] = None

    @property
    def id(self) -> str:
        return "usask"

    @property
    def name(self) -> str:
        return "University of Saskatchewan"

    @property
    def short_name(self) -> str:
        return "USask"

    @property
    def location(self) -> str:
        return "Saskatoon, SK"

    async def _ensure_client(self) -> USaskCatalogueClient:
        """Ensure client is initialized."""
        if self._client is None:
            self._client = USaskCatalogueClient()
            await self._client.__aenter__()
        return self._client

    async def close(self):
        """Close the client connection."""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _convert_course(self, data: dict) -> UnifiedCourse:
        """Convert USask API course data to UnifiedCourse."""
        # Parse course code
        subject = data.get("subject", "")
        number = data.get("course_number", "")
        code = f"{subject} {number}"

        # Parse prerequisites from tech field
        tech = data.get("tech", "")
        prereqs = parse_prerequisites(tech)

        # Convert required prerequisites to CourseReferences
        required_refs = [
            self.make_ref(c) for c in prereqs.required
        ]

        # Convert alternative groups
        alt_groups = [
            [self.make_ref(c) for c in group]
            for group in prereqs.alternative_groups
            if group  # Skip empty groups
        ]

        # Parse credits from title or credit field
        credits = 0.0
        title = data.get("title", "")
        # USask titles often include credits like "Introduction to Computer Science (3)"
        if "(" in title and ")" in title:
            try:
                credit_str = title.split("(")[-1].rstrip(")")
                credits = float(credit_str)
                title = title.rsplit("(", 1)[0].strip()
            except ValueError:
                pass

        return UnifiedCourse(
            ref=self.make_ref(code),
            title=title,
            description=data.get("description", ""),
            credits=credits,
            prerequisites=required_refs,
            prerequisite_alternatives=alt_groups,
            url=f"https://catalogue.usask.ca/#{data.get('id', '')}",
        )

    async def get_course(self, code: str) -> Optional[UnifiedCourse]:
        """Get a specific course by code (e.g., 'CMPT 141')."""
        client = await self._ensure_client()

        # Parse code into subject and number
        parts = code.upper().split()
        if len(parts) != 2:
            return None

        subject, number = parts
        response = await client.get_course(subject, number)
        courses = response.data.get("courses", [])

        if not courses:
            return None

        course = self._convert_course(courses[0])
        course.fetched_at = response.fetched_at
        return course

    async def get_courses_by_subject(self, subject: str) -> list[UnifiedCourse]:
        """Get all courses in a subject (e.g., 'CMPT')."""
        client = await self._ensure_client()
        response = await client.get_courses_by_subject(subject.upper())

        courses = []
        for data in response.data.get("courses", []):
            course = self._convert_course(data)
            course.fetched_at = response.fetched_at
            courses.append(course)

        return courses

    async def get_program(self, code: str) -> Optional[UnifiedProgram]:
        """
        Get a specific program.

        Note: USask's API is course-centric, not program-centric.
        Programs would need to be scraped from programs.usask.ca
        """
        # TODO: Implement when program scraping is fixed
        return None

    async def get_programs(self) -> list[UnifiedProgram]:
        """
        Get all programs.

        Note: USask's API is course-centric, not program-centric.
        """
        # TODO: Implement when program scraping is fixed
        return []

    async def search_courses(self, query: str) -> list[UnifiedCourse]:
        """
        Search courses by keyword.

        Currently searches all course codes/titles fetched.
        """
        # For now, this would need to fetch all courses which is expensive
        # TODO: Implement efficient search
        return []


# Singleton instance
_instance: Optional[USaskAdapter] = None


def get_usask_adapter() -> USaskAdapter:
    """Get the USask adapter singleton."""
    global _instance
    if _instance is None:
        _instance = USaskAdapter()
    return _instance
