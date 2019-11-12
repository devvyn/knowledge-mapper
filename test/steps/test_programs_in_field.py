from behave import *

from scrape.model import get_programs, get_programs_page

use_step_matcher("re")


@given("the web page for the list of (?P<level>.+) programs in (?P<field>.+)")
def step_impl(context, level, field):
    """
    :type field: str
    :type context: behave.runner.Context
    :type level: str
    :type college: str
    """
    context.page = get_programs_page(level, field)


@given("the list of programs")
def step_impl(context):
    """
    :type context: behave.runner.Context
    :type field: str
    """
    content, base_href = context.page
    context.programs = get_programs(content, base_href)


@then("(?P<program>.+) is listed as a program in (?P<field>.+)")
def step_impl(context, program, field):
    """
    :type field: str
    :type context: behave.runner.Context
    :type program: str
    """
    programs = context.programs
    assert program in programs, f"{programs}"
