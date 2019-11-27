from behave import *

use_step_matcher("re")


@given("the list of all programs")
def step_impl(context):
    # @todo: use ProgramCatalogue
    from devvyn.scrape.page.fields_at_levels import get_all_fields
    context.lookup = get_all_fields()


@then("the field of (?P<field>.+) is listed under (?P<level>.+)")
def step_impl(context, field, level):
    assert field in context.lookup[level], context.lookup.keys()


@given("the web page for the list of all programs")
def step_impl(context):
    from devvyn.scrape.page.fields_at_levels import get_fields_url
    base_href = get_fields_url()
    from devvyn.scrape.fetch import get_content
    content = get_content(base_href)
    assert locals()
