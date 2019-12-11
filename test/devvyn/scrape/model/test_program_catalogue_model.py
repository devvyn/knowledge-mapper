"""
Test model instances for program dictionary classes.
"""

import pytest

import devvyn.model.program_catalogue


class TestProgramCatalogue:

    def test_program_catalogue_contains_study_levels(self, catalogue):
        catalogue_children = catalogue.values()
        assert len(catalogue_children) > 0, f'dictionary contains non-study level object'
        assert all(
            isinstance(child, devvyn.model.program_catalogue.AcademicLevel)
            for child in catalogue_children
        )

    def test_program_catalogue_all_field_pages_parsed(self, catalogue):
        assert len(catalogue) > 0
        for level, fields in catalogue.items():
            for field, programs in fields.items():
                assert len(programs) > 0, f'empty collection at {level=}, {field=}'

    @pytest.fixture
    def catalogue(self):
        # @todo use mock content for ProgramCatalogue instantiation
        return devvyn.model.program_catalogue.ProgramCatalogue()
