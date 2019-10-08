import re
from typing import AnyStr, List

from behave import *

use_step_matcher("re")


@given(r"the description of (?P<code>\w{3,4}-\d{3})")
def course_description(context, code):
    from scrape.model import get_course
    context.course_description = get_course(code)
    assert isinstance(context.course_description, dict)


@then(r"there is a (?P<description_field_name>\w+) field")
def there_is_this_description_field(context, description_field_name):
    assert description_field_name in context.course_description


@then("the summary is more than just a few words")
def the_summary_is_not_too_short(context):
    summary = context.course_description['summary']
    words = get_words(summary)
    assert len(words) > 5


def get_words(text: AnyStr) -> List[AnyStr]:
    """
    Split text by whitespace.

    :param text: Text to split.
    :return: List of words.
    """
    return re.split(r'\s+', text)


@step(r"the prerequisites include (?P<code>\w{3,4}[ -]\d{3})")
def step_impl(context, code):
    prerequisites = context.course_description['prerequisites']
    assert code in prerequisites
