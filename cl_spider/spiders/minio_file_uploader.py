from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)


class Uploader:
    def __init__(self, config) -> None:
        self.minioClient = Minio(config['endpoint'],
                                 access_key=config['access_key'],
                                 secret_key=config['secret_key'])

    def make_bucket(self, bucket_name, location):
        try:
            self.minioClient.make_bucket(bucket_name, location)
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            raise

    def bucket_exists(self, bucket_name):
        try:
            return self.minioClient.bucket_exists(bucket_name)
        except ResponseError as err:
            raise

    def put_object(self, bucket_name, object_name, data):
        try:
            result = self.minioClient.put_object(bucket_name,
                                                 object_name,
                                                 data,
                                                 length=-1,
                                                 part_size=10*1024*1024)
            print(f"created {result.object_name} object; etag: {result.etag}, "
                  f"version-id: {result.version_id}")
        except ResponseError as err:
            raise
