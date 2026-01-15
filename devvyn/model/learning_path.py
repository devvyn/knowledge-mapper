"""
Learning paths through open educational resources.

A learning path is an ordered sequence of textbook sections that leads
to understanding a concept - independent of institutional enrollment.

This enables:
- "Show me a path to learn recursion using free textbooks"
- "What's the fastest route to understanding calculus?"
- Alternative paths through different resources
"""
from dataclasses import dataclass, field
from typing import Optional

from devvyn.model.course_materials import Textbook, TextbookSection


@dataclass
class LearningPath:
    """
    An ordered sequence of learning steps to achieve a goal.

    Learning paths are institution-independent journeys through
    open educational resources toward understanding a concept.

    Graph representation:
        [Start] → Section_1 → Section_2 → ... → Section_N → [Goal: Concept]
    """
    id: str                             # Unique path identifier
    title: str                          # e.g., "Path to Understanding Recursion"
    goal_concept_id: str                # The concept this path leads to

    # Ordered steps
    steps: list[TextbookSection] = field(default_factory=list)

    # Metadata
    description: str = ""
    estimated_hours: float = 0.0        # Total time estimate
    difficulty: int = 1                 # 1=beginner, 2=intermediate, 3=advanced

    # Source tracking
    textbooks_required: list[str] = field(default_factory=list)  # ISBN list
    is_free: bool = True                # All resources are free?

    def __post_init__(self):
        """Calculate totals from steps."""
        if self.steps and not self.estimated_hours:
            self.estimated_hours = sum(s.estimated_minutes for s in self.steps) / 60
        if self.steps and not self.textbooks_required:
            self.textbooks_required = list({
                str(s.textbook_ref) for s in self.steps
            })

    def add_step(self, section: TextbookSection) -> None:
        """Add a section to the path."""
        self.steps.append(section)
        self.estimated_hours += section.estimated_minutes / 60
        ref_str = str(section.textbook_ref)
        if ref_str not in self.textbooks_required:
            self.textbooks_required.append(ref_str)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def __str__(self) -> str:
        return f"{self.title} ({self.step_count} steps, ~{self.estimated_hours:.1f}h)"


@dataclass
class PathStep:
    """
    A single step in a learning path with additional context.

    Wraps a TextbookSection with path-specific metadata.
    """
    section: TextbookSection
    order: int                          # Position in path (1-indexed)
    is_optional: bool = False           # Can be skipped?
    notes: str = ""                     # Why this step matters
    alternatives: list[TextbookSection] = field(default_factory=list)

    @property
    def has_alternatives(self) -> bool:
        return len(self.alternatives) > 0


@dataclass
class LearningPathBuilder:
    """
    Builder for constructing learning paths from graph traversal.

    Used when generating paths from the curriculum graph.
    """
    goal_concept_id: str
    _sections: list[TextbookSection] = field(default_factory=list)
    _title: Optional[str] = None

    def add_section(self, section: TextbookSection) -> "LearningPathBuilder":
        """Add a section to the path being built."""
        self._sections.append(section)
        return self

    def set_title(self, title: str) -> "LearningPathBuilder":
        """Set the path title."""
        self._title = title
        return self

    def build(self) -> LearningPath:
        """Build the final LearningPath."""
        title = self._title or f"Path to {self.goal_concept_id}"
        path_id = f"path-{self.goal_concept_id}-{len(self._sections)}"

        return LearningPath(
            id=path_id,
            title=title,
            goal_concept_id=self.goal_concept_id,
            steps=self._sections.copy(),
        )


def find_shortest_path_to_concept(
    concept_id: str,
    available_sections: list[TextbookSection],
    concept_prerequisites: dict[str, list[str]],
) -> Optional[LearningPath]:
    """
    Find the shortest learning path to a concept.

    Uses BFS through concept prerequisites to find the minimal
    set of sections needed.

    Args:
        concept_id: Target concept to learn
        available_sections: Sections that can teach concepts
        concept_prerequisites: Map of concept → prerequisite concepts

    Returns:
        LearningPath if found, None otherwise
    """
    # Build section-to-concept mapping
    section_teaches: dict[str, list[str]] = {}
    for section in available_sections:
        for topic in section.topics:
            topic_id = topic.lower().replace(" ", "-")
            if topic_id not in section_teaches:
                section_teaches[topic_id] = []
            section_teaches[topic_id].append(section)

    # BFS to find required concepts
    required_concepts = [concept_id]
    visited = {concept_id}
    queue = [concept_id]

    while queue:
        current = queue.pop(0)
        for prereq in concept_prerequisites.get(current, []):
            if prereq not in visited:
                visited.add(prereq)
                required_concepts.append(prereq)
                queue.append(prereq)

    # Reverse to get learning order (prerequisites first)
    required_concepts.reverse()

    # Find sections for each required concept
    builder = LearningPathBuilder(concept_id)
    for concept in required_concepts:
        sections = section_teaches.get(concept, [])
        if sections:
            # Pick first available section (could optimize for shortest/free)
            builder.add_section(sections[0])

    if builder._sections:
        return builder.build()
    return None
