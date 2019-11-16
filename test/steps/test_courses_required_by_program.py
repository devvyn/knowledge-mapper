from behave import *

use_step_matcher("re")


@given("the page for (?P<program>.+) in the field of (?P<field>.+)")
def step_impl(context, program, field):
    """
    :type context: behave.runner.Context
    :type program: str
    """
    from scrape.model.page.courses_in_program import get_program_page
    context.page = get_program_page(program, field)


@then("(?P<code>.+) is listed as a requirement")
def step_impl(context, code):
    assert code in context.lookup


@step("the list of requirements for the program")
def step_impl(context):
    content = context.page
    from scrape.parse import get_program_data
    context.program_data = get_program_data(content)
