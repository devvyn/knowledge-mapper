from behave import *

from scrape.fetch import get_content
from scrape.model import get_all_fields
from scrape.url import get_fields_url

use_step_matcher("re")


@given("the list of all programs")
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


@given("the web page for the list of all programs")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    base_href = get_fields_url()
    content = get_content(base_href)
    assert locals()
