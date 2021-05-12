from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional, Set, Text, Tuple

from bs4 import BeautifulSoup
from cl_spider.app import db
from cl_spider.app.models import Picture
from cl_spider.config import PICTURE_BUCKET_NAME
from cl_spider.spiders.file_uploader import IMG_EXTS, Uploader
from cl_spider.spiders.manager import Manager
from cl_spider.spiders.spider import Spider
from loguru import logger

IMG_ATTRS = ['data-src', 'data-ssa', 'ess-data']


class PictureManager(Manager):
    def __init__(self, limit: Optional[int] = None) -> None:
        super().__init__(limit=limit)


class PictureSpider(Spider):
    def __init__(
        self,
        headers: Dict[Text, Text] = None,
        manager: Optional[PictureManager] = None,
        limit: Optional[int] = None,
    ) -> None:
        super().__init__(headers=headers)
        self.manager = manager if manager else PictureManager(limit=limit)

    def load_data(self, url: Text) -> BeautifulSoup:
        logger.info(f"route is '{self.format_url(url)}', have loaded.")
        return self.open(url)

    def parse_tid(self, url: Text) -> Text:
        return url.split('/')[-1][:-5]

    def parse_title(self, url: Text, data: BeautifulSoup) -> Text:
        title = data.head.title.string.strip()

        title = title.replace('技術討論區', '')
        title = title.replace('草榴社區', '')
        title = title.replace('t66y.com', '')
        title = self.format_string(title)

        if f"[{self.number_of_imgs}P]" in title:
            title = title.replace(f"[{self.number_of_imgs}P]", "")
        return f"{title}_[{self.number_of_imgs}P]"

    def parse_author(self, data: BeautifulSoup) -> Text:
        users = data.find_all(name='div', attrs={'class': 'tpc_detail f10 fl'})
        names = data.find_all(name='b')

        if len(users) > 0:
            return list(users[0].strings)[0]
        elif len(names) > 0:
            return names[3].string
        else:
            logger.warning("not find author")
            return "unknow"

    def parse_imgs(self, data: BeautifulSoup):
        imgs = data.body.find_all('img')
        for i, img in enumerate(imgs):
            link = ""
            for attr in IMG_ATTRS:
                if attr in img.attrs:
                    link = img[attr]
                    break
            else:
                if "src" in img.attrs:
                    logger.info(f'find other picture: {img["src"]}')
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

        self.parsed_data['tid'] = self.parse_tid(url)
        self.parsed_data['imgs'] = list(self.parse_imgs(data))
        self.parsed_data['title'] = self.parse_title(url, data)
        self.parsed_data['author'] = self.parse_author(data)

        logger.info(f"route is '{self.format_url(url)}', have parsed "
                    f"{self.number_of_imgs} imgs.")
        return self.parsed_data

    def check_object_not_exists(self, url: Text) -> bool:
        return Picture.query.filter_by(link=url).first() is None

    def exec_minio(
        self,
        uploader: Uploader,
        bucket_name: Text,
        object_name: Text,
        data: bytes,
        file_type: Text,
    ) -> Tuple[Text, Text]:
        import cl_spider.utils

        uploader.put_object_with_file_type(bucket_name,
                                           object_name,
                                           BytesIO(data),
                                           file_type=file_type)
        share = uploader.get_object_share(bucket_name, object_name)
        size = uploader.stat_object_size(bucket_name, object_name)
        return share, cl_spider.utils.bit2humanView(size)

    def exec_database(
        self,
        parsed_data: Dict[Text, Any],
        title: Text,
        size: Text,
        link: Text,
        share: Text,
    ) -> None:
        picture = Picture(
            origin_id=parsed_data['tid'],
            title=title,
            size=size,
            author=parsed_data['author'],
            public_datetime=datetime.now(),
            link=link,
            share=share,
        )
        db.session.add(picture)
        db.session.commit()

    def save_data(
        self,
        url: Text,
        parsed_data: Dict[Text, Any],
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        if parsed_data is None:
            return None
        if self.number_of_imgs == 0:
            self.manager.add_new_url(url)
            return None

        bucket_name = PICTURE_BUCKET_NAME
        uploader = Uploader(metadata)
        uploader.create_bucket(bucket_name)

        for url, name, ext in parsed_data["imgs"]:
            if self.check_object_not_exists(url):
                response = self.download(url)
                if response:
                    object_name = f"{parsed_data['title']}/{name}"
                    share, size = self.exec_minio(uploader, bucket_name,
                                                  object_name,
                                                  response.content, ext)
                    if share:
                        self.exec_database(parsed_data, object_name, size, url,
                                           share)

    def get_latest(self, metadata: Optional[Dict[Text, Any]] = None) -> None:
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
            self.save_data(url, parsed_data, metadata)

    @classmethod
    def load(cls, urlset: Set[Text]) -> "PictureSpider":
        manager = PictureManager()
        manager.add_new_urls(urlset=urlset)
        return cls(manager=manager)
