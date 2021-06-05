import os
import random
import time
import urllib.parse
from typing import Dict, Optional, Text, Tuple

import requests.exceptions
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent
from loguru import logger
from mechanicalsoup import StatefulBrowser as Browser
from requests import Response
from requests.sessions import HTTPAdapter

REQUESTS_EXCEPTION = (
    requests.exceptions.ReadTimeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.ConnectTimeout,
)

WAIT_TIME_MIN = 3
WAIT_TIME_MAX = 5
TIMEOUT = (10, 30)
MAX_RETRIES = 3


class Spider:
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        if headers is None:
            self.headers = {'User-Agent': self.user_agent}
        else:
            self.headers = headers

    def _open(
        self,
        url: Text,
        soup: Optional[BeautifulSoup] = None,
        response: Optional[Response] = None,
        **kwargs,
    ) -> Tuple[BeautifulSoup, Response]:
        with Browser(soup_config={'features': 'html5lib'},
                     user_agent=self.headers['User-Agent'],
                     **kwargs) as b:
            try:
                response = b.open(url, timeout=TIMEOUT)
            except REQUESTS_EXCEPTION as e:
                logger.error(
                    f"route is '{self.format_url(url)}', error is {e}.")
            except Exception as e:
                logger.error(
                    f"route is '{self.format_url(url)}', error is {e}.")
            else:
                soup = b.page

        if response is None:
            logger.warning(f"route is {self.format_url(url)}, request failed.")
            return None
        if response is None and soup is None:
            logger.warning(
                f"route is {self.format_url(url)}, parse soup failed.")
            return None
        if soup and '無法找到頁面' in soup.head.title.string:
            logger.warning(f"route is {self.format_url(url)}, page 404.")
            return None

        return soup, response

    def open(self, url: Text) -> BeautifulSoup:
        soup, _ = self._open(url)
        return soup

    def download(self, url: Text) -> Response:
        adapter = HTTPAdapter(max_retries=MAX_RETRIES)
        requests_adapters = {'http://': adapter, 'https://': adapter}

        _, response = self._open(url, requests_adapters=requests_adapters)
        return response

    @staticmethod
    def format_url(url: Text) -> Text:
        r = urllib.parse.urlsplit(url)
        if r.path and r.query and r.fragment:
            return f'{r.path}?{r.query}{r.fragment}'
        if r.path and r.query:
            return f'{r.path}?{r.query}'
        if r.path:
            return r.path
        return url

    @staticmethod
    def format_url_host(url: Text) -> Text:
        r = urllib.parse.urlsplit(url)
        if r.scheme and r.netloc:
            return f'{r.scheme}://{r.netloc}'
        if r.netloc:
            return f'http://{r.netloc}'
        return url

    @staticmethod
    def format_string(text: Text) -> Text:
        norm = {
            '\\': '',
            '/': '',
            ':': '：',
            '*': '',
            '?': '？',
            '<': '《',
            '>': '》',
            '|': '',
            '-': '',
            '(': '（',
            ')': '）',
            ' ': ''
        }

        for _old, _new in norm.items():
            text = text.replace(_old, _new)

        return text

    @property
    def random_sleep(
        self,
        min: Optional[int] = WAIT_TIME_MIN,
        max: Optional[int] = WAIT_TIME_MAX,
    ) -> None:
        time.sleep(random.randint(min, max))

    @property
    def user_agent(self):
        location = os.getcwd() + '/cl_spider/spiders/fake_useragent.json'
        ua = FakeUserAgent(path=location)
        return ua.random
