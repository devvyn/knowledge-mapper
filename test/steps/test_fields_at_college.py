""" Test scraping of program catalogue for academic fields and levels. """
from behave import *

from devvyn.scrape.page.usask.program_catalogue import URL_USASK_PROGRAMS_LIST

use_step_matcher("re")


@given("the list of all programs")
def step_impl(context):
    # @todo: use ProgramCatalogue
    from devvyn.scrape.page.usask.program_catalogue import program_catalogue_data
    context.data = program_catalogue_data()


@then("the field of (?P<field>.+) is listed under (?P<level>.+)")
def step_impl(context, field, level):
    catalogue = context.data
    assert field in catalogue[level], f'{catalogue.keys()=}'


@given("the web page for the list of all programs")
def step_impl(context):
    base_href = URL_USASK_PROGRAMS_LIST
    from devvyn.fetch import get_content
    content = get_content(base_href)
    assert locals()
