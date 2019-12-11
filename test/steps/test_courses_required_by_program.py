from itertools import chain

from behave import *

from devvyn.model.program_catalogue import get_program_data
from devvyn.scrape.page.usask.program import program_page

use_step_matcher("re")


@given(
    "the page for (?P<program>.+) in the field of (?P<field>.+) at the level "
    "of (?P<level>.+)")
def step_impl(context, program, field, level):
    """
    :param field:
    :type level: str
    :type context: behave.runner.Context
    :type program: str
    """
    content = program_page(program, field, level)
    context.content = content


@then("(?P<code>.+) is listed as a requirement")
def step_impl(context, code):
    data = context.program_page
    course_codes = chain.from_iterable(data.values())
    assert any(
        (code in listed_code for listed_code in course_codes)
    )


@given("the list of requirements for the program")
def step_impl(context):
    content = context.content
    data = get_program_data(content)
    assert len(data)
    context.program_page = data
