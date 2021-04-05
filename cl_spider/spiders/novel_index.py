from typing import Dict, Text, Any
from cl_spider.app.models import Novel, db
from cl_spider.spiders.spider import Spider


class NovelSpider(Spider):
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        super().__init__(headers)

    def get_book_data(self, chapter_html):
        data = {}  # 小说的元信息
        return data

    @staticmethod
    def parse_html(content: Text) -> Dict[Text, Any]:
        return {}

    @staticmethod
    def exec_database(data: Dict) -> None:
        novel = Novel(
            origin_id=data["origin_id"],
            title=data["title"],
            author=data["author"],
        )
        if Novel.query.filter_by(origin_id=data["origin_id"]).first() is None:
            db.session.add(novel)
        else:
            novel = Novel.query.filter_by(origin_id=data["origin_id"]).first()
            db.session.update(novel)

    def get_latest_novel(self):
        # 获取网页信息
        content = ""
        # 解析网页信息
        data = self.parse_html(content)
        # 操作数据库
        self.exec_database(data)
        return None
