import urllib.parse

from cssselect2 import ElementWrapper

from html_helper import fetch_wrapped_root_cssselect2

COURSE_DETAILS_PAGE_URL_BASE = "https://catalogue.usask.ca/"


def fetch_courses_by_section(program_page_url):
    root = fetch_wrapped_root_cssselect2(program_page_url)
    courses_by_section = {
        match.etree_element.text.strip(): {
            course_code: course_details_page_url(course_code)
            for course_code in (
                sub_match.etree_element.text.strip() for sub_match in
                match.parent.query_all("ul>li"))
        }
        for match in root.query_all('section.uofs-section h1')
    }
    return courses_by_section


def course_details_page_url(course_code):
    course_page_url_base = COURSE_DETAILS_PAGE_URL_BASE
    return urllib.parse.urljoin(course_page_url_base, course_code.lower())


def locate_main_content_node(
        cssselect2_root: ElementWrapper) -> ElementWrapper:
    return cssselect2_root.query('[role="main"]')


def locate_main_results_nodes(cssselect2_root):
    results_children = locate_main_content_node(cssselect2_root).query_all(
        'h3#results ~ div')
    return results_children


def fetch_course_details_by_course_code(course_code):
    # see data/biol-120.xml for main content node example
    # (all sections, especially
    #   section#Description>div#Description-subsection-0)
    pass


def fetch_course_details_by_subject_code(subject_code):
    # see data/biol.xml for main content node example
    # (all divs after h3#results, within section.uofs-section>div)
    pass


def etree_extract_course_description_fields(
        description_node: ElementWrapper) -> ElementWrapper:
    course_description_fields = {
        """
        'summary': 'p:nth-child(1)',
        'table of fields': 'p:nth-child(2)'
            'prerequisites_list': 'b:text("Prerequisite(s):")'.tail
                conjunctive expression
                    <subject_code>(<conjunction><subject_code>)*
                    <subject_code> = (\w+ \d{2,3})
                    <conjunction> = ( (?:or|and|,) )
            'note': 'b:text("Note:")'.tail
        """
        # @todo: implement the above, via strict MVP path
    }
    return course_description_fields


def etree_extract_course_details(cssselect2_root):
    # for course_code node:
    description_node = cssselect2_root.query('section#Description'
                                             '>div#Description-subsection-0')
    course_code_extraction = etree_extract_course_description_fields(
        description_node)
    # for subject_code node:
    pass
