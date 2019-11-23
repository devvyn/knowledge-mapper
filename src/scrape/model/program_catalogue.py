from scrape.fetch import get_content
from scrape.model.core import NamedSource, SourceMapping
from scrape.page.fields_at_levels import get_all_fields, get_fields_url
from scrape.page.programs_in_field_at_level import (get_programs,
                                                    get_programs_url)


class ProgramCatalogue(SourceMapping):
    """
    Represent scraped data, with the list of study levels at the root and
    courses as the leaf nodes
    """

    def __init__(self, src: str = None) -> None:
        if src is not None:
            url_ = str(src)
        else:
            url_ = get_fields_url()
        super().__init__(url_)
        root = get_all_fields(self.src)
        # self.data = root
        self.data = {
            level: {
                field: Field(level, field, src, ) for field, src in
                field_map.items()
            }
            for level, field_map in root.items()
        }


class Field(NamedSource):
    """ Field of study. """

    def __init__(self, level: str, name: str, src: str) -> None:
        super().__init__(name, src)
        if level is None:
            raise TypeError(level)
        self.level = level
        base_href = get_programs_url(level, name)
        content = get_content(base_href)
        self.data = get_programs(content, base_href)


class Program(NamedSource):
    """ Program in a field of study. """
    pass
