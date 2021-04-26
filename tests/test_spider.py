import unittest
from cl_spider.spiders.spider import Spider

class SpiderTest(unittest.TestCase):
    def test_format_url(self):
        spider = Spider()
        
        spider.format_url('https://x6img.com/i/2021/04/24/fpnm9d.gif')
