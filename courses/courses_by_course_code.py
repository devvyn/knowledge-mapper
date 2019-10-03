# @todo: import public methods from here into `courses` root
# @todo: move fetch_…() up one namespace
import urllib.parse
import xml.etree

import cssselect2

import courses.common
import html_helper
from html_helper import fetch_cssselect2_root


def fetch_course_details_by_course_code(course_code: str) -> dict:
    # see data/biol-120.xml for main content node example
    # (all sections, especially
    #   section#Description>div#Description-subsection-0)
    cssselect2_root = html_helper.fetch_cssselect2_root(
        course_details_page_url(course_code))
    course_details_dict = extract_by_course_code(cssselect2_root)
    return course_details_dict


def course_details_page_url(course_code):
    course_page_url_base = courses.common.COURSE_DETAILS_PAGE_URL_BASE
    return urllib.parse.urljoin(course_page_url_base, course_code.lower())


def description_dict(description_node: cssselect2.ElementWrapper) -> dict:
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
        "it's bloody raw": xml.etree.ElementTree.tostring(
            p2.etree_element).decode(html_helper.UTF8),
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


def extract_by_course_code(cssselect2_root):
    description_node = cssselect2_root.query('section#Description'
                                             '>div#Description-subsection-0')
    course_code_extraction = description_dict(
        description_node)
    return course_code_extraction


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
