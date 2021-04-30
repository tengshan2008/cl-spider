from typing import Any, Dict, Optional, Set, Text

from bs4 import BeautifulSoup
from cl_spider.app import db
from cl_spider.app.models import Picture
from cl_spider.spiders.file_uploader import Uploader
from cl_spider.spiders.manager import Manager
from cl_spider.spiders.spider import Spider
from loguru import logger

IMG_EXTS = ['png', 'jpg', 'gif']
IMG_ATTRS = ['data-src', 'data-ssa', 'ess-data']


class PictureManager(Manager):
    def __init__(self) -> None:
        super().__init__()


class PictureSpider(Spider):
    def __init__(
        self,
        headers: Dict[Text, Text] = None,
        manager: Optional[PictureManager] = None,
    ) -> None:
        super().__init__(headers=headers)
        self.manager = manager if manager else PictureManager()

    def load_data(self, url: Text) -> BeautifulSoup:
        logger.info(f"route is '{self.format_url(url)}', have loaded.")
        return self.open(url)

    def parse_tid(self, url: Text) -> Text:
        return url.split('/')[-1][:-5]

    def parse_title(self, url: Text, data: BeautifulSoup) -> Text:
        title = data.head.title.string.strip()

        tid = self.parse_tid(url)
        title = self.format_string(title)
        title = title.replace("技術討論區草榴社區", "")

        if f"[{self.number_of_imgs}P]" in title:
            title = title.replace(f"[{self.number_of_imgs}P]", "")
        return f"{title}_[{self.number_of_imgs}P]_{tid}"

    def parse_imgs(self, data: BeautifulSoup):
        imgs = data.body.find_all('img')
        for i, img in enumerate(imgs):
            link = ""
            for attr in IMG_ATTRS:
                if attr in img.attrs:
                    link = img[attr]
                    break
            else:
                logger.warning(f'unknow attr {img.attrs}')
                continue

            if '.' not in link:
                logger.warning(
                    f'route is {self.format_url(link)}, not found ext')
                continue
            ext = link.split('.')[-1].lower()

            if ext not in IMG_EXTS:
                logger.warning(
                    f'route is {self.format_url(link)}, ext is {ext}, not '
                    f'recognized')
                continue
            name = f"{i+1}.{ext}"

            yield (link, name, ext)

    @property
    def number_of_imgs(self):
        return len(self.parsed_data.get('imgs', []))

    def parse_data(self, url: Text, data: BeautifulSoup) -> Dict[Text, Any]:
        if data is None:
            self.manager.add_new_url(url)
            return None

        self.parsed_data = {}

        self.parsed_data['imgs'] = list(self.parse_imgs(data))
        self.parsed_data['tid'] = self.parse_tid(url)
        self.parsed_data['title'] = self.parse_title(url, data)

        logger.info(f"route is '{self.format_url(url)}', have parsed "
                    f"{self.number_of_imgs} imgs.")
        return self.parsed_data

    def save_data(self, url: Text, parsed_data: Dict[Text, Any],
                  config: Dict[Text, Any]) -> None:
        if parsed_data is None or self.number_of_imgs == 0:
            self.manager.add_new_url(url)
            return None

        bucket_name = f"picture/{parsed_data['title']}"
        uploader = Uploader(config)
        uploader.create_bucket(bucket_name)

        for url, name, ext in parsed_data["imgs"]:
            response = self.download(url)
            uploader.put_object_with_file_type(
                bucket_name,
                name,
                response.content,
                file_type=ext,
            )
            picture = Picture()
            db.session.add(picture)
            db.session.commit()

    def get_latest(self) -> None:
        # 是否有待取的 URL
        while self.manager.has_new_url():
            self.random_sleep
            # 获取一个新 URL
            url = self.manager.get_new_url()
            # 获取网页信息
            data = self.load_data(url)
            # 解析网页信息
            parsed_data = self.parse_data(url, data)
            # 保留有效信息
            self.save_data(url, parsed_data)

    @classmethod
    def load(cls, urlset: Set[Text]) -> "PictureSpider":
        manager = PictureManager()
        manager.add_new_urls(urlset=urlset)
        return cls(manager=manager)
