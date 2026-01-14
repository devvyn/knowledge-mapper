"""
Async client for USask Course Catalogue API.

API base: https://catalogue.usask.ca/
Endpoints:
  - /course_titles     → {code: title} for all courses
  - /api/?subj_code=X  → detailed course list for subject
  - /api/?subj_code=X&course_number=Y → single course
"""
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from aiolimiter import AsyncLimiter

from devvyn.cache.file_cache import FileCache, sanitize_filename


BASE_URL = "https://catalogue.usask.ca"
DEFAULT_CACHE_DIR = "./data/api_cache"

# Rate limit: 10 requests per second (polite)
DEFAULT_RATE_LIMIT = AsyncLimiter(10, 1)


@dataclass
class CachedResponse:
    """API response with provenance metadata."""
    data: dict | list
    fetched_at: datetime
    url: str


class USaskCatalogueClient:
    """
    Async client for USask Course Catalogue API.

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
        key = endpoint.strip("/")
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

    async def get_all_course_codes(self) -> CachedResponse:
        """
        Get all course codes and titles.

        Returns: CachedResponse with data as {code: title} dict
        """
        return await self._fetch("/course_titles")

    async def get_courses_by_subject(self, subject_code: str) -> CachedResponse:
        """
        Get all courses for a subject.

        Args:
            subject_code: e.g., "CMPT", "MATH"

        Returns: CachedResponse with data containing 'courses' list
        """
        return await self._fetch("/api/", subj_code=subject_code.upper())

    async def get_course(self, subject_code: str, course_number: str) -> CachedResponse:
        """
        Get a specific course.

        Args:
            subject_code: e.g., "CMPT"
            course_number: e.g., "141"

        Returns: CachedResponse with data containing 'courses' list (1 item if found)
        """
        # API doesn't filter by course_number, so we fetch subject and filter
        response = await self.get_courses_by_subject(subject_code)
        target_id = f"{subject_code.upper()}{course_number}"
        filtered = [
            c for c in response.data.get("courses", [])
            if c.get("id") == target_id
        ]
        return CachedResponse(
            data={"courses": filtered, **{k: v for k, v in response.data.items() if k != "courses"}},
            fetched_at=response.fetched_at,
            url=response.url,
        )


# Convenience function for sync usage
def get_client(cache_dir: str | Path = DEFAULT_CACHE_DIR) -> USaskCatalogueClient:
    """Create a client instance. Use with 'async with'."""
    return USaskCatalogueClient(cache_dir=cache_dir)


async def demo():
    """Demo the API client."""
    async with USaskCatalogueClient() as client:
        # Get all course codes
        print("Fetching all course codes...")
        codes = await client.get_all_course_codes()
        print(f"  Total courses: {len(codes.data)}")
        print(f"  Fetched at: {codes.fetched_at}")

        # Get CMPT courses
        print("\nFetching CMPT courses...")
        cmpt = await client.get_courses_by_subject("CMPT")
        print(f"  Found: {len(cmpt.data.get('courses', []))} courses")

        # Get specific course
        print("\nFetching CMPT 141...")
        course = await client.get_course("CMPT", "141")
        courses = course.data.get("courses", [])
        if courses:
            c = courses[0]
            print(f"  {c['id']}: {c['title']}")
            print(f"  Tech field (prerequisites): {c.get('tech', 'None')[:150]}...")
        else:
            print("  Not found")


if __name__ == "__main__":
    asyncio.run(demo())
