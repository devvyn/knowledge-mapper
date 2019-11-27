import pytest


class TestProgramCatalogue:

    def test_program_catalogue_all_field_pages_parsed(self, catalogue):
        for level, fields in catalogue.items():
            for field, programs in fields.items():
                assert programs, f'empty collection at {level=}, {field=}'

    @pytest.fixture
    def catalogue(self):
        from scrape.model.program_catalogue import ProgramCatalogue
        return ProgramCatalogue()
