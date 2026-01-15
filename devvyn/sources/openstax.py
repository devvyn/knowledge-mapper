"""
OpenStax API client for fetching open textbook data.

OpenStax provides free, peer-reviewed textbooks under CC-BY license.
This client fetches the approved book catalog and maps to our Textbook model.

Data sources:
- Approved book list: GitHub raw content
- Book content: openstax.org website (chapter structure)
"""
import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx

# GitHub raw URL for approved books list
APPROVED_BOOKS_URL = (
    "https://raw.githubusercontent.com/openstax/content-manager-approved-books"
    "/main/approved-book-list.json"
)

# OpenStax book base URL
OPENSTAX_BOOK_URL = "https://openstax.org/books/{slug}/pages/1-introduction"

# Subjects relevant to Saskatchewan post-secondary courses
RELEVANT_SUBJECTS = {
    "python",           # CMPT
    "calculus",         # MATH
    "precalculus",      # MATH
    "statistics",       # STAT
    "u-physics",        # PHYS
    "college-physics",  # PHYS
    "chemistry",        # CHEM
    "biology",          # BIOL
    "psychology",       # PSYC
    "philosophy",       # PHIL
    "economics",        # ECON
    "dev-math",         # Developmental math
}


@dataclass
class OpenStaxChapter:
    """A chapter in an OpenStax textbook."""
    number: int
    title: str
    sections: list[str] = field(default_factory=list)
    estimated_minutes: int = 60  # Default 1 hour per chapter


@dataclass
class OpenStaxBook:
    """An OpenStax textbook with metadata."""
    uuid: str
    title: str
    slug: str
    style: str  # Subject category
    repository: str
    versions: int
    edition: int = 1

    # OER metadata
    license: str = "CC-BY"
    is_free: bool = True
    source_url: str = ""

    # Content
    chapters: list[OpenStaxChapter] = field(default_factory=list)

    def __post_init__(self):
        if not self.source_url:
            self.source_url = f"https://openstax.org/details/books/{self.slug}"

    @property
    def subject(self) -> str:
        """Map OpenStax style to academic subject."""
        mapping = {
            "python": "CMPT",
            "calculus": "MATH",
            "precalculus": "MATH",
            "dev-math": "MATH",
            "statistics": "STAT",
            "u-physics": "PHYS",
            "college-physics": "PHYS",
            "hs-physics": "PHYS",
            "ap-physics": "PHYS",
            "chemistry": "CHEM",
            "organic-chemistry": "CHEM",
            "biology": "BIOL",
            "microbiology": "BIOL",
            "anatomy": "BIOL",
            "psychology": "PSYC",
            "philosophy": "PHIL",
            "economics": "ECON",
            "sociology": "SOC",
            "history": "HIST",
        }
        return mapping.get(self.style, "GEN")


