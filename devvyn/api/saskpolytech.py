"""
Async client for Saskatchewan Polytechnic API.

API base: https://webapi.saskpolytech.ca/
Endpoints:
  - /Program/list/?active=true   → all active programs
  - /Program/{code}/courses      → courses for a program
  - /Course/list                 → continuing education courses
  - /Cip/list                    → CIP code mappings
"""
import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from aiolimiter import AsyncLimiter

from devvyn.cache.file_cache import FileCache, sanitize_filename


BASE_URL = "https://webapi.saskpolytech.ca"
DEFAULT_CACHE_DIR = "./data/saskpolytech_cache"

# Rate limit: 5 requests per second (polite)
DEFAULT_RATE_LIMIT = AsyncLimiter(5, 1)


@dataclass
class CachedResponse:
    """API response with provenance metadata."""
    data: dict | list
    fetched_at: datetime
    url: str


@dataclass
class SaskPolytechCourse:
    """Normalized course from SaskPolytech."""
    id: str
    subject_code: str
    course_num: str
    title: str
    description: str
    credit_hours: int
    lecture_hours: int
    lab_hours: int
    prerequisites: list[str]  # Parsed prerequisite course codes
    corequisites: list[str]
    equivalents: list[str]
    semester: str  # e.g., "Year 1 - Semester 1"

    @classmethod
    def from_api(cls, data: dict, semester_key: str) -> "SaskPolytechCourse":
        """Create from API response value."""
        value = data.get("value", data)

        # Parse prerequisites (comma-separated course codes)
        prereq_str = value.get("prereq", "") or value.get("catalogPrereq", "") or ""
        prereqs = parse_course_list(prereq_str)

        # Parse corequisites
        coreq_str = value.get("coreq", "") or ""
        coreqs = parse_course_list(coreq_str)

        # Parse equivalents
        equiv_str = value.get("equivalent", "") or ""
        equivs = parse_course_list(equiv_str)

        return cls(
            id=value.get("id", ""),
            subject_code=value.get("subjectCode", ""),
            course_num=value.get("courseNum", ""),
            title=value.get("title", ""),
            description=value.get("description", ""),
            credit_hours=int(value.get("creditHours", 0) or 0),
            lecture_hours=int(value.get("lectureHours", 0) or 0),
            lab_hours=int(value.get("labHours", 0) or 0),
            prerequisites=prereqs,
            corequisites=coreqs,
            equivalents=equivs,
            semester=semester_key,
        )

    @property
    def code(self) -> str:
        """Full course code, e.g., 'COSC 180'."""
        return f"{self.subject_code} {self.course_num}"


@dataclass
class SaskPolytechProgram:
    """Normalized program from SaskPolytech."""
    code: str
    name: str
    credential: str  # Diploma, Certificate, Degree, etc.
    location: str
    school: str  # e.g., "School of Business and Entrepreneurship"
    active: bool
    international: bool
    part_time: bool
    courses: list[SaskPolytechCourse] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict) -> "SaskPolytechProgram":
        """Create from API response."""
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            credential=data.get("degree", ""),
            location=data.get("location", ""),
            school=data.get("cluster", ""),
            active=data.get("active", "").lower() == "true",
            international=bool(data.get("international")),
            part_time=bool(data.get("partTime")),
        )


def parse_course_list(text: str) -> list[str]:
    """
    Parse a comma-separated list of course codes.

    Input: "COSA 190, TCOM 190" or "COOS 181"
    Output: ["COSA 190", "TCOM 190"] or ["COOS 181"]
    """
    if not text or not text.strip():
        return []

    courses = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        # Normalize: ensure space between subject and number
        # Handle "COSC180" -> "COSC 180"
        normalized = normalize_course_code(part)
        if normalized:
            courses.append(normalized)
    return courses


def normalize_course_code(code: str) -> str:
    """Normalize course code format: 'COSC180' -> 'COSC 180'."""
    import re
    code = code.upper().strip()
    # Match pattern like "COSC180" or "COSC 180"
    match = re.match(r'^([A-Z]{2,4})\s*(\d{3})$', code)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return code if code else ""


