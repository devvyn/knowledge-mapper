from scrape.url import get_requirements_url


def test_get_requirements_url():
    assert get_requirements_url(
        'Bioinformatics',
        'Bachelor of Science Four-year (B.Sc. Four-year)'
    ) == 'https://programs.usask.ca/arts-and-science/bioinformatics/index.php'
