""" Data object for usask academic program catalogue. """

import scrape.fetch
import scrape.model.core
import scrape.page.fields_at_levels
import scrape.page.programs_in_field_at_level


# @todo: implement tests


class ProgramCatalogue(scrape.model.core.SourceMapping):
    """
    Represent scraped data, with the list of study levels at the root and
    courses as the leaf nodes
    """

    # @todo: make lazy
    # @todo: make separate dataclass and logic class
    def __init__(self, src: str = None) -> None:
        if src is not None:
            url_ = str(src)
        else:
            url_ = scrape.page.fields_at_levels.get_fields_url()
        super().__init__(url_)
        root = scrape.page.fields_at_levels.get_all_fields(self.src)
        # self.data = root
        self.data = {
            level: {
                field: Field(level, field, src, ) for field, src in
                field_map.items()
            }
            for level, field_map in root.items()
        }


class Field(scrape.model.core.NamedSource):
    """ Field of study. """

    # @todo: make separate dataclass and logic class
    def __init__(self, level: str, name: str, src: str) -> None:
        super().__init__(name, src)
        if level is None:
            raise TypeError(level)
        self.level = level

        # @todo: use src
        base_href = scrape.page.programs_in_field_at_level.get_programs_url(
            level, name)
        # @todo: make lazy
        content = scrape.fetch.get_content(base_href)
        self.data = scrape.page.programs_in_field_at_level.get_programs(
            content, base_href)
        self.data = {}


class Program(scrape.model.core.NamedSource):
    """ Program in a field of study. """
    # @todo: make lazy
    # @todo: make separate dataclass and logic class
    pass


def main():
    assert ProgramCatalogue()


if __name__ == '__main__':
    main()
