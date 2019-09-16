from urllib.parse import urljoin


def programs_url(url_path):
    data_page_url_base = 'https://programs.usask.ca/'
    url = urljoin(data_page_url_base, url_path)
    return url
