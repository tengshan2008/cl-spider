from typing import Any, Dict, Optional, Text
from minio import Minio
# from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
#                          BucketAlreadyExists)
from loguru import logger


class Uploader:
    def __init__(self, config: Dict[Text, Any]) -> None:
        self.minioClient = Minio(
            config['endpoint'],
            access_key=config['access_key'],
            secret_key=config['secret_key'],
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
        data: bytes,
        length: Optional[int] = None,
        file_type: Optional[Text] = None,
    ):
        length_data = length if length else len(data)
        if file_type == "gif":
            content_type = "image/gif"
        elif file_type == "png":
            content_type = "image/png"
        elif file_type in ["jpg", "jpeg"]:
            content_type = "image/jpeg"
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
            print(f"created {result.object_name} object; etag: {result.etag}, "
                  f"version-id: {result.version_id}")

    def create_bucket(self, bucket_name: Text) -> None:
        if not self.bucket_exists(bucket_name):
            self.make_bucket(bucket_name)
