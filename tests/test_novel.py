import unittest
from cl_spider.spiders.novel import NovelSpider

TEST_SINGLE_PAGE = 'https://cl.192x.xyz/htm_data/2105/20/4487838.html'
TEST_MULTIPLE_PAGE = 'https://cl.192x.xyz/htm_data/2104/20/4456719.html'
TEST_SINGLE_PAGE = 'https://cl.135x.xyz/htm_data/2009/20/4076366.html'


class NovelSpiderTest(unittest.TestCase):
    def test_load_data(self):
        ns = NovelSpider()
        data = ns.load_data(TEST_SINGLE_PAGE)
        print(data)

    def test_single_page_get_pages(self):
        ns = NovelSpider()
        pages = ns.get_pages(TEST_SINGLE_PAGE)
        print(pages)

    def test_multiple_page_get_pages(self):
        ns = NovelSpider()
        pages = ns.get_pages(TEST_MULTIPLE_PAGE)
        print(pages)

    def test_single_page_parse_data(self):
        url = TEST_SINGLE_PAGE
        ns = NovelSpider()
        data = ns.load_data(url)
        ns.parse_data(url, data)
        print(ns.parsed_data)

    def test_multiple_page_parse_data(self):
        url = TEST_MULTIPLE_PAGE
        ns = NovelSpider()
        data = ns.load_data(url)
        parsed_data = ns.parse_data(url, data)
        print(parsed_data)

    def test_get_latest(self):
        ns = NovelSpider()
        ns.get_latest(TEST_MULTIPLE_PAGE)
