import unittest
from cl_spider.spiders.picture import PictureSpider

TEST_URL = "https://cl.192x.xyz/htm_mob/2104/7/4459009.html"


class PictureSpiderTest(unittest.TestCase):
    def test_load_data(self):
        url = TEST_URL
        ps = PictureSpider()
        data = ps.load_data(url)
        print(data)
