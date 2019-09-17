# %%
"""
fn get list of course details data:
    get list of study_levels
    get list of program_subjects_urls
    for program subject page in program_subjects_urls:
        get list of program urls
        for program details page in program urls:
            get list of course urls
            for course details page in course urls:
                get course details data
"""

# %%
import urllib.parse

import pandas
from cssselect2 import ElementWrapper

import html_helper

# %%
"""
> get list of study_levels
> get list of program_subjects_urls
"""

program_subjects_list_page_url = "https://programs.usask.ca/programs/list-of-programs.php"
program_subjects_list_page_html = html_helper.get_page_html(program_subjects_list_page_url)
program_subjects_list_page_tree = html_helper.get_page_etree(program_subjects_list_page_html)
section_query = 'section.uofs-section h1'
root = ElementWrapper.from_html_root(program_subjects_list_page_tree)
study_level_sections_selection = root.query_all(section_query)
program_subjects_by_study_level = {
    match.etree_element.text.strip(): {
        sub_match.etree_element.text.strip(): sub_match.etree_element.attrib['href']
        for sub_match in match.parent.query_all('li>a')}
    for match in study_level_sections_selection}

# %%

"""
> for program type details page in program type urls:
>     get list of program urls
"""

# temporary bypass of loop
# https://programs.usask.ca/arts-and-science/bioinformatics/index.php
PROGRAM_TYPE_PAGE_PATH_BIOINFORMATICS = '../arts-and-science/bioinformatics/index.php'  # @todo: delete this line ASAP
program_type_page_path = PROGRAM_TYPE_PAGE_PATH_BIOINFORMATICS

# for program_subject_page_path in program_subjects:
program_type_page_url = urllib.parse.urljoin(program_subjects_list_page_url, program_type_page_path)
# @todo: query for relevent links

# %%

"""
>         for program details page in program urls:
>             get list of courses urls
"""

# temp bypass of loop
# https://programs.usask.ca/arts-and-science/bioinformatics/bsc-4-bioinformatics.php
PROGRAM_PAGE_PATH_BS4Y_BINF = "bsc-4-bioinformatics.php"
program_page_path = PROGRAM_PAGE_PATH_BS4Y_BINF

# inside for loop:
program_page_url = urllib.parse.urljoin(program_type_page_url, program_page_path)
# @todo: element query for course codes

# cl = list(courses_links)
# cldf = pandas.DataFrame(data=cl)

# %%

"""
>             for course details page in courses urls:
>                 get course details data
"""

# temp bypass
# COURSE_PAGE_PATH_EXAMPLE = ""  # @todo: fill
# course_page_path = COURSE_PAGE_PATH_EXAMPLE

# inside for loop:
# course_page_url = courses_url(course_page_path)
# get course details data
# course_details_collection = (courses.get_course_fields(course_details_node) for course_details_node in course_details_nodes)

# cddf = pandas.DataFrame(data=course_details_collection)
