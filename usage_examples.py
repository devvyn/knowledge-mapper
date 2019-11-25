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
import re
from typing import Tuple
from logging import debug

keys = list(
    (level, field, program,)
    for level in catalogue
    for field in catalogue[level]
    for program in catalogue[level][field]
)


def program_explode(program: str) -> Tuple[str, str]:
    # @todo: data object
    program, field = program.split(' - ')
    debug(program, field)
    program_long, program_short = re.match(
        r'(?P<long>.+)(?: \((?P<short>.+)\))',
        program,
    ).group('long', 'short', )
    debug(program_long, program_short)
    return field, program_long, program_short


flattened_catalogue = {
    (level, field, program_short):
        [
            program_long,
            catalogue[level][field][program],
        ]
    for (level, field, (program_long, program_short,), program,)
    in (
        (level, field, program_explode(program), program,)
        for (level, field, program)
        in keys
    )
}

# %%

import pandas

src = pandas.DataFrame.from_dict(
    data=flattened_catalogue,
    orient='index',
    columns=['program', 'URL']
)

# %%

level = 'Undergraduate'
field = 'Bioinformatics'
program = 'Bachelor of Science Four-year (B.Sc. Four-year)'
program_page = get_program_page(program, field, level)
content = clean_whitespace(program_page)
data = parse_program(content)
data

# %%

from scrape.parse import get_program_data

# FIXME get fails, not implemented
url = undergrad_binf['Bachelor of Science Four-year (B.Sc. Four-year)']
content = get_content(url)
data = get_program_data(content)
