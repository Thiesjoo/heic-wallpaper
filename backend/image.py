from io import StringIO

from PIL import Image
from botocore.client import BaseClient

from backend.config import AppConfig


def open_image(s3_instance: BaseClient, key: str) -> Image:
    obj = s3_instance.get_object(Bucket=AppConfig.UPLOAD.S3_BUCKET, Key=key)
    return Image.open(obj["Body"])


def generate_preview(s3_instance: BaseClient, image: Image, uid: str) -> None:
    image.thumbnail((1280, 720))
    tmp = StringIO()
    image.save(
        tmp,
        quality=50,
        optimize=True,
    )

    s3_instance.put_object(
        Bucket=AppConfig.RESULT.S3_BUCKET,
        Key=f"{uid}/preview.jpg",
        Body=tmp.getvalue(),
        ACL="public-read",
        ContentType="image/jpeg",
    )


def generate_normal_image(s3_instance: BaseClient, image: Image, uid: str,
                          idx: int) -> None:
    image.thumbnail((3840, 2160))

    s3_instance.put_object(
        Bucket=AppConfig.RESULT.S3_BUCKET,
        Key=f"{uid}/{idx}.png",
        Body=image,
        ACL="public-read",
        ContentType="image/png",
    )
