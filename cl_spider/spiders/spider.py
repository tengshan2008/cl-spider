from typing import Dict, Text
from mechanicalsoup import StatefulBrowser as Browser
import requests
from loguru import logger
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent

REQUESTS_EXCEPTION = (
    requests.exceptions.ReadTimeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.ConnectTimeout,
)

TIMEOUT = (10, 30)


def format_url(url):
    pass


class Spider:
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        if headers is None:
            self.headers = {
                'User-Agent': FakeUserAgent().data_randomize
            }
        else:
            self.headers = headers

    @staticmethod
    def open(url: Text) -> BeautifulSoup:
        with Browser() as browser:
            soup: BeautifulSoup = None
            try:
                browser.open(url, timeout=TIMEOUT)
            except REQUESTS_EXCEPTION as e:
                logger.error(f"url is '{format_url(url)}', error is {e}.")
            except Exception as e:
                logger.error(f"url is '{format_url(url)}', error is {e}.")
            else:
                soup = browser.get_current_page()

            if soup is None:
                logger.warning(f"url is {format_url(url)}, request failed.")
                return None
            if '無法找到頁面' in soup.head.title.string:
                logger.warning(f"url is {format_url(url)}, page 404.")
                return None

            return soup

    @staticmethod
    def format_string(text: Text) -> Text:
        norm = {'\\': '', '/': '', ':': '：', '*': '',
                '?': '？', '<': '《', '>': '》', '|': '',
                '(': '（', ')': '）', ' ': ''}

        for _old, _new in norm.items():
            text = text.replace(_old, _new)

        return text
