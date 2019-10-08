from behave import *

from scrape.model import get_fields

use_step_matcher("re")


@given("the college of (?P<college>.+)")
def step_impl(context, college):
    """
    :type context: behave.runner.Context
    :type college: str
    """
    context.lookup = get_fields(college)


@then("the field of (?P<field>.+) is listed")
def step_impl(context, field):
    """
    :type context: behave.runner.Context
    :type field: str
    """
    assert field in context.lookup
