import logging
import typing

import google.cloud.storage

LOG = logging.getLogger(__name__)


def bucket_construct(project: str, bucket: str) -> google.cloud.storage.bucket.Bucket:
    client = google.cloud.storage.Client(project)
    return client.bucket(bucket)


def put_raw(key: str, data: bytes, project: str, bucket: str) -> None:
    """
    Upload raw data to a Google Cloud Storage bucket

    params:
        key - Key or path the data will be stored at
        data - The data you want to upload, in bytes
        project - Name of the project to upload to
        bucket - Name of the bucket to upload to

    Example usage:
        with open('test.txt', 'rb') as f:
            data = f.read()
            put_raw('some_path/test.txt', data, 'some_project', 'some_bucket')
    """
    bucket = bucket_construct(project, bucket)
    blob = google.cloud.storage.blob.Blob(name=key, bucket=bucket)

    blob.upload_from_string(data, 'application/octet-stream')
    LOG.info(f'Successfully uploaded file to {key} in {bucket}')


def get_raw(key: str, bucket: google.cloud.storage.bucket.Bucket) -> bytes:
    """
    Download a raw file from a Google Cloud Storage bucket

    Example usage:
        bucket = bucket_construct('some_project', 'some_bucket')
        file = get_raw('some_path/test.txt', bucket)
    """
    blob = google.cloud.storage.blob.Blob(name=key, bucket=bucket)
    return blob.download_as_string()


def list_bucket(project: str, bucket: str, prefix: str = None) -> typing.List[typing.Any]:
    """
    List the contents of a Google Cloud Storage bucket

    Note - Attatch a prefix for nested levels

    Example usage:
        blobs = list_bucket('some_project', 'some_bucket', 'some/path/prefix'))
    """
    client = google.cloud.storage.Client(project)
    return list(client.list_blobs(bucket_or_name=bucket, prefix=prefix))
