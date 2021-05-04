import os
import random
import unittest

from cl_spider.config import MINIO_ACCESS_KEY, MINIO_ENDPOINT, MINIO_SECRET_KEY
from cl_spider.spiders.file_uploader import Uploader


class MinioTest(unittest.TestCase):
    @staticmethod
    def load_default_uploader() -> Uploader:
        return Uploader()

    @staticmethod
    def load_uploader() -> Uploader:
        config = {
            "endpoint": MINIO_ENDPOINT,
            "access_key": MINIO_ACCESS_KEY,
            "secret_key": MINIO_SECRET_KEY,
        }
        return Uploader(config)

    def test_minio_make_bucket(self):
        # uploader = self.load_uploader()
        uploader = self.load_default_uploader()
        bucket_name = f"bucket-{random.randint(1, 100)}"
        uploader.make_bucket(bucket_name)

        self.assertTrue(uploader.bucket_exists(bucket_name))

        uploader.remove_bucket(bucket_name)
        self.assertFalse(uploader.bucket_exists(bucket_name))

    def test_put_object(self):
        uploader = self.load_uploader()
        bucket_name = f"bucket-{random.randint(1, 100)}"
        uploader.create_bucket(bucket_name)

        object_name = "true_cat.jpeg"
        file_path = f"tests/{object_name}"
        with open(file_path, 'rb') as f:
            file_stat = os.stat(file_path)
            uploader.put_object_with_file_type(bucket_name,
                                               f"picture/{object_name}",
                                               f,
                                               length=file_stat.st_size,
                                               file_type="jpeg")


if __name__ == "__main__":
    unittest.main()
