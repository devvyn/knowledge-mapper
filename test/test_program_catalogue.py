import pytest


class TestProgramCatalogue:

    def test_program_catalogue_contains_study_levels(self, catalogue):
        assert all(
            isinstance(child, StudyField) for child in catalogue.values())

    def test_program_catalogue_all_field_pages_parsed(self, catalogue):
        for level, fields in catalogue.items():
            for field, programs in fields.items():
                assert programs, f'empty collection at {level=}, {field=}'

    @pytest.fixture
    # @todo: use mock
    def catalogue(self):
        from devvyn.scrape.model.program_catalogue import ProgramCatalogue
        return ProgramCatalogue()


class TestStudyLevel:
    def test_study_level_contains_fields(self, level):
        assert all(
            isinstance(child, Field) for child in level.values())

    @pytest.fixture
    def level(self):
        return StudyLevel()
