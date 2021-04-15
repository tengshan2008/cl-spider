from typing import Dict, Text
from mechanicalsoup import StatefulBrowser as Browser
import requests
import logger

REQUESTS_EXCEPTION = (
    requests.exceptions.ReadTimeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.ConnectTimeout,
)

def browser_open(url):
    with Browser() as browser:
        try:
            response = browser.open(url)
        except REQUESTS_EXCEPTION as e:
            logger.error("error is {error}", error=e)
        except Exception as e:
            logger.error("error is {error}", error=e)
        else:
            return response.content


class Spider:
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        if headers is None:
            self.headers = {
                'User-Agent': ''
            }
        else:
            self.headers = headers
