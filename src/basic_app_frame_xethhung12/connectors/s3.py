import os
import logging
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

logger = logging.getLogger(__name__)


class S3Context:
    """
    A context containing an active connection session and client to S3,
    along with helper methods to perform common operations on S3.
    """

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        endpoint_url: str,
        bucket_name: str,
        config: Optional[Config] = None,
        client_name: str = "s3",
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        self.client_name = client_name
        self.config = config

        # Create a session
        self.session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.region_name,
        )

        # Create client
        self.client = self.session.client(
            client_name,
            endpoint_url=self.endpoint_url,
            config=self.config,
        )
    
    def get_session(self):
        return self.session

    def get_client(self):
        return self.client


    def upload_file(
        self,
        file_path: str,
        key: str,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Uploads a local file to S3.

        Args:
            file_path: Path to the local file.
            key: S3 key (destination path).
            bucket_name: Optional S3 bucket name (falls back to default bucket).
            extra_args: Optional extra arguments to pass to boto3.

        Returns:
            True if upload succeeded, False otherwise.
        """
        resolved_bucket = self.bucket_name
        try:
            self.get_client().upload_file(file_path, self.bucket_name, key, ExtraArgs=extra_args)
            logger.info(f"Uploaded {file_path} to s3://{self.bucket_name}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {file_path} to s3://{resolved_bucket}/{key}: {e}")
            return False

    def upload_bytes(
        self,
        data: bytes,
        key: str,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Uploads raw bytes to S3.

        Args:
            data: Raw bytes to upload.
            key: S3 key (destination path).
            bucket_name: Optional S3 bucket name.
            extra_args: Optional extra arguments to pass to boto3.

        Returns:
            True if upload succeeded, False otherwise.
        """
        resolved_bucket = self.bucket_name
        try:
            self.get_client().put_object(Body=data, Bucket=resolved_bucket, Key=key, **(extra_args or {}))
            logger.info(f"Uploaded bytes data to s3://{resolved_bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload bytes to s3://{resolved_bucket}/{key}: {e}")
            return False

    def upload_string(
        self,
        data: str,
        key: str,
        encoding: str = "utf-8",
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Uploads a string to S3.

        Args:
            data: String data to upload.
            key: S3 key (destination path).
            bucket_name: Optional S3 bucket name.
            encoding: Text encoding to use (default: utf-8).
            extra_args: Optional extra arguments to pass to boto3.

        Returns:
            True if upload succeeded, False otherwise.
        """
        return self.upload_bytes(
            data.encode(encoding), key, extra_args=extra_args
        )

    def download_file(
        self, key: str, file_path: str
    ) -> bool:
        """
        Downloads an object from S3 to a local file.

        Args:
            key: S3 key (object path).
            file_path: Local file path where the object will be saved.
            bucket_name: Optional S3 bucket name.

        Returns:
            True if download succeeded, False otherwise.
        """
        resolved_bucket = self.bucket_name
        try:
            self.get_client().download_file(resolved_bucket, key, file_path)
            logger.info(f"Downloaded s3://{resolved_bucket}/{key} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Failed to download s3://{resolved_bucket}/{key} to {file_path}: {e}")
            return False

    def download_bytes(self, key: str) -> Optional[bytes]:
        """
        Downloads an object from S3 and returns it as bytes.

        Args:
            key: S3 key.
            bucket_name: Optional S3 bucket name.

        Returns:
            Object content as bytes, or None if download failed.
        """
        resolved_bucket = self.bucket_name
        try:
            response = self.get_client().get_object(Bucket=resolved_bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Failed to download bytes from s3://{resolved_bucket}/{key}: {e}")
            return None

    def download_string(
        self, key: str, encoding: str = "utf-8"
    ) -> Optional[str]:
        """
        Downloads an object from S3 and returns it as a string.

        Args:
            key: S3 key.
            bucket_name: Optional S3 bucket name.
            encoding: Text decoding to use (default: utf-8).

        Returns:
            Object content as a string, or None if download failed.
        """
        content_bytes = self.download_bytes(key)
        if content_bytes is not None:
            return content_bytes.decode(encoding)
        return None

    def object_exists(self, key: str) -> bool:
        """
        Checks if an object exists in a bucket.

        Args:
            key: S3 key.
            bucket_name: Optional S3 bucket name.

        Returns:
            True if the object exists, False otherwise.
        """
        resolved_bucket = self.bucket_name
        try:
            self.get_client().head_object(Bucket=resolved_bucket, Key=key)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                return False
            logger.warning(f"Failed to check object existence for s3://{resolved_bucket}/{key}: {e}")
            return False

    def list_objects(self, prefix: str = "") -> List[str]:
        """
        Lists all object keys in a bucket matching the given prefix.

        Args:
            prefix: Key prefix to filter by.
            bucket_name: Optional S3 bucket name.

        Returns:
            A list of keys matching the prefix.
        """
        resolved_bucket = self.bucket_name
        keys = []
        paginator = self.get_client().get_paginator("list_objects_v2")
        try:
            pages = paginator.paginate(Bucket=resolved_bucket, Prefix=prefix)
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        keys.append(obj["Key"])
            return keys
        except ClientError as e:
            logger.error(
                f"Error listing objects in s3://{resolved_bucket} with prefix '{prefix}': {e}"
            )
            return []

    def delete_object(self, key: str) -> bool:
        """
        Deletes an object from S3.

        Args:
            key: S3 key.
            bucket_name: Optional S3 bucket name.

        Returns:
            True if deletion succeeded, False otherwise.
        """
        resolved_bucket = self.bucket_name
        try:
            self.get_client().delete_object(Bucket=resolved_bucket, Key=key)
            logger.info(f"Deleted object s3://{resolved_bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete object s3://{resolved_bucket}/{key}: {e}")
            return False


class S3Connector:
    """
    A connector class that stores connection parameters lazily.
    Connections are initialized only when calling get_context().
    """

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        endpoint_url: str,
        bucket_name: str,
        client_name: str = "s3",
        config: Optional[Config] = None,
    ):
        # Store configuration parameters lazily, loading defaults from environment if needed
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.bucket_name =  bucket_name
        self.client_name = client_name
        self.config = config

    def get_connection(self) -> S3Context:
        """
        Lazily creates and returns an S3Context containing the active boto3 session and client connection.
        """
        return S3Context(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            bucket_name=self.bucket_name,
            client_name=self.client_name,
            config=self.config,
        )
    
def connect(
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        endpoint_url: str,
        bucket_name: str,
        client_name: str = "s3",
        config: Optional[Config] = None,
) -> S3Context:
    """
    A convenience function to create an S3Context directly without needing to instantiate S3Connector.
    """
    return S3Connector(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        endpoint_url=endpoint_url,
        bucket_name=bucket_name,
        client_name=client_name,
        config=config,
    )