class SaskPolytechClient:
    """
    Async client for Saskatchewan Polytechnic API.

    Features:
    - Rate limiting to avoid hammering the server
    - Disk caching with timestamps
    - Async/await interface
    """

    def __init__(
        self,
        cache_dir: str | Path = DEFAULT_CACHE_DIR,
        rate_limiter: Optional[AsyncLimiter] = None,
    ):
        self.cache = FileCache(cache_dir)
        self.limiter = rate_limiter or DEFAULT_RATE_LIMIT
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=30.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    def _cache_key(self, endpoint: str, **params) -> str:
        """Generate cache key from endpoint and params."""
        key = endpoint.strip("/").replace("/", "_")
        if params:
            param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()) if v)
            key = f"{key}_{param_str}"
        return sanitize_filename(key) + ".json"

    def _read_cache(self, key: str) -> Optional[CachedResponse]:
        """Read from cache if exists, return with metadata."""
        try:
            raw = self.cache.load(key)
            cached = json.loads(raw)
            return CachedResponse(
                data=cached["data"],
                fetched_at=datetime.fromisoformat(cached["fetched_at"]),
                url=cached["url"],
            )
        except (KeyError, json.JSONDecodeError):
            return None

    def _write_cache(self, key: str, data: dict | list, url: str) -> None:
        """Write to cache with timestamp."""
        cached = {
            "data": data,
            "fetched_at": datetime.now().isoformat(),
            "url": url,
        }
        self.cache.save(key, json.dumps(cached, indent=2))

    async def _fetch(self, endpoint: str, **params) -> CachedResponse:
        """
        Fetch from API with rate limiting and caching.

        Returns cached response if available, otherwise fetches fresh.
        """
        cache_key = self._cache_key(endpoint, **params)

        # Check cache first
        cached = self._read_cache(cache_key)
        if cached:
            return cached

        # Rate limit, then fetch
        async with self.limiter:
            if not self._client:
                raise RuntimeError("Client not initialized. Use 'async with' context.")

            response = await self._client.get(endpoint, params=params or None)
            response.raise_for_status()
            data = response.json()

        # Cache the response
        self._write_cache(cache_key, data, str(response.url))

        return CachedResponse(
            data=data,
            fetched_at=datetime.now(),
            url=str(response.url),
        )

    async def get_programs(self, active_only: bool = True) -> CachedResponse:
        """
        Get all programs.

        Args:
            active_only: If True, only return active programs

        Returns: CachedResponse with list of program dicts
        """
        params = {"active": "true"} if active_only else {}
        return await self._fetch("/Program/list/", **params)

    async def get_program_courses(self, program_code: str) -> CachedResponse:
        """
        Get all courses for a program.

        Args:
            program_code: e.g., "CSTDP" for Computer Systems Technology

        Returns: CachedResponse with list of course dicts organized by semester
        """
        return await self._fetch(f"/Program/{program_code}/courses")

    async def get_continuing_ed_courses(self) -> CachedResponse:
        """
        Get continuing education courses.

        Returns: CachedResponse with list of course dicts
        """
        return await self._fetch("/Course/list")

    async def get_cip_codes(self) -> CachedResponse:
        """
        Get CIP code mappings for programs.

        Returns: CachedResponse with list of {program, credential, cipCode}
        """
        return await self._fetch("/Cip/list")

    async def get_program_with_courses(self, program_code: str) -> SaskPolytechProgram:
        """
        Get a program with all its courses loaded.

        Args:
            program_code: e.g., "CSTDP"

        Returns: SaskPolytechProgram with courses populated
        """
        # Get program info
        programs_response = await self.get_programs()
        program_data = next(
            (p for p in programs_response.data if p.get("code") == program_code),
            None
        )

        if not program_data:
            raise ValueError(f"Program not found: {program_code}")

        program = SaskPolytechProgram.from_api(program_data)

        # Get courses
        courses_response = await self.get_program_courses(program_code)
        for item in courses_response.data:
            semester_key = item.get("key", "Unknown")
            course = SaskPolytechCourse.from_api(item, semester_key)
            program.courses.append(course)

        return program


# Convenience function for sync usage
def get_client(cache_dir: str | Path = DEFAULT_CACHE_DIR) -> SaskPolytechClient:
    """Create a client instance. Use with 'async with'."""
    return SaskPolytechClient(cache_dir=cache_dir)


async def demo():
    """Demo the API client."""
    async with SaskPolytechClient() as client:
        # Get all programs
        print("Fetching all programs...")
        programs = await client.get_programs()
        print(f"  Total programs: {len(programs.data)}")
        print(f"  Fetched at: {programs.fetched_at}")

        # Show some programs
        print("\n  Sample programs:")
        for p in programs.data[:5]:
            print(f"    {p['code']}: {p['name']} ({p['degree']})")

        # Get CST courses
        print("\nFetching Computer Systems Technology courses...")
        cst = await client.get_program_with_courses("CSTDP")
        print(f"  Program: {cst.name} ({cst.credential})")
        print(f"  Total courses: {len(cst.courses)}")

        # Show courses by semester
        print("\n  Courses by semester:")
        semesters = {}
        for course in cst.courses:
            if course.semester not in semesters:
                semesters[course.semester] = []
            semesters[course.semester].append(course)

        for semester, courses in sorted(semesters.items()):
            print(f"\n  {semester}:")
            for c in courses:
                prereq_str = f" (prereqs: {', '.join(c.prerequisites)})" if c.prerequisites else ""
                print(f"    {c.code}: {c.title}{prereq_str}")

        # Get CIP codes
        print("\nFetching CIP codes...")
        cip = await client.get_cip_codes()
        print(f"  Total CIP mappings: {len(cip.data)}")


if __name__ == "__main__":
    asyncio.run(demo())
