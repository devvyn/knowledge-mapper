import urllib.parse
from xml.etree import ElementTree

from cssselect2 import ElementWrapper

from src import html_helper
from src.html_helper import fetch_cssselect2_root

UTF8 = 'utf-8'

COURSE_DETAILS_PAGE_URL_BASE = "https://catalogue.usask.ca/"


def fetch_courses_by_section(program_page_url):
    root = fetch_cssselect2_root(program_page_url)
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


def fetch_course_details_by_course_code(course_code) -> dict:
    # see data/biol-120.xml for main content node example
    # (all sections, especially
    #   section#Description>div#Description-subsection-0)
    cssselect2_root = html_helper.fetch_cssselect2_root(
        course_details_page_url(course_code))
    course_details_dict = cssselect2_extract_description_fields(
        cssselect2_root)
    return course_details_dict


def fetch_course_details_by_subject_code(subject_code):
    # see data/biol.xml for main content node example
    # (all divs after h3#results, within section.uofs-section>div)
    pass


def description_dict(description_node: ElementWrapper) -> dict:
    # 'summary': 'p:nth-child(1)',
    # 'table of fields': 'p:nth-child(2)'
    #     'prerequisites_list': 'b:text("Prerequisite(s):")'.tail
    #         conjunctive expression
    #             <subject_code>(<conjunction><subject_code>)*
    #             <subject_code> = (\w+ \d{2,3})
    #             <conjunction> = ( (?:or|and|,) )
    #     'note': 'b:text("Note:")'.tail
    # @todo: implement the above, via strict MVP path
    p2 = locate_p2(description_node)
    course_description_fields = {
        "it's bloody raw": ElementTree.tostring(p2.etree_element).decode(UTF8),
        "prerequisites": parse_description_fields(p2),
        "summary": description_node.query('p:nth-child(1)').etree_element.text,
    }
    return course_description_fields


def locate_p2(description_node):
    return description_node.query('p:nth-child(2)')


def parse_description_fields(description_node):
    target_tag = 'b'
    target_text = "Prerequisite(s):"
    match_collection = [node.etree_element.tail for node in
                        description_node.query_all(target_tag) if
                        node.etree_element.text == target_text]
    return match_collection.pop()


def cssselect2_extract_description_fields(
        cssselect2_root: ElementWrapper) -> dict:
    # for course_code node:
    description_node = cssselect2_root.query('section#Description'
                                             '>div#Description-subsection-0')
    course_code_extraction = description_dict(
        description_node)
    # for subject_code node:
    # @todo: extract subject_code node
    return course_code_extraction
