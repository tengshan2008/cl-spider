from io import BytesIO
from typing import Any, Dict, Optional, Text

from cl_spider.config import MINIO_ACCESS_KEY, MINIO_ENDPOINT, MINIO_SECRET_KEY
# from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
#                          BucketAlreadyExists)
from loguru import logger
from minio import Minio

IMG_EXTS = ['png', 'jpg', 'jpeg', 'gif']
TXT_EXT = 'txt'


class Uploader:
    def __init__(self, metadata: Optional[Dict[Text, Any]] = None) -> None:
        if metadata is None:
            self.minioClient = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=False,
            )
        else:
            self.minioClient = Minio(
                metadata['endpoint'],
                access_key=metadata['access_key'],
                secret_key=metadata['secret_key'],
                secure=False,
            )

    def make_bucket(self,
                    bucket_name: Text,
                    location: Optional[Text] = "cn-north-1") -> None:
        try:
            self.minioClient.make_bucket(bucket_name, location)
        # except BucketAlreadyOwnedByYou as err:
        #     logger.warning(f"bucket already owned by you. {err}")
        # except BucketAlreadyExists as err:
        #     logger.warning(f"bucket already exists. {err}")
        except Exception as err:
            logger.error(f"response error: {err}")
            raise

    def remove_bucket(self, bucket_name: Text) -> None:
        try:
            self.minioClient.remove_bucket(bucket_name)
        except Exception as err:
            logger.error(f"response error: {err}")
            raise

    def bucket_exists(self, bucket_name):
        try:
            return self.minioClient.bucket_exists(bucket_name)
        except Exception as err:
            logger.error(f"response error: {err}")
            raise

    def put_object_with_file_type(
        self,
        bucket_name: Text,
        object_name: Text,
        data: BytesIO,
        length: Optional[int] = None,
        file_type: Optional[Text] = None,
    ):
        length_data = length if length else len(data.getvalue())
        if file_type in IMG_EXTS:
            content_type = f"image/{file_type}"
        elif file_type == TXT_EXT:
            content_type = "text/plain"
        else:
            logger.warning("unknow content type")
            return
        try:
            result = self.minioClient.put_object(bucket_name,
                                                 object_name,
                                                 data,
                                                 length_data,
                                                 content_type=content_type)
        except Exception as err:
            logger.error(f"response error: {err}")
            raise
        else:
            logger.info(
                f"created {result.object_name} object; etag: {result.etag}")

    def stat_object_size(self, bucket_name: Text, object_name: Text):
        try:
            obj = self.minioClient.stat_object(bucket_name, object_name)
        except Exception as err:
            logger.error(f"response error: {err}")
            raise
        else:
            return obj.size

    def get_object_share(self, bucket_name: Text, object_name: Text):
        try:
            share = self.minioClient.presigned_get_object(
                bucket_name, object_name)
        except Exception as err:
            logger.error(f"response error: {err}")
            raise
        else:
            return share

    def get_object(self, bucket_name: Text, object_name: Text):
        # try:
        #     data = self.minioClient.get_object(bucket_name, object_name)
        #     data.stream()
        pass

    def create_bucket(self, bucket_name: Text) -> None:
        if not self.bucket_exists(bucket_name):
            self.make_bucket(bucket_name)
