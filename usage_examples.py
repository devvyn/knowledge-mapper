# %%
from scrape.model.program_catalogue import ProgramCatalogue

catalogue = ProgramCatalogue()

# %%

list(catalogue)

# %%

undergrad = catalogue['Undergraduate']
undergrad

# %%

undergrad_binf = undergrad['Bioinformatics']
undergrad_binf

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

# FIXME get fails, not implemented
url = undergrad_binf['Bachelor of Science Four-year (B.Sc. Four-year)']
content = get_content(url)
data = get_program_data(content)
