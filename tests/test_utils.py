from cl_spider import utils
import unittest


class UtilsTest(unittest.TestCase):
    def test_get_source_url(self):
        url, update = utils.get_source_url()
        print(url, update)
