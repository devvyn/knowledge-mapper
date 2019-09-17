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

import programs

"""
> get list of study_levels
> get list of program_subjects_urls
"""

program_subjects = programs.fetch_subjects_by_study_level()

# %%

import urllib.parse

"""
> for program type details page in program type urls:
>     get list of program urls
"""

# temporary bypass of loop
PROGRAM_SUBJECT_PAGE_PATH_BIOINFORMATICS = '../arts-and-science/bioinformatics/index.php'  # @todo: delete this line ASAP
program_subject_page_path = PROGRAM_SUBJECT_PAGE_PATH_BIOINFORMATICS

# for program_subject_page_path in program_subjects:
# @todo: query for relevant links
program_subject_page_url = urllib.parse.urljoin(programs.LIST_OF_PROGRAMS, program_subject_page_path)
programs = programs.fetch_programs_by_subject(program_subject_page_url)

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
program_page_url = urllib.parse.urljoin(program_subject_page_url, program_page_path)
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
