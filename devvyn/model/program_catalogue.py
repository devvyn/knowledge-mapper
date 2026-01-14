"""
Data object for academic program dictionary.

Supports lazy loading to avoid hammering the server on initialization.
"""
import asyncio
import time
from datetime import datetime
from typing import Optional

import devvyn.scrape.page.usask
import devvyn.scrape.page.usask.program_catalogue
from devvyn.fetch import get_content
from devvyn.model.base import NamedSource, SourceMapping
from devvyn.scrape.page.usask.field import field_data
from devvyn.scrape.page.usask.program import parse_program


# Rate limiting: minimum seconds between requests
RATE_LIMIT_SECONDS = 0.1


class RateLimiter:
    """Simple rate limiter for synchronous code."""

    def __init__(self, min_interval: float = RATE_LIMIT_SECONDS):
        self.min_interval = min_interval
        self._last_request = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_request = time.time()


# Global rate limiter for program scraping
_rate_limiter = RateLimiter()


class ProgramCatalogue(SourceMapping):
    """
    Represent scraped data, with the list of study levels at the root and
    courses as the leaf nodes.

    Lazy loading: levels are fetched on first access, not on init.
    """

    def __init__(self, src: str = None) -> None:
        if src is not None:
            url_ = str(src)
        else:
            url_ = devvyn.scrape.page.usask.program_catalogue.URL_USASK_PROGRAMS_LIST
        super().__init__(url_)
        self._data: Optional[dict] = None
        self._fetched_at: Optional[datetime] = None

    def _ensure_loaded(self) -> None:
        """Fetch data if not already loaded."""
        if self._data is None:
            _rate_limiter.wait()
            program_catalogue = devvyn.scrape.page.usask.program_catalogue.program_catalogue_data(self.src)
            self._data = {
                level: AcademicLevel(src=self.src, name=level, field_urls=field_map)
                for level, field_map in program_catalogue.items()
            }
            self._fetched_at = datetime.now()

    @property
    def data(self) -> dict:
        """Lazy-loaded level data."""
        self._ensure_loaded()
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def fetched_at(self) -> Optional[datetime]:
        """When the catalogue was fetched."""
        return self._fetched_at

    @property
    def levels(self) -> dict:
        """Alias for data."""
        return self.data


class AcademicLevel(NamedSource):
    """
    Represents an academic level (Undergraduate, Graduate, etc.).

    Lazy loading: field objects are created on init but don't fetch
    their programs until accessed.
    """

    def __init__(self, src: str, name: str, field_urls: dict):
        super().__init__(name=name, src=src)
        self._field_urls = field_urls
        self._data: Optional[dict] = None

    def _ensure_loaded(self) -> None:
        """Create field objects (they load lazily themselves)."""
        if self._data is None:
            self._data = {
                field_name: AcademicField(
                    level=self.name,
                    name=field_name,
                    src=field_url
                )
                for field_name, field_url in self._field_urls.items()
            }

    @property
    def data(self) -> dict:
        """Lazy-loaded field data."""
        self._ensure_loaded()
        return self._data

    @data.setter
    def data(self, value):
        self._data = value


class AcademicField(NamedSource):
    """
    Represents an academic field of study (Computer Science, etc.).

    Lazy loading: programs are fetched on first data access.
    """

    def __init__(self, level: str, name: str, src: str) -> None:
        super().__init__(src=src, name=name)
        self.level = level
        self._data: Optional[dict] = None
        self._fetched_at: Optional[datetime] = None

    def _ensure_loaded(self) -> None:
        """Fetch and parse field page for programs."""
        if self._data is None:
            _rate_limiter.wait()
            try:
                content = get_content(self.src)
                self._data = field_data(content, self.src)
            except Exception as e:
                # Graceful degradation: empty data on failure
                self._data = {}
            self._fetched_at = datetime.now()

    @property
    def data(self) -> dict:
        """Lazy-loaded program data."""
        self._ensure_loaded()
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def fetched_at(self) -> Optional[datetime]:
        """When the field page was fetched."""
        return self._fetched_at

    @property
    def programs(self) -> dict:
        """Alias for data - dict of {program_name: program_url}."""
        return self.data


class AcademicProgram(NamedSource):
    """
    Program in a field of study.

    Lazy loading: program details fetched on access.
    """

    def __init__(self, name: str, src: str, level: str = "", field: str = ""):
        super().__init__(name=name, src=src)
        self.level = level
        self.field = field
        self._data: Optional[dict] = None
        self._fetched_at: Optional[datetime] = None

    def _ensure_loaded(self) -> None:
        """Fetch and parse program page."""
        if self._data is None:
            _rate_limiter.wait()
            try:
                content = get_content(self.src)
                self._data = parse_program(content)
            except Exception:
                self._data = {}
            self._fetched_at = datetime.now()

    @property
    def data(self) -> dict:
        """Lazy-loaded program data."""
        self._ensure_loaded()
        return self._data

    @property
    def fetched_at(self) -> Optional[datetime]:
        """When the program page was fetched."""
        return self._fetched_at


def get_programs(content, base_href) -> dict:
    """
    Academic field data, a list of programs on this page.

    :param content:
    :param base_href:
    :return:
    """
    return field_data(content, base_href)


def get_program_data(content: str) -> dict:
    """
    Program data.

    :param content:
    :return: dict-like collection of program data
    """
    return parse_program(content)


def demo():
    """Demo lazy loading."""
    import logging
    logging.basicConfig(level=logging.INFO)

    print("Creating ProgramCatalogue (no fetch yet)...")
    catalogue = ProgramCatalogue()

    print("\nAccessing levels (fetches catalogue page)...")
    levels = list(catalogue.data.keys())
    print(f"Levels: {levels}")

    print("\nAccessing first field in Undergraduate (no fetch yet)...")
    undergrad = catalogue.data.get("Undergraduate")
    if undergrad:
        first_field_name = list(undergrad.data.keys())[0]
        first_field = undergrad.data[first_field_name]
        print(f"Field: {first_field.name}")
        print(f"URL: {first_field.src}")

        print("\nAccessing programs (fetches field page)...")
        programs = first_field.programs
        print(f"Found {len(programs)} programs")
        for name in list(programs.keys())[:3]:
            print(f"  - {name}")


if __name__ == '__main__':
    demo()
