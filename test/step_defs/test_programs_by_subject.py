from pytest_bdd import given, then, scenario


@scenario('../features/programs_by_subject.feature',
          'degree program names and links')
def test_programs_by_subject():
    pass


@given("the UofS <study_level> programs for <subject>")
def program_dict_for_subject(study_level, subject):
    raise NotImplementedError(
        u'STEP: Given the UofS program list for <subject>')


@then("there is at least 1 degree program link")
def there_is_at_least_1_degree_program_link():
    raise NotImplementedError(
        u'STEP: Then there is at least 1 degree program link')
