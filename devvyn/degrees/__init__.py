"""
Degree requirements modeling for Saskatchewan post-secondary institutions.

Supports:
- Degree requirement definitions (major, minor, honours)
- Requirement satisfaction checking
- "What degrees can I get?" queries
- Degree stacking optimization
"""
from devvyn.degrees.models import (
    DegreeProgram,
    RequirementBlock,
    CourseRequirement,
    CoursePool,
    CredentialType,
)
from devvyn.degrees.usask import get_usask_programs
from devvyn.degrees.analyzer import DegreeAnalyzer

__all__ = [
    "DegreeProgram",
    "RequirementBlock",
    "CourseRequirement",
    "CoursePool",
    "CredentialType",
    "get_usask_programs",
    "DegreeAnalyzer",
]
