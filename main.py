# %%

# noinspection PyUnresolvedReferences
import lxml.html
# noinspection PyUnresolvedReferences
import requests

# %%

CONTENT = 'content'
COURSES = 'courses'
COURSE_DETAILS = 'course_details'
HREF = 'href'
LIST = 'list'
MAPPING = 'mapping'
PROGRAMS = 'programs'
SUBJECT_CODE = 'subject_code'
TEXT = 'text'
TREE = 'tree'

courses_struct = {
    SUBJECT_CODE: {
        HREF: "https://catalogue.usask.ca",
        LIST: [],
    },
    COURSE_DETAILS: {
        HREF: "",
        MAPPING: {},
    }
}
programs_struct = {
    HREF: "https://programs.usask.ca/programs/list-of-programs.php",
    CONTENT: {
        TEXT: None,
        TREE: None,
    },
}
data = {
    PROGRAMS: programs_struct,
    COURSES: courses_struct,
}

# %%

cache_file_path = './data/programs.html'
try:
    with open(cache_file_path) as f:
        text = f.read()
except FileNotFoundError:
    text = requests.get(data[PROGRAMS][HREF]).text
    with open(cache_file_path, 'w') as f:
        f.write(text)
data[PROGRAMS][CONTENT][TEXT] = text

data[PROGRAMS][CONTENT][TREE] = lxml.html.fromstring(data[PROGRAMS][CONTENT][TEXT])
