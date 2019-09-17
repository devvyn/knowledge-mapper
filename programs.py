from html_helper import fetch_wrapped_root_cssselect2

LIST_OF_PROGRAMS = "https://programs.usask.ca/programs/list-of-programs.php"


def fetch_subjects_by_study_level(subjects_list_page_url=LIST_OF_PROGRAMS):
    root = fetch_wrapped_root_cssselect2(subjects_list_page_url)
    program_subjects_by_study_level = {
        match.etree_element.text.strip(): {
            sub_match.etree_element.text.strip(): sub_match.etree_element.attrib['href']
            # @todo: resolve absolute URLs ASAP
            for sub_match in match.parent.query_all('li>a')}
        for match in (root.query_all('section.uofs-section h1'))}
    return program_subjects_by_study_level


def fetch_programs_by_subject(program_subject_page_url):
    root = fetch_wrapped_root_cssselect2(program_subject_page_url)
    programs_in_subject = {
        element.etree_element.text: element.etree_element.attrib['href']
        # @todo: resolve absolute URLs ASAP
        for element in root.query_all('section#Programs ul>li>a')}
    return programs_in_subject
