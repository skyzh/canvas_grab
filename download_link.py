from utils import is_windows
from pathlib import Path


def get_url_file(url):
    return f'[InternetShortcut]\nURL={url}\n'


def get_html_file(url):
    return f'<!DOCTYPE html>\
<html><head>\
<meta http-equiv="refresh" content="0; url={url}">\
<title>Redirecting...</title>\
</head><body></body></html>'


def download_link(url, filename: str):
    if filename.endswith('.url'):
        content = get_url_file(url)
    elif filename.endswith('.html'):
        content = get_html_file(url)
    else:
        raise Exception('Internal Error!')
    Path(filename).write_text(content, encoding='ascii')
