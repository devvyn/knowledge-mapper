from scrape.fetch import get_content
from scrape.page.programs_in_field_at_level import get_programs_url
from scrape.parse import parse_programs


def get_program_page(program: str, field: str, level: str) -> str:
    """
    For given program, return the content of the program's page in the
    course catalogue. Lookup is done on data returned by sibling methods
    until a match is found, or the search is exhausted.

    :param program: Program name
    :param field: Field of study
    :param level: Level of study (Undergraduate, Graduate, Non-degree)
    :return: HTML content from first found page
    """
    field_at_level_url = get_programs_url(level, field)
    programs_in_field_at_level_content = get_content(field_at_level_url)
    programs_in_field_at_level_data = parse_programs(
        programs_in_field_at_level_content, field_at_level_url)
    program_page_url = next(
        (
            url
            for title, url
            in programs_in_field_at_level_data.items()
            if program in title
        )
    )
    content = get_content(program_page_url)
    return content
