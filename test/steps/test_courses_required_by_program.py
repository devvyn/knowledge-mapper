from itertools import chain

from behave import *

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
    from scrape.model.page.courses_in_program import get_program_page
    content = get_program_page(program, field, level)
    context.content = content


@then("(?P<code>.+) is listed as a requirement")
def step_impl(context, code):
    data = context.program_data
    course_codes = chain.from_iterable(data.values())
    assert any(
        (code in listed_code for listed_code in course_codes)
    )


@step("the list of requirements for the program")
def step_impl(context):
    content = context.content
    from scrape.parse import get_program_data
    data = get_program_data(content)
    assert len(data)
    context.program_data = data
