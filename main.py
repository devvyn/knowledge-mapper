# %%
"""
fn get list of course details:
    get list of program types urls
    for program type details page in program type urls:
        get list of program urls
        for program details page in program urls:
            get list of courses urls
            for course details page in courses urls:
                get course details data
                (add to dependency graph)
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
