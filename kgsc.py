import gzip
import hashlib
import os
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
    if os.path.isfile(filepath + ".gz"):
        with gzip.open(filepath + ".gz", "rb") as f:
            contents = f.read()
    else:
        with open(filepath, "rb") as html_file:
            contents = html_file.read()
        file_write(contents, filepath)
        os.remove(filepath)
    return contents


def prepare_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def get_filepath(url: str) -> str:
    return os.path.join(CACHE_DIR, get_url_hash(url) + ".html")


def get_list_page(url: str) -> (int, list[str], list[str]):
    url_file = get_filepath(url)
    if os.path.isfile(url_file):
        html_content = file_read(url_file)
    else:
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        buffer = BytesIO()
        c.setopt(pycurl.WRITEDATA, buffer)
        c.perform()
        html_content = buffer.getvalue()
    file_write(html_content, url_file)
    html_root = fromstring(html_content.decode(encoding="utf-8"))
    # div.graveyards-list>div.paginate-meta>span.current
    # result = html_root.xpath("//div[contains(@class, 'paginate-meta')]/span/text()")
    # div.graveyards-list>div.paginate-meta>span.total
    print(etree.tostring(html_root))
    # div.graveyards-list>a.graveyard-item href
    result = html_root.xpath('//a[@class="graveyard-item"]/@href')
    print(result)
    # div.graveyards-list>a.graveyard-item h4
    c.close()



def main():
    prepare_cache_dir()
    get_list_page(HOME_URL)


if __name__ == "__main__":
    main()

