from io import StringIO, BytesIO

from PIL import Image
from botocore.client import BaseClient

from backend.config import AppConfig


def open_image(s3_instance: BaseClient, key: str) -> Image:
    obj = s3_instance.get_object(Bucket=AppConfig.UPLOAD.BUCKET, Key=key)

    tmp = BytesIO(obj["Body"].read())
    tmp.seek(0)
    return Image.open(tmp)


def generate_preview(s3_instance: BaseClient, image: Image, uid: str) -> None:
    image.thumbnail((1280, 720))
    tmp = BytesIO()
    image.save(
        tmp,
        quality=50,
        optimize=True,
        format='PNG',
    )
    tmp.seek(0)

    s3_instance.put_object(
        Bucket=AppConfig.RESULT.BUCKET,
        Key=f"{uid}/preview.png",
        Body=tmp.getvalue(),
        ACL="public-read",
        ContentType="image/png",
    )


def generate_normal_image(s3_instance: BaseClient, image: Image, uid: str,
                          idx: int) -> None:
    image.thumbnail((3840, 2160))

    tmp = BytesIO()
    image.save(
        tmp,
        format="PNG",
    )
    tmp.seek(0)

    s3_instance.put_object(
        Bucket=AppConfig.RESULT.BUCKET,
        Key=f"{uid}/{idx}.png",
        Body=tmp.getvalue(),
        ACL="public-read",
        ContentType="image/png",
    )
