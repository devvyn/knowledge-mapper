from pytest_bdd import given, scenario, then

import programs


@scenario('../features/programs_by_subject.feature',
          'degree program names and links')
def test_programs_by_subject():
    pass


@given("the UofS <study_level> programs for <subject>")
def program_dict_for_subject(study_level, subject):
    return programs.fetch_programs_by_subject('https://programs.usask.ca/'
                                              'arts-and-science/'
                                              'bioinformatics/index.php')


@then("there is at least 1 degree program")
def there_is_at_least_1_degree_program_link(program_dict_for_subject):
    assert len(program_dict_for_subject) >= 1


@then("all degree programs have at least 1 link")
def all_degree_programs_have_min_links(program_dict_for_subject):
    assert all((
        value.startswith('http')
        for value
        in program_dict_for_subject.values()
    ))
