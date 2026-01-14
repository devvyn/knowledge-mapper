"""
Saskatchewan Polytechnic adapter for unified institution interface.
"""
from typing import Optional

from devvyn.api.saskpolytech import SaskPolytechClient, SaskPolytechCourse
from devvyn.institutions.base import (
    CourseReference,
    CredentialType,
    InstitutionAdapter,
    UnifiedCourse,
    UnifiedProgram,
)


class SaskPolytechAdapter(InstitutionAdapter):
    """
    Adapter for Saskatchewan Polytechnic course catalogue.

    Wraps the SaskPolytech API client and converts responses to unified format.
    """

    def __init__(self):
        self._client: Optional[SaskPolytechClient] = None
        self._programs_cache: Optional[list[dict]] = None

    @property
    def id(self) -> str:
        return "saskpolytech"

    @property
    def name(self) -> str:
        return "Saskatchewan Polytechnic"

    @property
    def short_name(self) -> str:
        return "SaskPolytech"

    @property
    def location(self) -> str:
        return "Saskatoon, SK"  # Multiple campuses, Saskatoon is largest

    async def _ensure_client(self) -> SaskPolytechClient:
        """Ensure client is initialized."""
        if self._client is None:
            self._client = SaskPolytechClient()
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

    def _convert_course(self, course: SaskPolytechCourse) -> UnifiedCourse:
        """Convert SaskPolytech course to UnifiedCourse."""
        # Convert prerequisites to CourseReferences
        prereq_refs = [self.make_ref(c) for c in course.prerequisites]
        coreq_refs = [self.make_ref(c) for c in course.corequisites]

        return UnifiedCourse(
            ref=self.make_ref(course.code),
            title=course.title,
            description=course.description,
            credits=float(course.credit_hours),
            lecture_hours=float(course.lecture_hours),
            lab_hours=float(course.lab_hours),
            prerequisites=prereq_refs,
            corequisites=coreq_refs,
            url=f"https://saskpolytech.ca/programs-and-courses/",
        )

    def _convert_program(self, data: dict, courses: list[UnifiedCourse] = None) -> UnifiedProgram:
        """Convert SaskPolytech program data to UnifiedProgram."""
        credential = CredentialType.from_string(data.get("degree", ""))

        return UnifiedProgram(
            institution=self.id,
            code=data.get("code", ""),
            name=data.get("name", ""),
            credential=credential,
            description="",  # Would need to parse from overview HTML
            courses=courses or [],
            url=f"https://saskpolytech.ca/programs-and-courses/programs/{data.get('filename', '')}",
        )

    async def _get_programs_raw(self) -> list[dict]:
        """Get raw program data, cached."""
        if self._programs_cache is None:
            client = await self._ensure_client()
            response = await client.get_programs()
            self._programs_cache = response.data
        return self._programs_cache

    async def get_course(self, code: str) -> Optional[UnifiedCourse]:
        """
        Get a specific course by code.

        Note: SaskPolytech courses are organized by program, so this
        requires knowing which program the course belongs to.
        """
        # Would need to search through all programs to find the course
        # For now, return None - use get_program() instead
        return None

    async def get_courses_by_subject(self, subject: str) -> list[UnifiedCourse]:
        """
        Get all courses with a subject code prefix.

        Searches all programs for courses matching the subject.
        """
        client = await self._ensure_client()
        programs = await self._get_programs_raw()
        subject = subject.upper()

        courses = []
        seen_codes = set()

        for prog_data in programs:
            try:
                program = await client.get_program_with_courses(prog_data["code"])
                for course in program.courses:
                    if course.subject_code == subject and course.code not in seen_codes:
                        courses.append(self._convert_course(course))
                        seen_codes.add(course.code)
            except Exception:
                # Skip programs that fail to load
                continue

        return courses

    async def get_program(self, code: str) -> Optional[UnifiedProgram]:
        """Get a specific program by code (e.g., 'CSTDP')."""
        client = await self._ensure_client()

        try:
            program = await client.get_program_with_courses(code.upper())
        except ValueError:
            return None

        # Convert courses
        courses = [self._convert_course(c) for c in program.courses]

        # Get program metadata
        programs = await self._get_programs_raw()
        prog_data = next(
            (p for p in programs if p.get("code") == code.upper()),
            {}
        )

        unified = self._convert_program(prog_data, courses)
        return unified

    async def get_programs(self) -> list[UnifiedProgram]:
        """Get all programs (without courses loaded)."""
        programs = await self._get_programs_raw()
        return [self._convert_program(p) for p in programs]

    async def search_courses(self, query: str) -> list[UnifiedCourse]:
        """
        Search courses by keyword.

        Searches course titles across all programs.
        """
        client = await self._ensure_client()
        programs = await self._get_programs_raw()
        query = query.lower()

        results = []
        seen_codes = set()

        for prog_data in programs:
            try:
                program = await client.get_program_with_courses(prog_data["code"])
                for course in program.courses:
                    if course.code not in seen_codes:
                        if query in course.title.lower() or query in course.code.lower():
                            results.append(self._convert_course(course))
                            seen_codes.add(course.code)
            except Exception:
                continue

        return results


# Singleton instance
_instance: Optional[SaskPolytechAdapter] = None


def get_saskpolytech_adapter() -> SaskPolytechAdapter:
    """Get the SaskPolytech adapter singleton."""
    global _instance
    if _instance is None:
        _instance = SaskPolytechAdapter()
    return _instance
