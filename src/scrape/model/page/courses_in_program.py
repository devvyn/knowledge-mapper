import itertools
from typing import Iterable, Optional

from scrape.fetch import get_content
from scrape.model.page.fields_at_levels import get_all_fields
from scrape.model.page.programs_in_field_at_level import get_programs_url
from scrape.parse import parse_programs


def first_field_matching(program):
    all_fields: dict = get_all_fields()
    sections_children: Iterable[dict] = itertools.chain(all_fields.values())
    fields_list = (
        value
        for program_pages in sections_children
        for key, value in program_pages.items()
        if key == program
    )
    return next(fields_list)


def get_program_page(program: str, field: str = None,
                     level: str = None) -> str:
    """
    For given program, return the content of the program's page in the
    course catalogue. Lookup is done on data returned by sibling methods
    until a reasonable or exact match is found, or the search is exhausted.
    If the field is provided, shortcut the lookup by trying to match
    programs associated with the given field only.

    :param level: Optional. Level of study (Undergraduate, Graduate,
    Non-degree)
    :param field: Optional. Field of study
    :param program: Program name
    :return: HTML content from first found page
    :raises KeyError: Program or field cannot be found
    """
    if level is None:
        # try to infer the level from the program name
        level = infer_level(program)
        if field is None:
            # try to infer the field of study from the program name
            field_str = infer_field(program)
            if field_str is not None:
                # confirm that field_str leads to page with matching program
                try:
                    program_page_url = attempt_get_program_page_url(field_str,
                                                                    level)
                except KeyError as e:
                    raise e

            # must search everywhere in given level!
            # find the program on the page for the field at the appropriate
            # level
            url = first_field_matching(program)
    content = get_content(url)
    return content


def attempt_get_program_page_url(field_str, level):
    field_candidate = field_str
    # @todo: try get and check
    field_candidate_url = get_programs_url(level, field_candidate)
    field_candidate_content = get_content(
        field_candidate_url)
    field_candidate_data = parse_programs(field_candidate_content,
                                          field_candidate_url)
    if field_str in field_candidate_data.keys():
        return field_candidate_data[field_str]


def infer_field(program: str, sep: str = " - ") -> Optional[str]:
    """
    Try to find a field of study in the program name. Assume the field of
    study is named after the given separator.

    :param program: The name of the program
    :param sep: Separator to use for splitting `program`
    :return:
    """
    program_str, field_str = program.split(sep, maxsplit=2)
    return field_str


def infer_level(program_str):
    bachelor = 'Bachelor'
    undergrad = 'Undergraduate'
    master = 'Master'
    grad = 'Graduate'
    phd = 'Doctor'
    levels = {
        bachelor: undergrad,
        master: grad,
        phd: grad,
    }
    level_str = levels[program_str.split(maxsplit=2)[0]]
    return level_str
