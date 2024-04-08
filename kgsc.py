import gzip
import hashlib
import os
import re
from urllib.parse import urljoin
from io import BytesIO
from lxml.ElementInclude import etree
from lxml.html.soupparser import fromstring
import pycurl

CATALOG_FILE = "kriegsgraeberstaetten.csv"
HOME_URL = "https://kriegsgraeberstaetten.volksbund.de"
LIST_URL = f"{HOME_URL}/friedhof"
CACHE_DIR = "./cache/"
PER_PAGE = 10
START_PAGE = 0


def get_cemetery_page(url: str):
    pass


def get_url_hash(url: str) -> str:
    m = hashlib.md5()
    m.update(url.encode("utf-8"))
    return m.hexdigest()


def file_write(contents: bytes, filepath: str):
    filepath = filepath + ".gz"
    with gzip.open(filepath, "wb") as f:
        f.write(contents)


def file_read(filepath: str) -> bytes:
    with gzip.open(filepath, "rb") as f:
        contents = f.read()
    return contents


def prepare_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def get_filepath(url: str) -> str:
    return os.path.join(CACHE_DIR, get_url_hash(url) + ".html.gz")


def get_list_page(url: str) -> (int, list[str], list[str]):
    url_file = get_filepath(url)
    if os.path.isfile(url_file):
        print(f"Reading from cache: {url_file}")
        html_content = file_read(url_file)
    else:
        print(f"Downloading: {url}")
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        buffer = BytesIO()
        c.setopt(pycurl.WRITEDATA, buffer)
        c.perform()
        html_content = buffer.getvalue()
        c.close()
        file_write(html_content, url_file)
    html_root = fromstring(html_content.decode(encoding="utf-8"))
    result = html_root.xpath("//div[contains(@class, 'paginate-meta')]/span/text()")
    current_start = current_end = per_page = total = None
    if len(result) == 2:
        current_start, current_end = result[0].strip().split(" - ")
        per_page, total = result[1].strip().split(" von ")
    graveyard_urls = html_root.xpath("//a[contains(@class, 'graveyard-item')]/@href")
    graveyard_names = html_root.xpath("//a[contains(@class, 'graveyard-item')]/div/div/div/h4/text()")
    graveyard_country = html_root.xpath("//a[contains(@class, 'graveyard-item')]/div/div/div/p/span[@class=\"coordinate\"]/text()")
    graveyard_list = []
    for x in range(0, len(graveyard_urls)):
        graveyard_list.append(
            [
                graveyard_names[x],
                graveyard_country[x],
                graveyard_urls[x],
            ]
        )
    next_url = None
    next_page_url = html_root.xpath("//li[contains(@class, 'page-item next')]/a/@href")
    if next_page_url:
        next_url = urljoin(HOME_URL, next_page_url[0])
    return graveyard_list, int(total), next_url


def get_all_graveyards():
    total = None
    next_url = LIST_URL
    graveyards = []
    while next_url:
        graveyards_list, total, next_url = get_list_page(next_url)
        if len(graveyards) == 0:
            print(f"Downloading total of: {total} graveyards")
        if len(graveyards_list) == 0:
            break
        graveyards += graveyards_list
        if len(graveyards) >= total:
            break
    return total, graveyards


def main():
    prepare_cache_dir()
    total, graveyards = get_all_graveyards()
    print(graveyards)


if __name__ == "__main__":
    main()


