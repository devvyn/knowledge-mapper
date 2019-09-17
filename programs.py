import cssselect2

import html_helper


def get_subjects_by_study_level():
    program_subjects_list_page_html = html_helper.get_page_html(program_subjects_list_page_url())
    program_subjects_list_page_tree = html_helper.get_page_etree(program_subjects_list_page_html)
    section_query = 'section.uofs-section h1'
    root = cssselect2.ElementWrapper.from_html_root(program_subjects_list_page_tree)
    study_level_sections_selection = root.query_all(section_query)
    program_subjects_by_study_level = {
        match.etree_element.text.strip(): {
            sub_match.etree_element.text.strip(): sub_match.etree_element.attrib['href']
            for sub_match in match.parent.query_all('li>a')}
        for match in study_level_sections_selection}
    return program_subjects_by_study_level


def program_subjects_list_page_url():
    return "https://programs.usask.ca/programs/list-of-programs.php"
