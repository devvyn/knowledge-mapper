# %%
"""
fn get list of course details:
    get list of programs
    for program in programs:
        get list of courses
        for course in courses:
            get course details
"""

# %%
import html_helper
from programs import programs_url

BIOINFORMATICS_INDEX_PHP = 'arts-and-science/bioinformatics/index.php'

"""
> get list of programs
"""

# DATA_PROGRAMS_LIST_PAGE_URL_ = "https://programs.usask.ca/programs/list-of-programs.php"


programs_links = html_helper.get_links_from_page(programs_url(BIOINFORMATICS_INDEX_PHP))

# 212 programs

# EXAMPLE_PROGRAM = 'Bioinformatics'
# program_page_url = program_dict[program]

# %%

"""
> get list of courses
"""
