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

# noinspection PyUnresolvedReferences
from pathlib import Path

import cssselect2
import lxml.html
# noinspection PyUnresolvedReferences
import requests

from cache import get_page_text_with_cache


"""
> get list of programs
"""

DATA_PATH = Path('./data/')
DATA_PROGRAMS_LIST_PATH = Path(DATA_PATH, 'programs.html')
DATA_PROGRAMS_LIST_PAGE_URL = "https://programs.usask.ca/programs/list-of-programs.php"
DATA_COURSES_SUBJECT_CODE_LIST_HREF = "https://catalogue.usask.ca"


def get_programs_list_page_tree():
    page_url = DATA_PROGRAMS_LIST_PAGE_URL
    path = DATA_PROGRAMS_LIST_PATH
    html = get_page_text_with_cache(path, page_url)
    return lxml.html.fromstring(html)


tree = get_programs_list_page_tree()
tree_css = cssselect2.ElementWrapper.from_html_root(tree)
adict = {item.text.strip():item.attrib['href'] for item in (item.etree_element for item in tree_css.query_all('li>a'))}
program_dict = {key: value for key, value in adict.items() if value[:3] == '../'}

# 212 programs
