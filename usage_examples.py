# %%
from scrape.model.program_catalogue import ProgramCatalogue

catalogue = ProgramCatalogue()

# %%

list(catalogue)

# %%

catalogue['Undergraduate']

# %%

catalogue
# %%

tuple(
    (parent, child)
    for (parent, children) in catalogue.items()
    for child in children
)

# %%

from scrape.parse import clean_whitespace, parse_program
from scrape.page.courses_in_program import get_program_page

level = 'Undergraduate'
field = 'Bioinformatics'
program = 'Bachelor of Science Four-year (B.Sc. Four-year)'
program_page = get_program_page(program, field, level)
content = clean_whitespace(program_page)
data = parse_program(content)
data

# %%
from scrape.fetch import get_content
from scrape.parse import get_program_data

url = catalogue['Undergraduate']['Bioinformatics']
content = get_content(url)
data = get_program_data(content)
