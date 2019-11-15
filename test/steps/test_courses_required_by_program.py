from behave import *

from scrape.model import get_program_data, get_program_page

use_step_matcher("re")


@given("the page for (?P<program>.+) in the field of (?P<field>.+)")
def step_impl(context, program, field):
    """
    :type context: behave.runner.Context
    :type program: str
    """
    context.page = get_program_page(field, program)


@then("(?P<code>.+) is listed as a requirement")
def step_impl(context, code):
    """
    :type context: behave.runner.Context
    :type code: str
    """
    assert code in context.lookup


@step("the list of requirements for the program")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    content = context.page
    context.program_data = get_program_data(context)
