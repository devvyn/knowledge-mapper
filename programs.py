from html_helper import fetch_cssselect2_root, abs_url, reformat_text, get_href

LIST_OF_PROGRAMS = "https://programs.usask.ca/programs/list-of-programs.php"


def fetch_subjects_by_study_level(
        subjects_list_page_url: str = LIST_OF_PROGRAMS) -> dict:
    root = fetch_cssselect2_root(subjects_list_page_url)
    section_headers = get_section_headers(root)
    links_in_list = 'li>a'
    subjects = {
        get_reformatted_text(match): {
            get_reformatted_text(sub_match):
                abs_url(subjects_list_page_url, get_href(sub_match))
            for sub_match in match.parent.query_all(links_in_list)}
        for match in section_headers}
    return subjects


def fetch_programs_by_subject(page_url: str) -> dict:
    root = fetch_cssselect2_root(page_url)
    links_in_programs_section = 'section#Programs ul>li>a'
    links = root.query_all(links_in_programs_section)
    programs_in_subject = {
        reformat_text(element):
            abs_url(page_url, get_href(element))
        for element in links}
    return programs_in_subject


def get_section_headers(root):
    return root.query_all('section.uofs-section h1')


def get_reformatted_text(match):
    return reformat_text(match.etree_element.text)
