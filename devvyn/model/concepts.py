"""
Learning concepts that bridge courses, textbooks, and knowledge paths.

Concepts are abstract knowledge units (e.g., "recursion", "linear algebra")
that can be taught by multiple sources and are required by multiple courses.

This enables:
- "I want to learn recursion" → paths through different textbooks
- "What concepts does CMPT 145 require?" → prerequisite knowledge
- "Which open textbooks teach calculus?" → alternative resources
"""
from dataclasses import dataclass, field
from typing import Optional

from devvyn.institutions.base import CourseReference
from devvyn.model.course_materials import TextbookReference, TextbookSection


@dataclass
class LearningConcept:
    """
    An abstract knowledge concept that spans textbooks and courses.

    Concepts are derived from textbook chapter titles and learning objectives.
    They form the semantic layer connecting institutional courses to open resources.

    Graph relationships:
        TextbookSection ──teaches──► Concept
        Course ──requires──► Concept
        Concept ──prerequisite_of──► Concept
    """
    id: str                             # Slug identifier (e.g., "recursion")
    name: str                           # Display name (e.g., "Recursion")
    description: str = ""               # Brief description

    # Subject area (maps to academic subjects)
    subject: str = ""                   # e.g., "CMPT", "MATH"

    # Difficulty/level
    level: int = 1                      # 1=intro, 2=intermediate, 3=advanced

    # Aliases for search/matching
    aliases: list[str] = field(default_factory=list)

    # Topics covered (for matching with textbook sections)
    topics: list[str] = field(default_factory=list)

    def matches(self, query: str) -> bool:
        """Check if this concept matches a search query."""
        query_lower = query.lower()
        # Check both directions: query in concept OR concept in query
        if query_lower in self.id.lower() or self.id.lower() in query_lower:
            return True
        if query_lower in self.name.lower() or self.name.lower() in query_lower:
            return True
        for alias in self.aliases:
            if query_lower in alias.lower() or alias.lower() in query_lower:
                return True
        for topic in self.topics:
            if query_lower in topic.lower() or topic.lower() in query_lower:
                return True
        return False

    def __str__(self) -> str:
        return self.name


@dataclass
class ConceptSource:
    """
    A source that teaches a concept (textbook section, video, etc.).

    Links concepts to their teaching materials.
    """
    concept_id: str
    section: TextbookSection
    coverage: str = "full"              # "full", "partial", "introduction"
    notes: str = ""                     # Additional context

    @property
    def id(self) -> str:
        return f"{self.concept_id}:{self.section.id}"


@dataclass
class ConceptRequirement:
    """
    A course's requirement for a concept.

    Links courses to the concepts they require students to know.
    """
    course_ref: CourseReference
    concept_id: str
    is_prerequisite: bool = True        # Required before vs learned during
    notes: str = ""

    @property
    def id(self) -> str:
        return f"{self.course_ref}:requires:{self.concept_id}"


# Pre-defined concepts for CS/Math (derived from OpenStax Python TOC)
# These will be expanded by parsing textbook TOCs
SEED_CONCEPTS = [
    # Programming fundamentals
    LearningConcept("variables", "Variables", "Storing and naming values", "CMPT", 1,
                    aliases=["variable", "assignment"],
                    topics=["variables", "assignment", "naming"]),
    LearningConcept("expressions", "Expressions", "Combining values and operators", "CMPT", 1,
                    aliases=["operators", "arithmetic"],
                    topics=["expressions", "operators", "arithmetic"]),
    LearningConcept("conditionals", "Conditionals", "Decision making in code", "CMPT", 1,
                    aliases=["if-else", "branching", "decisions"],
                    topics=["if", "else", "boolean", "conditions"]),
    LearningConcept("loops", "Loops", "Repeating code execution", "CMPT", 1,
                    aliases=["iteration", "while", "for"],
                    topics=["loops", "while", "for", "iteration"]),
    LearningConcept("functions", "Functions", "Reusable code blocks", "CMPT", 1,
                    aliases=["methods", "procedures", "subroutines"],
                    topics=["functions", "parameters", "return"]),
    LearningConcept("recursion", "Recursion", "Functions that call themselves", "CMPT", 2,
                    aliases=["recursive"],
                    topics=["recursion", "base case", "recursive case"]),
    LearningConcept("oop", "Object-Oriented Programming", "Classes and objects", "CMPT", 2,
                    aliases=["classes", "objects", "OOP"],
                    topics=["class", "object", "instance", "method"]),
    LearningConcept("inheritance", "Inheritance", "Class hierarchies and code reuse", "CMPT", 2,
                    topics=["inheritance", "subclass", "superclass", "polymorphism"]),
    LearningConcept("data-structures", "Data Structures", "Organizing data efficiently", "CMPT", 2,
                    aliases=["lists", "dictionaries", "arrays"],
                    topics=["list", "dictionary", "array", "stack", "queue"]),
    LearningConcept("file-io", "File I/O", "Reading and writing files", "CMPT", 1,
                    aliases=["files", "input/output"],
                    topics=["file", "read", "write", "open", "close"]),

    # Math concepts
    LearningConcept("algebra", "Algebra", "Symbolic mathematics", "MATH", 1,
                    aliases=["algebraic"],
                    topics=["equations", "variables", "polynomials"]),
    LearningConcept("linear-algebra", "Linear Algebra", "Vectors and matrices", "MATH", 2,
                    aliases=["matrices", "vectors"],
                    topics=["vector", "matrix", "linear transformation"]),
    LearningConcept("calculus", "Calculus", "Rates of change and accumulation", "MATH", 2,
                    aliases=["derivatives", "integrals"],
                    topics=["derivative", "integral", "limit"]),
    LearningConcept("statistics", "Statistics", "Data analysis and probability", "STAT", 1,
                    aliases=["probability", "data analysis"],
                    topics=["mean", "median", "standard deviation", "probability"]),

    # Science concepts
    LearningConcept("mechanics", "Mechanics", "Motion and forces", "PHYS", 1,
                    topics=["force", "motion", "velocity", "acceleration"]),
    LearningConcept("thermodynamics", "Thermodynamics", "Heat and energy", "PHYS", 2,
                    topics=["heat", "energy", "entropy", "temperature"]),
    LearningConcept("chemistry-basics", "Chemistry Basics", "Atoms and molecules", "CHEM", 1,
                    topics=["atom", "molecule", "element", "compound"]),
    LearningConcept("biology-basics", "Biology Basics", "Life sciences fundamentals", "BIOL", 1,
                    topics=["cell", "organism", "evolution", "genetics"]),
]


def get_seed_concepts() -> list[LearningConcept]:
    """Get pre-defined seed concepts."""
    return SEED_CONCEPTS.copy()


def derive_concepts_from_sections(sections: list[TextbookSection]) -> list[LearningConcept]:
    """
    Derive learning concepts from textbook section titles and topics.

    This is the main mechanism for building the concept ontology organically
    from textbook TOCs.
    """
    concepts = []
    seen_ids = {c.id for c in SEED_CONCEPTS}

    for section in sections:
        # Check if any topic matches an existing concept
        for topic in section.topics:
            concept_id = topic.lower().replace(" ", "-")
            if concept_id not in seen_ids:
                seen_ids.add(concept_id)
                concepts.append(LearningConcept(
                    id=concept_id,
                    name=topic.title(),
                    description=f"Derived from: {section.title}",
                    topics=[topic],
                ))

    return concepts