class OpenStaxClient:
    """
    Client for fetching OpenStax textbook data.

    Usage:
        async with OpenStaxClient() as client:
            books = await client.get_relevant_books()
            for book in books:
                print(f"{book.title} ({book.subject})")
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "knowledge-mapper" / "openstax"
        self._client: Optional[httpx.AsyncClient] = None
        self._books: Optional[list[OpenStaxBook]] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def get_all_books(self) -> list[OpenStaxBook]:
        """Fetch all approved OpenStax books."""
        if self._books is not None:
            return self._books

        # Try cache first
        cache_file = self.cache_dir / "approved-books.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                self._books = self._parse_approved_books(data)
                return self._books
            except (json.JSONDecodeError, KeyError):
                pass

        # Fetch from GitHub
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context.")

        response = await self._client.get(APPROVED_BOOKS_URL)
        response.raise_for_status()
        raw_data = response.json()

        # Extract books list from response
        if isinstance(raw_data, dict):
            data = raw_data.get("approved_books", [])
        else:
            data = raw_data

        # Cache response
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(data, indent=2))

        self._books = self._parse_approved_books(data)
        return self._books

    async def get_relevant_books(self) -> list[OpenStaxBook]:
        """Get books relevant to Saskatchewan post-secondary subjects."""
        all_books = await self.get_all_books()

        # Filter to relevant subjects and prefer latest editions
        relevant = {}
        for book in all_books:
            if book.style in RELEVANT_SUBJECTS:
                key = (book.style, book.slug.split("-")[0])
                existing = relevant.get(key)
                if existing is None or book.edition > existing.edition:
                    relevant[key] = book

        return list(relevant.values())

    async def get_book_by_slug(self, slug: str) -> Optional[OpenStaxBook]:
        """Get a specific book by its URL slug."""
        all_books = await self.get_all_books()
        for book in all_books:
            if book.slug == slug:
                return book
        return None

    def _parse_approved_books(self, data: list[dict]) -> list[OpenStaxBook]:
        """Parse the approved books list structure."""
        books = []
        seen_slugs = set()

        for repo_entry in data:
            repo_name = repo_entry.get("repository_name", "")
            versions = repo_entry.get("versions", [])

            # Get latest version's books
            if not versions:
                continue

            latest = versions[-1]
            commit_meta = latest.get("commit_metadata", {})
            edition = latest.get("edition", 1)

            for book_data in commit_meta.get("books", []):
                slug = book_data.get("slug", "")
                if slug and slug not in seen_slugs:
                    seen_slugs.add(slug)
                    books.append(OpenStaxBook(
                        uuid=book_data.get("uuid", ""),
                        title=self._slug_to_title(slug),
                        slug=slug,
                        style=book_data.get("style", ""),
                        repository=repo_name,
                        versions=len(versions),
                        edition=edition,
                    ))

        return books

    def _slug_to_title(self, slug: str) -> str:
        """Convert slug to readable title."""
        # Remove edition suffix and convert
        title = slug.replace("-", " ").title()
        # Fix common patterns
        title = title.replace(" 2e", " (2nd Edition)")
        title = title.replace(" 3e", " (3rd Edition)")
        return title

    def clear_cache(self):
        """Clear cached data."""
        if self.cache_dir.exists():
            for f in self.cache_dir.iterdir():
                f.unlink()


# Pre-defined chapter data for key textbooks (avoids web scraping)
# These are manually curated from OpenStax TOCs
KNOWN_CHAPTERS = {
    "introduction-python-programming": [
        OpenStaxChapter(1, "Statements", ["Introduction", "Input/output", "Variables", "Strings", "Numbers"]),
        OpenStaxChapter(2, "Expressions", ["Python shell", "Type conversion", "Math module"]),
        OpenStaxChapter(3, "Objects", ["Strings revisited", "Lists", "Tuples"]),
        OpenStaxChapter(4, "Decisions", ["Boolean values", "If-else", "Conditionals"]),
        OpenStaxChapter(5, "Loops", ["While loop", "For loop", "Nested loops"]),
        OpenStaxChapter(6, "Functions", ["Defining functions", "Parameters", "Return values"]),
        OpenStaxChapter(7, "Modules", ["Module basics", "Importing"]),
        OpenStaxChapter(8, "Strings", ["String operations", "Slicing", "Formatting"]),
        OpenStaxChapter(9, "Lists", ["Modifying lists", "List comprehensions"]),
        OpenStaxChapter(10, "Dictionaries", ["Dictionary basics", "Nested dictionaries"]),
        OpenStaxChapter(11, "Classes", ["OOP basics", "Instance methods"]),
        OpenStaxChapter(12, "Recursion", ["Recursion basics", "Math recursion"]),
        OpenStaxChapter(13, "Inheritance", ["Inheritance basics", "Multiple inheritance"]),
        OpenStaxChapter(14, "Files", ["Reading files", "Writing files", "CSV", "Exceptions"]),
        OpenStaxChapter(15, "Data Science", ["NumPy", "Pandas", "Visualization"]),
    ],
    "calculus-volume-1": [
        OpenStaxChapter(1, "Functions and Graphs", ["Review of functions", "Basic classes", "Trigonometric functions"]),
        OpenStaxChapter(2, "Limits", ["Limit of a function", "Epsilon-delta definition", "Continuity"]),
        OpenStaxChapter(3, "Derivatives", ["Derivative as a function", "Differentiation rules"]),
        OpenStaxChapter(4, "Applications of Derivatives", ["Related rates", "Linear approximations", "L'Hopital's rule"]),
        OpenStaxChapter(5, "Integration", ["Antiderivatives", "Definite integrals", "Fundamental theorem"]),
        OpenStaxChapter(6, "Applications of Integration", ["Areas between curves", "Volumes", "Physical applications"]),
    ],
    "college-algebra-2e": [
        OpenStaxChapter(1, "Prerequisites", ["Real numbers", "Exponents", "Polynomials", "Factoring"]),
        OpenStaxChapter(2, "Equations and Inequalities", ["Linear equations", "Quadratic equations"]),
        OpenStaxChapter(3, "Functions", ["Function notation", "Domain and range", "Composition"]),
        OpenStaxChapter(4, "Linear Functions", ["Slope", "Linear equations", "Fitting lines"]),
        OpenStaxChapter(5, "Polynomial and Rational Functions", ["Quadratic functions", "Power functions"]),
        OpenStaxChapter(6, "Exponential and Logarithmic Functions", ["Exponential functions", "Logarithms"]),
    ],
    "introductory-statistics-2e": [
        OpenStaxChapter(1, "Sampling and Data", ["Statistics terminology", "Sampling methods"]),
        OpenStaxChapter(2, "Descriptive Statistics", ["Measures of center", "Measures of spread"]),
        OpenStaxChapter(3, "Probability Topics", ["Probability rules", "Contingency tables"]),
        OpenStaxChapter(4, "Discrete Random Variables", ["Expected value", "Binomial distribution"]),
        OpenStaxChapter(5, "Continuous Random Variables", ["Normal distribution", "Z-scores"]),
        OpenStaxChapter(6, "The Central Limit Theorem", ["Sampling distributions"]),
        OpenStaxChapter(7, "Confidence Intervals", ["Point estimates", "Interval estimates"]),
        OpenStaxChapter(8, "Hypothesis Testing", ["Null hypothesis", "P-values"]),
    ],
    "university-physics-volume-1": [
        OpenStaxChapter(1, "Units and Measurement", ["SI units", "Unit conversions"]),
        OpenStaxChapter(2, "Vectors", ["Vector algebra", "Components"]),
        OpenStaxChapter(3, "Motion Along a Straight Line", ["Position", "Velocity", "Acceleration"]),
        OpenStaxChapter(4, "Motion in Two and Three Dimensions", ["Projectile motion"]),
        OpenStaxChapter(5, "Newton's Laws of Motion", ["Force", "Mass", "Laws of motion"]),
        OpenStaxChapter(6, "Applications of Newton's Laws", ["Friction", "Drag"]),
        OpenStaxChapter(7, "Work and Kinetic Energy", ["Work", "Kinetic energy theorem"]),
        OpenStaxChapter(8, "Potential Energy and Conservation", ["Conservative forces"]),
    ],
    "chemistry-2e": [
        OpenStaxChapter(1, "Essential Ideas", ["Chemistry overview", "Scientific method"]),
        OpenStaxChapter(2, "Atoms, Molecules, and Ions", ["Atomic theory", "Chemical formulas"]),
        OpenStaxChapter(3, "Composition of Substances", ["Formula mass", "Moles"]),
        OpenStaxChapter(4, "Stoichiometry", ["Balancing equations", "Reaction yields"]),
        OpenStaxChapter(5, "Thermochemistry", ["Energy in reactions", "Enthalpy"]),
        OpenStaxChapter(6, "Electronic Structure", ["Electromagnetic radiation", "Quantum theory"]),
    ],
    "biology-2e": [
        OpenStaxChapter(1, "The Study of Life", ["Science of biology", "Themes"]),
        OpenStaxChapter(2, "The Chemical Foundation of Life", ["Atoms", "Molecules"]),
        OpenStaxChapter(3, "Biological Macromolecules", ["Carbohydrates", "Proteins", "Nucleic acids"]),
        OpenStaxChapter(4, "Cell Structure", ["Prokaryotic and eukaryotic cells"]),
        OpenStaxChapter(5, "Structure and Function of Plasma Membranes", ["Membrane transport"]),
        OpenStaxChapter(6, "Metabolism", ["Energy", "Enzymes"]),
        OpenStaxChapter(7, "Cellular Respiration", ["Glycolysis", "Citric acid cycle"]),
        OpenStaxChapter(8, "Photosynthesis", ["Light reactions", "Calvin cycle"]),
    ],
    "psychology-2e": [
        OpenStaxChapter(1, "Introduction to Psychology", ["History", "Scientific method"]),
        OpenStaxChapter(2, "Psychological Research", ["Research methods", "Ethics"]),
        OpenStaxChapter(3, "Biopsychology", ["Brain and nervous system"]),
        OpenStaxChapter(4, "States of Consciousness", ["Sleep", "Dreams"]),
        OpenStaxChapter(5, "Sensation and Perception", ["Sensory processes"]),
        OpenStaxChapter(6, "Learning", ["Classical conditioning", "Operant conditioning"]),
        OpenStaxChapter(7, "Thinking and Intelligence", ["Cognition", "Problem solving"]),
        OpenStaxChapter(8, "Memory", ["Encoding", "Storage", "Retrieval"]),
    ],
}


def get_chapters_for_book(slug: str) -> list[OpenStaxChapter]:
    """Get chapter data for a known book."""
    return KNOWN_CHAPTERS.get(slug, [])


async def main():
    """Demo: List relevant OpenStax textbooks."""
    async with OpenStaxClient() as client:
        books = await client.get_relevant_books()
        print(f"Found {len(books)} relevant OpenStax textbooks:\n")

        for book in sorted(books, key=lambda b: b.subject):
            print(f"[{book.subject}] {book.title}")
            print(f"       Slug: {book.slug}")
            print(f"       UUID: {book.uuid}")

            chapters = get_chapters_for_book(book.slug)
            if chapters:
                print(f"       Chapters: {len(chapters)}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
