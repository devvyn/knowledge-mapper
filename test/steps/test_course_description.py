import re

from behave import *

use_step_matcher("re")


@given(r"the description of (?P<code>\w{3,4}-\d{3})")
def course_description(context, code):
    from scrape.model import get_course
    context.course_description = get_course(code)
    assert isinstance(context.course_description, dict)


@then(r"there is a (?P<description_field_name>\w+)")
def there_is_this_description_field(context, description_field_name):
    assert description_field_name in context.course_description
    context.summary = context.course_description[description_field_name]


@then("the summary is more than just a few words")
def the_summary_is_not_too_short(context):
    words = re.split(r'\s+', context.summary)
    assert len(words) > 5
