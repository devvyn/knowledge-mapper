from behave import *

from scrape.model import get_programs

use_step_matcher("re")


@given("the field of (?P<field>.+) at the college of (?P<college>.+)")
def step_impl(context, field, college):
    """
    :type context: behave.runner.Context
    :type field: str
    :type college: str
    """
    context.lookup = get_programs(college, field)


@then("(?P<program>.+) is listed as a program")
def step_impl(context, program):
    """
    :type context: behave.runner.Context
    :type program: str
    """
    assert program in context.lookup
