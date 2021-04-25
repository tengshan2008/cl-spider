from typing import Dict, Text
import urllib.parse
import requests
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent
from loguru import logger
from mechanicalsoup import StatefulBrowser as Browser

REQUESTS_EXCEPTION = (
    requests.exceptions.ReadTimeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.ConnectTimeout,
)

TIMEOUT = (10, 30)



class Spider:
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        ua = FakeUserAgent()
        # ua.update()
        if headers is None:
            self.headers = {
                'User-Agent': ua.random
            }
        else:
            self.headers = headers

    def open(self, url: Text) -> BeautifulSoup:
        with Browser(user_agent=self.headers['User-Agent']) as browser:
            soup: BeautifulSoup = None
            try:
                browser.open(url, timeout=TIMEOUT)
            except REQUESTS_EXCEPTION as e:
                logger.error(f"route is '{self.format_url(url)}', error is {e}.")
            except Exception as e:
                logger.error(f"route is '{self.format_url(url)}', error is {e}.")
            else:
                soup = browser.get_current_page()

            if soup is None:
                logger.warning(f"route is {self.format_url(url)}, request failed.")
                return None
            if '無法找到頁面' in soup.head.title.string:
                logger.warning(f"route is {self.format_url(url)}, page 404.")
                return None

            return soup

    @staticmethod
    def format_url(url: Text) -> Text:
        r = urllib.parse.urlsplit(url)
        if r.path and r.query and r.fragment:
            return r.path + r.query + r.fragment
        if r.path and r.query:
            return r.path + r.query
        if r.path:
            return r.path
        return url

    @staticmethod
    def format_string(text: Text) -> Text:
        norm = {'\\': '', '/': '', ':': '：', '*': '',
                '?': '？', '<': '《', '>': '》', '|': '',
                '(': '（', ')': '）', ' ': ''}

        for _old, _new in norm.items():
            text = text.replace(_old, _new)

        return text
