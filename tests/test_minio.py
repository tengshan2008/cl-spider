import os
import random
import unittest

from cl_spider.config import (MINIO_ACCESS_KEY, MINIO_SECRET_KEY,
                              MINIO_SERVER_PORT, MINIO_SERVER_HOST)
from cl_spider.spiders.file_uploader import Uploader


class MinioTest(unittest.TestCase):
    @staticmethod
    def load_default_uploader() -> Uploader:
        return Uploader()

    @staticmethod
    def load_uploader() -> Uploader:
        endpoint = f'{MINIO_SERVER_HOST}:{MINIO_SERVER_PORT}'
        config = {
            "endpoint": endpoint,
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

    def test_share_object(self):
        uploader = self.load_uploader()

        bucket_name = 'picture'
        object_name = '[动图GIF0519]午间发车，上高速_[60P]/60.gif'

        share = uploader.get_object_share(bucket_name, object_name)
        print(share)


if __name__ == "__main__":
    unittest.main()

# http://raspberrypi4.local:9090/picture/%5B%E5%8A%A8%E5%9B%BEGIF0519%5D%E5%8D%88%E9%97%B4%E5%8F%91%E8%BD%A6%EF%BC%8C%E4%B8%8A%E9%AB%98%E9%80%9F_%5B60P%5D/60.gif?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=admin%2F20210609%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210609T145610Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=109155677fa7befc144f297e9e82242a4eaec761fe7999992e07be8037f12561
# http://raspberrypi4.local:9090/picture/%5B%E5%8A%A8%E5%9B%BEGIF0519%5D%E5%8D%88%E9%97%B4%E5%8F%91%E8%BD%A6%EF%BC%8C%E4%B8%8A%E9%AB%98%E9%80%9F_%5B60P%5D/60.gif?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=admin%2F20210609%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210609T145655Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=472d51c94e431e24acba498ce453239aa9b74ce8c18d7e2340efd65848f88bd0
