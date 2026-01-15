"""
Degree progress analyzer.

Supports queries like:
- What's my progress toward degree X?
- What degrees can I complete with my current courses?
- What's the most efficient path to multiple degrees?
"""
from dataclasses import dataclass, field
from typing import Optional

from devvyn.degrees.models import (
    DegreeProgram,
    RequirementBlock,
    CoursePool,
    CredentialType,
)
from devvyn.degrees.usask import get_usask_programs, get_program


@dataclass
class RequirementSatisfaction:
    """How well a requirement block is satisfied."""
    block: RequirementBlock
    credits_required: float
    credits_satisfied: float
    courses_used: list[str]
    courses_remaining_options: list[str]

    @property
    def percentage(self) -> float:
        if self.credits_required == 0:
            return 100.0
        return min(100.0, (self.credits_satisfied / self.credits_required) * 100)

    @property
    def is_complete(self) -> bool:
        return self.credits_satisfied >= self.credits_required


@dataclass
class DegreeProgress:
    """Progress toward completing a degree."""
    program: DegreeProgram
    completed_courses: set[str]

    # Per-block satisfaction
    block_progress: list[RequirementSatisfaction] = field(default_factory=list)

    # Summary
    total_credits_earned: float = 0.0
    total_credits_needed: float = 0.0
    completion_percentage: float = 0.0
    courses_still_needed: list[str] = field(default_factory=list)
    is_complete: bool = False


@dataclass
class DegreeStackAnalysis:
    """Analysis of degree stacking potential."""
    base_courses: set[str]
    achievable_degrees: list[tuple[DegreeProgram, DegreeProgress]]
    shared_courses: dict[str, list[str]]  # course -> list of program IDs
    optimal_additions: list[tuple[str, list[str]]]  # course -> degrees it helps


