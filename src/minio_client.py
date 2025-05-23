from pathlib import Path
from uuid import uuid4

from minio import Minio

from src.config import settings


def get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )


def upload_file_to_minio(path: Path, content_type: str = "video/mp4") -> str:
    client = get_minio_client()

    bucket = settings.MINIO_BUCKET_NAME
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    unique_filename = f"{uuid4()}_{path.name}"
    client.fput_object(
        bucket,
        unique_filename,
        file_path=str(path),
        content_type=content_type,
    )

    return f"http://{settings.MINIO_ENDPOINT}/{bucket}/{unique_filename}"