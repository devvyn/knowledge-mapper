"""
Test model instances for program dictionary classes.
"""

import pytest

import devvyn.model.program_catalogue


class TestProgramCatalogue:

    def test_program_catalogue_contains_study_levels(self, catalogue):
        catalogue_children = catalogue.values()
        assert len(catalogue_children) > 0, 'no children in catalogue'
        assert all(
            isinstance(child, devvyn.model.program_catalogue.AcademicLevel)
            for child in catalogue_children
        ), f'dictionary contains non-study level object'

    def test_program_catalogue_field_pages_parsed(self, catalogue):
        """
        Verify that known fields can be parsed for programs.

        Tests specific fields known to have programs, rather than
        iterating all fields (which is slow and hits the server).
        """
        undergrad = catalogue.get("Undergraduate")
        assert undergrad is not None

        # Computer Science should have programs
        cs = undergrad.data.get("Computer Science")
        assert cs is not None, "Computer Science field not found"
        assert len(cs.programs) > 0, "Computer Science has no programs"

        # Check a few program names exist
        program_names = list(cs.programs.keys())
        assert any("Bachelor" in name for name in program_names), (
            "No Bachelor programs found in Computer Science"
        )

    @pytest.fixture
    def catalogue(self):
        # @todo use mock content for ProgramCatalogue instantiation
        return devvyn.model.program_catalogue.ProgramCatalogue()
