import devvyn.scrape.fetch
import devvyn.scrape.page.programs_in_field_at_level
import devvyn.scrape.parse


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
    url = devvyn.scrape.page.programs_in_field_at_level.get_programs_url(level, field)
    content = devvyn.scrape.fetch.get_content(url)
    data = devvyn.scrape.parse.parse_programs(content, url)
    program_page_url = next(
        (
            url
            for title, url
            in data.items()
            if program in title
        )
    )
    content = devvyn.scrape.fetch.get_content(program_page_url)
    return content
