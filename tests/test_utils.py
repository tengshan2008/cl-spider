import cl_spider.utils
import unittest


class UtilsTest(unittest.TestCase):
    def test_request_source_url(self):
        url, update = cl_spider.utils.request_source_url()
        print(url, update)

    def test_get_source_url(self):
        url, update = cl_spider.utils.get_source_url()
        print(url, update)
