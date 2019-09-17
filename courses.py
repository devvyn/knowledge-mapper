from html_helper import fetch_wrapped_root_cssselect2


def fetch_courses_by_section(program_page_url):
    root = fetch_wrapped_root_cssselect2(program_page_url)
    courses_by_section = {
        match.etree_element.text.strip(): {
            course_code: course_details_url(course_code)
            for course_code in (sub_match.etree_element.text.strip() for sub_match in match.parent.query_all("ul>li"))
        }
        for match in root.query_all('section.uofs-section h1')
    }
    return courses_by_section


def course_details_url(course_code):
    pass
    # @todo: insert course_code in URL template
    return '[sorry]'