class DegreeAnalyzer:
    """
    Analyzes degree progress and stacking opportunities.
    """

    def __init__(self, programs: Optional[list[DegreeProgram]] = None):
        self.programs = programs or get_usask_programs()
        self._program_by_id = {p.id: p for p in self.programs}

    def get_program(self, program_id: str) -> Optional[DegreeProgram]:
        """Get a program by ID."""
        return self._program_by_id.get(program_id)

    def calculate_progress(
        self,
        program: DegreeProgram | str,
        completed_courses: set[str],
    ) -> DegreeProgress:
        """
        Calculate progress toward a specific degree.

        Args:
            program: Program or program ID
            completed_courses: Set of completed course codes (e.g., {"CMPT 141", "MATH 110"})

        Returns:
            DegreeProgress with detailed breakdown
        """
        if isinstance(program, str):
            prog = self.get_program(program)
            if not prog:
                raise ValueError(f"Unknown program: {program}")
            program = prog

        # Normalize course codes (remove credit suffixes like ".3")
        completed = {self._normalize_course(c) for c in completed_courses}

        progress = DegreeProgress(
            program=program,
            completed_courses=completed,
        )

        total_earned = 0.0
        total_needed = program.total_credits
        courses_still_needed = []

        for block in program.requirements:
            satisfaction = self._evaluate_block(block, completed)
            progress.block_progress.append(satisfaction)
            total_earned += satisfaction.credits_satisfied
            courses_still_needed.extend(satisfaction.courses_remaining_options[:5])

        progress.total_credits_earned = min(total_earned, total_needed)
        progress.total_credits_needed = total_needed
        progress.completion_percentage = (progress.total_credits_earned / total_needed) * 100
        progress.courses_still_needed = courses_still_needed[:10]
        progress.is_complete = progress.completion_percentage >= 100.0

        return progress

    def _normalize_course(self, code: str) -> str:
        """Normalize course code by removing credit suffix."""
        # "CMPT 141.3" -> "CMPT 141"
        # "CMPT 141" -> "CMPT 141"
        parts = code.split(".")
        return parts[0].strip().upper()

    def _evaluate_block(
        self,
        block: RequirementBlock,
        completed: set[str],
    ) -> RequirementSatisfaction:
        """Evaluate how well a requirement block is satisfied."""
        credits_satisfied = 0.0
        courses_used = []
        remaining_options = []

        # Check required courses
        for req in block.required_courses:
            norm_code = self._normalize_course(req.code)
            if norm_code in completed:
                credits_satisfied += req.credits
                courses_used.append(norm_code)
            else:
                remaining_options.append(norm_code)

        # Check course pools
        for pool in block.course_pools:
            pool_satisfied = 0.0
            for course_req in pool.courses:
                norm_code = self._normalize_course(course_req.code)
                if norm_code in completed and pool_satisfied < pool.pick_credits:
                    pool_satisfied += course_req.credits
                    courses_used.append(norm_code)
                elif norm_code not in completed:
                    remaining_options.append(norm_code)

            credits_satisfied += pool_satisfied

        # Check subject requirements (simplified - count any matching courses)
        for subj_req in block.subject_requirements:
            subj_satisfied = 0.0
            for course in completed:
                course_subj = course.split()[0] if " " in course else course[:4]
                if course_subj in subj_req.subjects and subj_satisfied < subj_req.credits:
                    subj_satisfied += 3.0  # Assume 3cu per course
                    courses_used.append(course)
            credits_satisfied += subj_satisfied

        return RequirementSatisfaction(
            block=block,
            credits_required=block.total_credits,
            credits_satisfied=min(credits_satisfied, block.total_credits),
            courses_used=courses_used,
            courses_remaining_options=remaining_options,
        )

    def find_achievable_degrees(
        self,
        completed_courses: set[str],
        min_progress: float = 25.0,
        credential_types: Optional[list[CredentialType]] = None,
    ) -> list[tuple[DegreeProgram, DegreeProgress]]:
        """
        Find all degrees achievable with given courses.

        Args:
            completed_courses: Courses already completed
            min_progress: Minimum completion percentage to include (default 25%)
            credential_types: Filter by credential type (default: all)

        Returns:
            List of (program, progress) tuples, sorted by completion percentage
        """
        results = []

        for program in self.programs:
            if credential_types and program.credential not in credential_types:
                continue

            progress = self.calculate_progress(program, completed_courses)
            if progress.completion_percentage >= min_progress:
                results.append((program, progress))

        # Sort by completion percentage (highest first)
        results.sort(key=lambda x: x[1].completion_percentage, reverse=True)
        return results

    def analyze_degree_stacking(
        self,
        completed_courses: set[str],
        target_credentials: Optional[list[CredentialType]] = None,
    ) -> DegreeStackAnalysis:
        """
        Analyze opportunities to stack multiple degrees.

        Identifies:
        - Which degrees are achievable
        - Which courses count toward multiple degrees
        - Most valuable courses to add for multi-degree completion
        """
        if target_credentials is None:
            target_credentials = [
                CredentialType.BACHELOR_3YR,
                CredentialType.BACHELOR_4YR,
                CredentialType.HONOURS,
                CredentialType.MINOR,
            ]

        # Find achievable degrees
        achievable = self.find_achievable_degrees(
            completed_courses,
            min_progress=10.0,
            credential_types=target_credentials,
        )

        # Track which courses help which programs
        course_to_programs: dict[str, list[str]] = {}
        for program, progress in achievable:
            for block_prog in progress.block_progress:
                for course in block_prog.courses_used:
                    if course not in course_to_programs:
                        course_to_programs[course] = []
                    if program.id not in course_to_programs[course]:
                        course_to_programs[course].append(program.id)

        # Find shared courses (count toward 2+ programs)
        shared = {c: progs for c, progs in course_to_programs.items() if len(progs) > 1}

        # Find most valuable courses to add
        optimal_additions = self._find_optimal_additions(
            completed_courses,
            achievable,
        )

        return DegreeStackAnalysis(
            base_courses=completed_courses,
            achievable_degrees=achievable,
            shared_courses=shared,
            optimal_additions=optimal_additions,
        )

    def _find_optimal_additions(
        self,
        completed: set[str],
        achievable: list[tuple[DegreeProgram, DegreeProgress]],
    ) -> list[tuple[str, list[str]]]:
        """Find courses that would help the most programs."""
        course_value: dict[str, list[str]] = {}

        for program, progress in achievable:
            if progress.completion_percentage >= 90:
                # Near completion - which courses finish it?
                for block_prog in progress.block_progress:
                    for course in block_prog.courses_remaining_options[:5]:
                        if course not in completed:
                            if course not in course_value:
                                course_value[course] = []
                            course_value[course].append(program.id)

        # Sort by number of programs helped
        sorted_courses = sorted(
            course_value.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )

        return sorted_courses[:10]

    def format_progress_report(self, progress: DegreeProgress) -> str:
        """Format a progress report as readable text."""
        lines = [
            f"# Progress: {progress.program.name}",
            f"",
            f"**Overall:** {progress.completion_percentage:.1f}% complete",
            f"**Credits:** {progress.total_credits_earned:.0f} / {progress.total_credits_needed:.0f}",
            f"",
            "## Requirements Breakdown",
        ]

        for block_prog in progress.block_progress:
            status = "✓" if block_prog.is_complete else "○"
            lines.append(
                f"- {status} **{block_prog.block.code} {block_prog.block.name}**: "
                f"{block_prog.credits_satisfied:.0f}/{block_prog.credits_required:.0f} cu "
                f"({block_prog.percentage:.0f}%)"
            )

        if progress.courses_still_needed:
            lines.append("")
            lines.append("## Suggested Next Courses")
            for course in progress.courses_still_needed[:5]:
                lines.append(f"- {course}")

        return "\n".join(lines)

    def format_stacking_report(self, analysis: DegreeStackAnalysis) -> str:
        """Format a degree stacking analysis as readable text."""
        lines = [
            "# Degree Stacking Analysis",
            f"",
            f"Based on {len(analysis.base_courses)} completed courses.",
            "",
            "## Achievable Degrees",
        ]

        for program, progress in analysis.achievable_degrees:
            emoji = "🎓" if progress.completion_percentage >= 90 else "📚"
            lines.append(
                f"- {emoji} **{program.name}**: {progress.completion_percentage:.0f}%"
            )

        if analysis.shared_courses:
            lines.append("")
            lines.append("## Multi-Degree Courses")
            lines.append("These courses count toward multiple programs:")
            for course, programs in sorted(
                analysis.shared_courses.items(),
                key=lambda x: len(x[1]),
                reverse=True,
            )[:10]:
                prog_names = [self._program_by_id[p].name.split(" - ")[-1] for p in programs]
                lines.append(f"- **{course}**: {', '.join(prog_names)}")

        if analysis.optimal_additions:
            lines.append("")
            lines.append("## High-Value Courses to Add")
            lines.append("Taking these would advance multiple degrees:")
            for course, programs in analysis.optimal_additions[:5]:
                prog_names = [self._program_by_id[p].name.split(" - ")[-1] for p in programs]
                lines.append(f"- **{course}**: helps {', '.join(prog_names)}")

        return "\n".join(lines)
