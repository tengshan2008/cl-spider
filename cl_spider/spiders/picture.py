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