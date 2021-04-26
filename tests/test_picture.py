import unittest
from cl_spider.spiders.picture import PictureSpider

TEST_URL = "https://cl.192x.xyz/htm_mob/2104/7/4459009.html"


class PictureSpiderTest(unittest.TestCase):
    @staticmethod
    def _create_picture_spider() -> PictureSpider:
        return PictureSpider.load(urlset=set([TEST_URL]))

    def test_picture_spider(self):
        ps = self._create_picture_spider()
        ps.get_latest()

    def test_load_data(self):
        url = TEST_URL
        ps = PictureSpider()
        data = ps.load_data(url)
        print(data)

    def test_parse_data(self):
        url = TEST_URL
        ps = PictureSpider()
        data = ps.load_data(url)
        result = ps.parse_data(url, data)
        print(result)
