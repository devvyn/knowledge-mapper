"""
Multi-institution support for educational data.

Provides a unified interface for querying courses, programs, and prerequisites
across different post-secondary institutions.
"""
from devvyn.institutions.base import (
    Institution,
    UnifiedCourse,
    UnifiedProgram,
    CourseReference,
)
from devvyn.institutions.registry import (
    InstitutionRegistry,
    get_registry,
    get_institution,
)

__all__ = [
    "Institution",
    "UnifiedCourse",
    "UnifiedProgram",
    "CourseReference",
    "InstitutionRegistry",
    "get_registry",
    "get_institution",
]
