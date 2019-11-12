from behave import *

from scrape.model import get_all_fields, get_list_of_program_page

use_step_matcher("re")


@given("the list of programs")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.lookup = get_all_fields()


@then("the field of (?P<field>.+) is listed under (?P<level>.+)")
def step_impl(context, field, level):
    """
    :type context: behave.runner.Context
    :type level: str
    :type field: str
    """
    assert field in context.lookup[level], context.lookup.keys()


@given("the web page for the list of programs")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert get_list_of_program_page()
