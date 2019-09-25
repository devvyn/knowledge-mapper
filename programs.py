from html_helper import (fetch_cssselect2_root, abs_url, reformat_text,
                         get_href)


def fetch_programs_by_subject(page_url: str) -> dict:
    root = fetch_cssselect2_root(page_url)
    links_in_programs_section = 'section#Programs ul>li>a'
    links = root.query_all(links_in_programs_section)
    programs_in_subject = {
        reformat_text(element):
            abs_url(page_url, get_href(element))
        for element in links}
    return programs_in_subject
