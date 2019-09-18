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


def fetch_course_details_by_course_code(course_code):
    # see data/biol-120.xml for main content node example
    return extract_course_details_from_etree_node(
        fetch_wrapped_root_cssselect2(
            course_details_page_url(course_code)))


def fetch_course_details_by_subject_code(subject_code):
    # see data/biol.xml for main content node example
    pass


def extract_course_details_from_etree_node(
        course_details_node_etree_cssselect2):
    details_matches = [
        [
            sub_match.parent.etree_element.text
            for sub_match in match.parent.query_all('p>b')
        ]
        for match in course_details_node_etree_cssselect2
    ]
    # course_details_dict = {}
    # return course_details_dict
    return details_matches


def locate_course_details_node(
        course_details_page_root: ElementWrapper) -> ElementWrapper:
    return course_details_page_root.query(
        '[role="main"]')


def locate_course_details_results_node(course_details_page_etree_cssselect2):
    pass
