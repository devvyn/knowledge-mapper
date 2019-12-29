import devvyn.scrape.page.usask.program_catalogue


def test_program_catalogue_data() -> None:
    """
    Verify that `devvyn.scrape.page.program_catalogue.program_catalogue_data()`
    returns a dict-like object that isn't empty.
    """
    catalogue = (
        devvyn.scrape.page.usask.program_catalogue.program_catalogue_data()
    )

    assert catalogue
    assert len(catalogue) > 0
    assert catalogue.keys()
    assert catalogue.values()
    assert catalogue.items()
