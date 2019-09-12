import requests


def save_page_text_to_cache(cache_file_path, page_url):
    text = requests.get(page_url).text
    save_text_to_cache(cache_file_path, text)
    return text


def save_text_to_cache(cache_file_path, text):
    with open(cache_file_path, 'w') as f:
        f.write(text)


def get_text_from_cache(cache_file_path):
    with open(cache_file_path) as f:
        text = f.read()
    return text


def get_page_text_with_cache(cache_file_path: str, page_url: str) -> str:
    """
    Fetch text from file if it exists, otherwise fetch text from URL and save to file before returning.
    :param page_url: Full URL to page.
    :param cache_file_path: Full path to file.
    :return: Page text.
    """
    try:
        text = get_text_from_cache(cache_file_path)
    except FileNotFoundError:
        text = save_page_text_to_cache(cache_file_path, page_url)
    return text
