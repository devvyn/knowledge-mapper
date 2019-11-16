from behave import *

from scrape.model.page.course import get_course

use_step_matcher("re")


@given(r"the description of (?P<code>\w{3,4}-\d{3})")
def step_impl(context, code):
    context.course_description = get_course(code)
    assert isinstance(context.course_description, dict)


@then(r"there is a (?P<description_field_name>\w+) field")
def step_impl(context, description_field_name):
    assert description_field_name in context.course_description


@step(r"the prerequisites include (?P<code>\w{3,4}[ -]\d{3})")
def step_impl(context, code):
    prerequisites = context.course_description['prerequisites']
    assert code in prerequisites
