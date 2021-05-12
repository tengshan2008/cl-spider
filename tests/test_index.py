from cl_spider.spiders.novel import IndexSpider
import unittest

TEST_URL = 'https://cl.192x.xyz/thread0806.php?fid=20&page=1'
TEST_HOST_URL = 'https://cl.192x.xyz/thread0806.php'


class IndexSpiderText(unittest.TestCase):
    def test_load_data(self):
        ins = IndexSpider()
        data = ins.load_data(TEST_URL)
        print(data)

    def test_get_pages(self):
        ins = IndexSpider()
        pages = ins.get_pages(TEST_HOST_URL, 1, 5)
        print(pages)

    def test_parse_data(self):
        url = 'https://cl.192x.xyz/thread0806.php?fid=20&page=4'
        ins = IndexSpider()
        data = ins.load_data(url)
        parsed_data = ins.parse_data(url, data)
        print(parsed_data)

    def test_get_latest(self):
        ins = IndexSpider()
        ins.get_latest(TEST_URL, 1, 3)
