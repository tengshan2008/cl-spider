from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional, Set, Text, Tuple

from bs4 import BeautifulSoup
import dateutil.parser
from cl_spider.app import db
from cl_spider.app.models import Picture, PictureTask
from cl_spider.config import PICTURE_BUCKET_NAME
from cl_spider.spiders.file_uploader import IMG_EXTS, Uploader
from cl_spider.spiders.manager import Manager
from cl_spider.spiders.spider import Spider
from loguru import logger

TID_KEY = 'tid'
IMGS_KEY = 'imgs'
TITLE_KEY = 'title'
AUTHOR_KEY = 'author'
DATE_KEY = 'date'

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
        self.random_sleep
        logger.info(f"route is '{self.format_url(url)}', have loaded.")
        return self.open(url)

    def parse_date(self, data: BeautifulSoup) -> datetime:
        tipad = data.find('div', attrs={'class': 'tipad'})
        if tipad:
            tipad_text = tipad.stripped_strings
            return dateutil.parser.parse(
                list(tipad_text)[1].replace('Posted:', ''))
        return datetime.now()

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
        cnt = 1
        for img in imgs:
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
            name = f"{cnt}.{ext}"
            cnt += 1

            yield (link, name, ext)

    @property
    def number_of_imgs(self):
        return len(self.parsed_data.get(IMGS_KEY, []))

    def parse_data(self, url: Text, data: BeautifulSoup) -> Dict[Text, Any]:
        if data is None:
            self.manager.add_new_url(url)
            return None

        self.parsed_data = {}

        self.parsed_data[TID_KEY] = self.parse_tid(url)
        self.parsed_data[IMGS_KEY] = list(self.parse_imgs(data))
        self.parsed_data[TITLE_KEY] = self.parse_title(url, data)
        self.parsed_data[AUTHOR_KEY] = self.parse_author(data)
        self.parsed_data[DATE_KEY] = self.parse_date(data)

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
        size = uploader.stat_object_size(bucket_name, object_name)
        return cl_spider.utils.bit2humanView(size)

    def exec_database(
        self,
        parsed_data: Dict[Text, Any],
        name: Text,
        size: Text,
        link: Text,
        task_id: Text,
    ) -> None:
        picture = Picture(
            origin_id=parsed_data[TID_KEY],
            title=parsed_data[TITLE_KEY],
            pidx=name,
            size=size,
            author=parsed_data[AUTHOR_KEY],
            public_datetime=parsed_data[DATE_KEY],
            link=link,
            task_id=task_id,
        )
        try:
            db.session.add(picture)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            logger.error(f'picture execute database has error: {err}')
            raise err
        finally:
            db.session.close()

    def new_picture_task(self, task_id, links):
        for link in links:
            picture_task = PictureTask(task_id=task_id, link=link)
            db.session.add(picture_task)
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            logger.error(f'picture task execute database has error: {err}')
            raise err
        finally:
            db.session.close()

    def save_data(
        self,
        url: Text,
        task_id: Text,
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

        for url, name, ext in parsed_data[IMGS_KEY]:
            if self.check_object_not_exists(url):
                response = self.download(url)
                if response:
                    pub_date = parsed_data[DATE_KEY].strftime('%Y-%m')
                    object_name = f'{pub_date}/{parsed_data[TITLE_KEY]}/{name}'
                    size = self.exec_minio(uploader, bucket_name, object_name,
                                           response.content, ext)
                    if size:
                        self.exec_database(parsed_data, name, size, url,
                                           task_id)

    @logger.catch
    def get_latest(self, metadata: Optional[Dict[Text, Any]] = None) -> None:
        task_id = self.new_task('picture', 'P001')
        self.new_picture_task(task_id, list(self.manager.queue))
        # 是否有待取的 URL
        while self.manager.has_new_url():
            # 获取一个新 URL
            url = self.manager.get_new_url()
            # 获取网页信息
            data = self.load_data(url)
            # 解析网页信息
            parsed_data = self.parse_data(url, data)
            # 保留有效信息
            self.save_data(url, task_id, parsed_data, metadata)

    @classmethod
    def load(cls, urlset: Set[Text]) -> "PictureSpider":
        manager = PictureManager()
        manager.add_new_urls(urlset=urlset)
        return cls(manager=manager)
