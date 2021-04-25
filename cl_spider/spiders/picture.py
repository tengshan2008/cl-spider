import random
import time
from typing import Any, Dict, List, Optional, Text

from bs4 import BeautifulSoup
from cl_spider.app.models import Picture
from cl_spider.spiders.manager import Manager
from cl_spider.spiders.spider import Spider
from loguru import logger

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
    def random_sleep(self, min: Optional[int] = WAIT_TIME_MIN, max: Optional[int] = WAIT_TIME_MAX,) -> None:
        time.sleep(random.randint(min, max))

    def load_data(self, url: Text) -> BeautifulSoup:
        return self.open(url)

    def parse_title(self, url: Text, data: BeautifulSoup, length_of_imgs: int) -> Text:
        title = data.head.title.string.strip()

        tid = url.split('/')[-1][:-5]
        title = self.format_string(title)
        title = title.replace("技術討論區草榴社區", "")

        if f"[{length_of_imgs}P]" in title:
            title = title.replace(f"[{length_of_imgs}P]", "")
        return f"{title}_[{length_of_imgs}P]_{tid}"

    def parse_imgs(self, data: BeautifulSoup):
        imgs = data.body.find_all('img')
        for i, img in enumerate(imgs):
            link = ""
            if "data-src" in img.attrs:
                link = img["data-src"]
            elif "data-ssa" in img.attrs:
                link = img["data-ssa"]
            elif "ess-data" in img.attrs:
                link = img["ess-data"]
            else:
                logger.warning()
                continue

            ext = link.split('.')[-1]
            if len(ext) > 7:
                continue
            name = f"{i+1}.{ext}"

            yield (link, name)

    def parse_data(self, url: Text, data: BeautifulSoup) -> Dict:
        parsed_data = {}

        parsed_data['imgs'] = list(self.parse_imgs(data))
        parsed_data['title'] = self.parse_title(url, data, len(parsed_data['imgs']))

        logger.info(f"route is '{self.format_url(url)}', have parsed.")
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
