# %%
"""
fn get list of course details data:
    get list of program types urls
    for program type details page in program type urls:
        get list of program urls
        for program details page in program urls:
            get list of courses urls
            for course details page in courses urls:
                get course details data
"""

# %%
import html_helper
from programs import programs_url

"""
> get list of program types urls
"""

PROGRAM_TYPES_LIST_PAGE_PATH = "programs/list-of-programs.php"
program_types_list_page_url = programs_url(PROGRAM_TYPES_LIST_PAGE_PATH)
program_types_links = html_helper.get_links_from_page(program_types_list_page_url)

# 212 programs

# %%


"""
> for program type details page in program type urls:
>     get list of program urls
"""

# temporary bypass of loop
PROGRAM_TYPE_PAGE_PATH_BIOINFORMATICS = 'arts-and-science/bioinformatics/index.php'  # @todo: delete this line ASAP
program_type_page_path = PROGRAM_TYPE_PAGE_PATH_BIOINFORMATICS

# to be put inside for loop:
program_type_page_url = programs_url(program_type_page_path)
program_links = html_helper.get_links_from_page(program_type_page_url)

# %%

"""
>         for program details page in program urls:
>             get list of courses urls
"""

# temp bypass of loop
PROGRAM_PAGE_PATH_BS4Y_BINF = "bsc-4-bioinformatics.php"
program_page_path = PROGRAM_PAGE_PATH_BS4Y_BINF

# inside for loop:
program_page_url = programs_url(program_page_path)
courses_links = html_helper.get_links_from_page(program_page_url)

# %%

"""
>             for course details page in courses urls:
>                 get course details data
"""

# temp bypass
COURSE_PAGE_PATH_EXAMPLE = ""  # @todo: fill
course_page_path = COURSE_PAGE_PATH_EXAMPLE

# inside for loop:
# course_page_url = courses_url(course_page_path)
# get course details data
