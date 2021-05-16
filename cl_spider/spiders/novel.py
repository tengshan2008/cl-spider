import urllib.parse
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional, Text, Tuple

import bs4.element
import dateutil.parser
from bs4 import BeautifulSoup
from cl_spider.app import db, thread_lock
from cl_spider.app.models import Novel
from cl_spider.config import NOVEL_BUCKET_NAME
from cl_spider.spiders.file_uploader import Uploader
from cl_spider.spiders.manager import Manager
from cl_spider.spiders.spider import Spider
from loguru import logger


TID_KEY = 'tid'
TITLE_KEY = 'title'
CATEGORY_KEY = 'category'
AUTHOR_KEY = 'author'
PUBLIC_DATETIME_KEY = 'public_datetime'
CONTENT_KEY = 'content'
CATEGORIES = [
    '[現代奇幻]', '[古典武俠]', '[另類禁忌]', '[性愛技巧]', '[笑話連篇]', '[有声小说]', '[其他交流]'
]


class IndexManager(Manager):
    def __init__(self, limit: Optional[int] = None) -> None:
        super().__init__(limit=limit)


class NovelManager(Manager):
    def __init__(self, limit: Optional[int] = None) -> None:
        super().__init__(limit=limit)


class IndexSpider(Spider):
    def __init__(
        self,
        headers: Dict[Text, Text] = None,
        manager: Optional[IndexManager] = None,
        limit: Optional[int] = None,
    ) -> None:
        super().__init__(headers=headers)
        self.manager = manager if manager else IndexManager(limit=limit)

    def load_data(self, url: Text) -> BeautifulSoup:
        self.random_sleep
        logger.info(f"route is '{self.format_url(url)}', have loaded")
        return self.open(url)

    def parse_link(self, url: Text, data: bs4.element.Tag) -> Text:
        return f"{self.format_url_host(url)}/{data.find('a')['href'].strip()}"

    def parse_tid(self, url: Text) -> Text:
        return url.split('/')[-1][:-5]

    def parse_title(self, data: bs4.element.Tag) -> Text:
        return list(data.find('a').stripped_strings)[0]

    def parse_category(self, data: bs4.element.Tag) -> Text:
        return list(
            data.find(name='td', attrs={
                'class': 'tal'
            }).stripped_strings)[0][1:-1]

    def parse_public_datetime(self, data: bs4.element.Tag) -> Text:
        base = data.find(name='div', attrs={'class': 'f12'})
        _date = base.string.strip()
        _time = base.span['title'].strip()
        if '今天' in _date or '昨天' in _date:
            _date, _time = _time, _date
            _date = _date.split(' ')[-1]
            _time = _date.split(' ')[-1]
        return dateutil.parser.parse(f'{_date} {_time}')

    def parse_author(self, data: bs4.element.Tag) -> Text:
        return data.find(name='a', attrs={'class': 'bl'}).string.strip()

    def parse_data(self, url: Text, data: BeautifulSoup) -> Dict[Text, Any]:
        body = data.find(name='tbody', attrs={'id': 'tbody'})
        records = body.find_all(name='tr', attrs={'class': 'tr3 t_one tac'})

        parsed_data = {}
        for record in records:
            link = self.parse_link(url, record)
            parsed_data[link] = {
                TID_KEY: self.parse_tid(link),
                TITLE_KEY: self.parse_title(record),
                CATEGORY_KEY: self.parse_category(record),
                PUBLIC_DATETIME_KEY: self.parse_public_datetime(record),
                AUTHOR_KEY: self.parse_author(record),
            }

        return parsed_data

    def sub_spider(
        self,
        parsed_data: Dict,
        metadata: Optional[Dict[Text, Any]] = None,
    ):
        for novel_url, novel_info in parsed_data.items():
            novel_spider = NovelSpider(novel_info=novel_info)
            novel_spider.get_latest(novel_url, metadata)

    def get_pages(self, url: Text, start: int, end: int) -> List[Text]:
        host = self.format_url_host(url)
        link = f"{host}/thread0806.php?fid=20"

        return [f'{link}&page={i}' for i in range(start, end + 1)]

    def get_latest(
        self,
        url: Text,
        start: int,
        end: int,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        try:
            pages = self.get_pages(url, start, end)
        except Exception as err:
            logger.error(f'index spider - get_pages has error: {err}')
            return None
        self.manager.add_new_urls(set(pages))

        while self.manager.has_new_url():
            url = self.manager.get_new_url()
            try:
                data = self.load_data(url)
                parsed_data = self.parse_data(url, data)
                self.sub_spider(parsed_data, metadata)
            except Exception as err:
                logger.error(f'index spider has error: {err}')
                continue


class NovelSpider(Spider):
    def __init__(
        self,
        headers: Dict[Text, Text] = None,
        manager: Optional[NovelManager] = None,
        novel_info: Optional[Dict[Text, Any]] = None,
        limit: Optional[int] = None,
    ) -> None:
        super().__init__(headers=headers)
        self.parsed_data = novel_info.copy() if novel_info else {}
        self.parsed_data[CONTENT_KEY] = {}
        self.manager = manager if manager else NovelManager(limit=limit)

    def load_data(self, url: Text) -> BeautifulSoup:
        self.random_sleep
        logger.info(f'route is "{self.format_url(url)}", have loaded.')
        return self.open(url)

    def parse_tid(self, url: Text) -> Text:
        if TID_KEY in url:
            r = urllib.parse.urlsplit(url)
            return urllib.parse.parse_qs(r.query)[TID_KEY][0]
        return url.split('/')[-1][:-5]

    def parse_title_category(self, data: BeautifulSoup) -> Tuple[Text, Text]:
        title = data.head.title.string.strip()
        title = title.replace('技術討論區', '')
        title = title.replace('草榴社區', '')
        title = title.replace('t66y.com', '')
        title = title.replace('成人文學交流區', '')
        title = self.format_string(title)

        for cate in CATEGORIES:
            if cate in title:
                return title.replace(cate, ''), cate[1:-1]
        return title, 'UNKNOW'

    def parse_public_datetime(self, data: BeautifulSoup) -> Text:
        tipad = data.find('div', attrs={'class': 'tipad'})
        if tipad:
            tipad_text = tipad.stripped_strings
            return dateutil.parser.parse(
                list(tipad_text)[1].replace('Posted:', ''))
        return datetime.now()

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

    def parse_content(self, data: BeautifulSoup) -> Text:
        cells = data.find_all(name='div', attrs={'class': 'tpc_content'})
        content = []
        for cell in cells:
            content += list(cell.stripped_strings)
        return '\n'.join(content)

    def parse_data(self, url: Text, data: BeautifulSoup) -> Dict[Text, Any]:
        if data is None:
            logger.warning(f'route is "{self.format_url(url)}", load failed.')
            self.manager.add_new_url(url)
            return None

        if 'page' not in url:
            if TID_KEY not in self.parsed_data:
                self.parsed_data[TID_KEY] = self.parse_tid(url)
            if (TITLE_KEY
                    not in self.parsed_data) or (CATEGORY_KEY
                                                 not in self.parsed_data):
                title, category = self.parse_title_category(data)
                self.parsed_data[TITLE_KEY] = title
                self.parsed_data[CATEGORY_KEY] = category
            if PUBLIC_DATETIME_KEY not in self.parsed_data:
                self.parsed_data[
                    PUBLIC_DATETIME_KEY] = self.parse_public_datetime(data)
            if AUTHOR_KEY not in self.parsed_data:
                self.parsed_data[AUTHOR_KEY] = self.parse_author(data)

        self.parsed_data[CONTENT_KEY][url] = self.parse_content(data)

    def exec_minio(
        self,
        uploader: Uploader,
        bucket_name: Text,
        object_name: Text,
        data: bytes,
    ) -> Text:
        uploader.put_object_with_file_type(bucket_name,
                                           object_name,
                                           BytesIO(data),
                                           file_type='txt')
        share = uploader.get_object_share(bucket_name, object_name)
        return share

    def exec_database(self, link: Text, share: Text, size: int) -> None:
        _query = Novel.query.filter_by(origin_id=self.parsed_data[TID_KEY])
        if _query.first():
            _query.update({
                Novel.size: str(size),
                Novel.updated_at: datetime.now(),
            })
            return

        novel = Novel(
            origin_id=self.parsed_data[TID_KEY],
            title=self.parsed_data[TITLE_KEY],
            author=self.parsed_data[AUTHOR_KEY],
            public_datetime=self.parsed_data[PUBLIC_DATETIME_KEY],
            category=self.parsed_data[CATEGORY_KEY],
            link=link,
            size=str(size),
            share=share,
        )
        try:
            thread_lock.acquire()
            db.session.add(novel)
            db.session.commit()
            thread_lock.release()
        except Exception as err:
            logger.error(f'novel execute database has error: {err}')
            raise err
        # db.session.add(novel)
        # db.session.commit()

    def merge_content(self, pages: List[Text]) -> Text:
        content = []
        for page in pages:
            if page in self.parsed_data[CONTENT_KEY]:
                content.append(self.parsed_data[CONTENT_KEY][page])

        return '\n'.join(content)

    def is_need_put_or_update(self, content: Text):
        row = Novel.query.filter_by(
            origin_id=self.parsed_data[TID_KEY]).first()
        return row is None or int(row.size) < len(content)

    def save_data(
        self,
        pages: List[Text],
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        if self.parsed_data is None:
            logger.warning(
                f'route is "{self.format_url(pages[0])}", parse failed.')
            return None

        bucket_name = NOVEL_BUCKET_NAME
        uploader = Uploader(metadata)
        uploader.create_bucket(bucket_name)

        content = self.merge_content(pages)
        if self.is_need_put_or_update(content):
            pub_date = self.parsed_data[PUBLIC_DATETIME_KEY].strftime('%Y-%m')
            object_name = f"{pub_date}/{self.parsed_data[TITLE_KEY]}.txt"
            share = self.exec_minio(uploader, bucket_name, object_name,
                                    content.encode(encoding="utf-8"))
            if share:
                self.exec_database(pages[0], share, len(content))

    def get_pages(self, url: Text) -> List[Text]:
        only_author_url = (f'{self.format_url_host(url)}/read.php'
                           f'?tid={self.parse_tid(url)}&toread=2')
        data = self.load_data(only_author_url)

        div_pages = data.find_all(name='div', attrs={'class': 'pages'})
        if len(div_pages) < 2:
            return [url]

        page_range = div_pages[0].find(name='a', attrs={
            'class': 'w70'
        }).input.get('value').split('/')

        return [only_author_url] + [
            f'{self.format_url_host(url)}/read.php'
            f'?tid={self.parse_tid(url)}&toread=2&page={i}'
            for i in range(2,
                           int(page_range[-1]) + 1)
        ]

    def get_latest(
        self,
        url: Text,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        try:
            pages = self.get_pages(url)
        except Exception as err:
            logger.error(f'novel spider - get_pages has error: {err}')
            return None
        self.manager.add_new_urls(set(pages))

        while self.manager.has_new_url():
            url = self.manager.get_new_url()
            try:
                data = self.load_data(url)
                self.parse_data(url, data)
            except Exception as err:
                logger.error(f'novel spider has error: {err}')
                continue
        try:
            self.save_data(pages, metadata)
        except Exception as err:
            logger.error(f'novel spider - save_data has error: {err}')
            return None
