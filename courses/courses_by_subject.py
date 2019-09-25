import html_helper


def fetch_course_details_by_subject_code(subject_code):
    # see data/biol.xml for main content node example
    # (all divs after h3#results, within section.uofs-section>div)
    pass


def locate_main_results_nodes(cssselect2_root):
    results_children = html_helper.locate_main_content_node(
        cssselect2_root).query_all('h3#results ~ div')
    return results_children
