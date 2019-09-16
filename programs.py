from urllib.parse import urljoin

PROGRAMS_USASK_CA_ = 'https://programs.usask.ca/'


def programs_url(url_path):
    data_page_url_base = PROGRAMS_USASK_CA_
    url = urljoin(data_page_url_base, url_path)
    return url
