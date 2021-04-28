import unittest
from cl_spider.spiders.file_uploader import Uploader
import random
import os


class MinioTest(unittest.TestCase):
    @staticmethod
    def load_uploader() -> Uploader:
        config = {
            "endpoint": "raspberrypi4.local:9090",
            "access_key": "admin",
            "secret_key": "8rO8qpl3VASXagqX",
        }
        return Uploader(config)

    def test_minio_make_bucket(self):
        uploader = self.load_uploader()
        bucket_name = f"bucket-{random.randint(1, 100)}"
        uploader.make_bucket(bucket_name)

        self.assertTrue(uploader.bucket_exists(bucket_name))

    def test_put_object(self):
        uploader = self.load_uploader()
        bucket_name = f"bucket-{random.randint(1, 100)}"
        uploader.create_bucket(bucket_name)

        object_name = "true_cat.jpeg"
        with open(f"tests/{object_name}", 'rb') as f:
            file_stat = os.stat(object_name)
            uploader.put_object_with_file_type(bucket_name,
                                               object_name,
                                               f,
                                               length=file_stat.st_size,
                                               file_type="jpeg")


if __name__ == "__main__":
    unittest.main()
