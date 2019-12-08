""" Data object for usask academic program catalogue. """

import devvyn.scrape.model.core
import devvyn.scrape.page.fields_at_levels


# @todo: implement tests


class ProgramCatalogue(devvyn.scrape.model.core.SourceMapping):
    """
    Represent scraped data, with the list of study levels at the root and
    courses as the leaf nodes
    """

    def __init__(self, src: str = None) -> None:
        if src is not None:
            url_ = str(src)
        else:
            url_ = devvyn.scrape.page.fields_at_levels.get_fields_url()
        super().__init__(url_)
        study_fields = devvyn.scrape.page.fields_at_levels.get_all_fields(self.src)
        self.data = {
            level: AcademicLevel(name=level, data=field_map,
                                 src=self.src)
            for level, field_map in study_fields.items()
        }


class AcademicLevel(devvyn.scrape.model.core.NamedSource):
    """
    Represents an academic level, which has a parent institution and child fields.

    """

    def __init__(self, name: str, data: dict, src: str):
        super(AcademicLevel, self).__init__(name=name, src=src)
        level = name
        self.data = {
            field: AcademicField(level, field, src, ) for field, src in data.items()
        }


class AcademicField(devvyn.scrape.model.core.NamedSource):
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


class AcademicProgram(devvyn.scrape.model.core.NamedSource):
    """ Program in a field of study. """
    # @todo: make lazy
    # @todo: make separate dataclass and logic class
    pass


def main():
    assert ProgramCatalogue()


if __name__ == '__main__':
    main()

