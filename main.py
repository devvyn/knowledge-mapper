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

# noinspection PyUnresolvedReferences
import requests

from programs import get_program_dict

"""
> get list of programs
"""

program_dict = get_program_dict()

# 212 programs
