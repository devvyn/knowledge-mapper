""" Data object for academic program dictionary. """
import devvyn.scrape.page.usask
import devvyn.scrape.page.usask.program_catalogue
from devvyn.model.base import NamedSource, SourceMapping
from devvyn.scrape.page.usask.field import field_data
from devvyn.scrape.page.usask.program import parse_program


class ProgramCatalogue(SourceMapping):
    """
    Represent scraped data, with the list of study levels at the root and
    courses as the leaf nodes
    """

    def __init__(self, src: str = None) -> None:
        if src is not None:
            url_ = str(src)
        else:
            url_ = devvyn.scrape.page.usask.program_catalogue.URL_USASK_PROGRAMS_LIST
        super().__init__(url_)
        program_catalogue = self.levels
        self.data = {
            level: AcademicLevel(src=self.src, name=level, data=field_map)
            for level, field_map in program_catalogue.items()
        }

    @property
    def levels(self) -> dict:
        src = self.src
        levels = devvyn.scrape.page.usask.program_catalogue.program_catalogue_data(src)
        return levels


class AcademicLevel(NamedSource):
    """
    Represents an academic level, which has a parent institution and child fields.

    """

    def __init__(self, src: str, name: str, data: dict):
        super().__init__(name=name, src=src)
        level = name
        self.data = {
            field: AcademicField(level, field, src, ) for field, src in data.items()
        }


class AcademicField(NamedSource):
    """ Represents an academic field of study, with a parent level and child programs. """

    # @todo: make separate dataclass and logic class
    def __init__(self, level: str, name: str, src: str) -> None:
        super().__init__(name, src)
        self.level = level

        # @todo: use src
        # base_href = scrape.page.programs_in_field_at_level.get_programs_url(
        #     level, name)
        # @todo: make lazy
        # content = scrape.fetch.get_content(base_href)
        # self.data = scrape.page.programs_in_field_at_level.get_programs(
        #     content, base_href)
        self.data = {}


class AcademicProgram(NamedSource):
    """ Program in a field of study. """
    # @todo: make lazy
    # @todo: make separate dataclass and logic class
    pass


def main():
    catalogue = ProgramCatalogue()
    assert catalogue
    logging.info(catalogue)


if __name__ == '__main__':
    import logging
    from logging import INFO

    logging.basicConfig(level=INFO)

    main()


def get_programs(content, base_href) -> dict:
    """
    Academic field data, a list of programs on this page.

    :param content:
    :param base_href:
    :return:
    """
    return field_data(content, base_href)


def get_program_data(content: str) -> dict:
    """
    Program data.

    :param content:
    :return: dict-like collection of program data
    """
    # @todo: explicitly document/stub data structures this function may return
    return parse_program(content)
