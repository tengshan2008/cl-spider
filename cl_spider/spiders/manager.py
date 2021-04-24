from collections import deque
from typing import Optional, Set, Text

LIMIT = 3

class Manager:
    def __init__(self, limit: Optional[int] = LIMIT) -> None:
        self.queue = deque() # 待抓取的网页
        self.visited = dict() # 已抓取的网页
        self.limit = limit # 进入待爬取队列重试上限

    def new_url_size(self) -> int:
        """获取待爬取 URL 集合的大小"""
        return len(self.queue)

    def old_url_size(self) -> int:
        """获取已爬取 URL 集合的大小"""
        return len(self.visited)

    def has_new_url(self) -> bool:
        """判断是否有待爬取的 URL"""
        return self.new_url_size() != 0

    def get_new_url(self) -> Text:
        """获取一个待爬取的 URL
           在已爬取中为该 URL 计数
        """
        new_url = self.queue.popleft() # 从左侧取出一个链接
        if new_url in self.visited: # 记录已经爬取
            self.visited[new_url] += 1
        else:
            self.visited[new_url] = 1
        return new_url
    
    def add_new_url(self, url: Optional[Text] = None) -> bool:
        """将新的单个 URL 添加到待爬取的 URL 集合
           若该 URL 已爬取，只要没超过限制范围，依然可以添加到待爬取集合
        """
        if url is None or url in self.queue:
            return False
        if url not in self.visited:
            self.queue.append(url)
            return True
        else: 
            if self.visited[url] < self.limit:
                self.queue.append(url)
                return True
            else:
                return False

    def add_new_urls(self, urlset: Optional[Set[Text]] = None) -> None:
        """将新的多个 URL 添加到待爬取的 URL 集合"""
        if urlset is None or len(urlset) == 0:
            return
        for url in urlset:
            self.add_new_url(url)
