from typing import Any, Dict, List, Text

from cl_spider.app.models import Novel, db
from cl_spider.spiders.manager import Manager
from cl_spider.spiders.spider import Spider


class NovelManager(Manager):
    def __init__(self) -> None:
        super().__init__()

    def get_new_novel(self):
        new_novel = self.queue.popleft()
        self.visited.add(new_novel)
        return new_novel

    def add_new_novel(self, novel: Novel):
        if novel is None:
            return False
        if novel not in self.queue and novel not in self.visited:
            self.queue.append(novel)

    def add_new_novels(self, novels: List[Novel]):
        if novels is None or len(novels) == 0:
            return
        for novel in novels:
            self.add_new_url(novel)


class IndexSpider(Spider):
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        super().__init__(headers=headers)

    def get_index_data(self):
        pass

    def parse_html(self):
        pass

    def exec_database(self):
        pass

class NovelSpider(Spider):
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        super().__init__(headers=headers)

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
            old_novel = Novel.query.filter_by(origin_id=data["origin_id"]).first()
            novel.created_at = old_novel.created_at
            db.session.update(novel)

    def get_latest_novel(self):
        # 获取网页信息
        content = ""
        # 解析网页信息
        data = self.parse_html(content)
        # 保留有效信息
        self.exec_database(data)
        return None
