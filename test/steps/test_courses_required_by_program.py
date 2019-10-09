from behave import *

from scrape.model import get_requirements

use_step_matcher("re")


@given("the (?P<program>.+) program in the field of (?P<field>.+)")
def step_impl(context, program, field):
    """
    :type context: behave.runner.Context
    :type field: str
    :type program: str
    """
    context.lookup = get_requirements(field, program)


@then("(?P<code>.+) is listed as a requirement")
def step_impl(context, code):
    """
    :type context: behave.runner.Context
    :type code: str
    """
    assert code in context.lookup
