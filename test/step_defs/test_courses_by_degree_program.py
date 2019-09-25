from pytest_bdd import scenario, given, then


@scenario('../features/courses_by_degree_program.feature',
          'courses required by degree program')
def courses_by_degree_program():
    pass


@given("the program: <degree_program>")
def degree_program(degree_program):
    raise NotImplementedError(u'STEP: Given <degree_program>')


@then("<course_code> is required")
def course_code_is_present(course_code, degree_program):
    raise NotImplementedError(u'STEP: Then <course_code> is required')
