from tests.test_picture import TEST_URL
import unittest
from cl_spider.spiders.spider import Spider

TEST_URL = "https://x6img.com/i/2021/04/24/fpnm9d.gif"


class SpiderTest(unittest.TestCase):
    def test_format_url(self):
        spider = Spider()

        url = spider.format_url(TEST_URL)
        self.assertEqual(url, "/i/2021/04/24/fpnm9d.gif")

    def test_download(self):
        spider = Spider()

        response = spider.download(TEST_URL)
        self.assertEqual(len(response.content), 990857)
