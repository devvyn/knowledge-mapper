"""
Test model instances for program catalogue classes.
"""

import pytest

import devvyn.scrape.model.program_catalogue


class TestProgramCatalogue:

    def test_program_catalogue_contains_study_levels(self, catalogue):
        assert all(
            isinstance(child, devvyn.scrape.model.program_catalogue.AcademicLevel)
            for child in catalogue.values()
        ) and len(catalogue) > 0, f'catalogue contains non-study level object'

    def test_program_catalogue_all_field_pages_parsed(self, catalogue):
        assert len(catalogue) > 0
        for level, fields in catalogue.items():
            for field, programs in fields.items():
                assert len(programs) > 0, f'empty collection at {level=}, {field=}'

    @pytest.fixture
    def catalogue(self):
        # @todo: use mock
        return devvyn.scrape.model.program_catalogue.ProgramCatalogue()
