from typing import Dict, Text
from cl_spider.spiders.spider import Spider

def download_image(url: Text):
    with Browser() as browser:
        response = browser.open(url)



class PictureSpider(Spider):
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        super().__init__(headers=headers)

    def parse_html(self):
        pass
import time
import random
from typing import Dict, Optional, Text, List

from cl_spider.spiders.spider import Spider
from cl_spider.app.models import Picture
from cl_spider.spiders.manager import Manager

WAIT_TIME_MIN = 1
WAIT_TIME_MAX = 5

def download_image(url):
    pass

class PictureManager(Manager):
    def __init__(self) -> None:
        super().__init__()

class PictureSpider(Spider):
    def __init__(self, headers: Dict[Text, Text] = None,
                    manager: Optional[PictureManager] = None,) -> None:
        super().__init__(headers=headers)
        self.manager = manager if manager else PictureManager()
    
    @property
    def random_sleep(self, min:Optional[int]=WAIT_TIME_MIN, max: Optional[int]=WAIT_TIME_MAX,) -> None:
        time.sleep(random.randint(min, max))

    def load_data(self, url):
        pass

    def parse_data(self, data) -> Dict:
        parsed_data = {}
        return parsed_data

    def save_data(self, parse_data: Dict) -> None:
        pass

    def get_latest(self) -> None:
        # 是否有待取的 URL
        while self.manager.has_new_url():
            self.random_sleep
            # 获取一个新 URL
            url = self.manager.get_new_url()
            # 获取网页信息
            data = self.load_data(url)
            # 解析网页信息
            parsed_data = self.parse_data(data)
            # 保留有效信息
            self.save_data(parsed_data)
