from behave import *

use_step_matcher("re")


@given("the web page for the list of (?P<level>.+) programs in (?P<field>.+)")
def step_impl(context, level, field):
    """
    :type field: str
    :type context: behave.runner.Context
    :type level: str
    """
    from scrape.page.programs_in_field_at_level import get_programs_page
    context.page = get_programs_page(level, field)


@given("the list of programs")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    content, base_href = context.page
    from scrape.page.programs_in_field_at_level import get_programs
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
