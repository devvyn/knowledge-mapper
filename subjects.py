from html_helper import (fetch_cssselect2_root, get_reformatted_text, abs_url,
                         get_href)

LIST_OF_PROGRAMS = "https://programs.usask.ca/programs/list-of-programs.php"


def fetch_subjects_by_study_level(
        subjects_list_page_url: str = LIST_OF_PROGRAMS) -> dict:
    root = fetch_cssselect2_root(subjects_list_page_url)
    section_headers = root.query_all('section.uofs-section h1')
    links_in_list = 'li>a'
    subjects = {
        get_reformatted_text(match): {
            get_reformatted_text(sub_match):
                abs_url(subjects_list_page_url, get_href(sub_match))
            for sub_match in match.parent.query_all(links_in_list)}
        for match in section_headers}
    return subjects
