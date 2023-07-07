from PIL import Image

from backend.config import AppConfig


def open_image(filename: str) -> Image:
    return Image.open(filename)

def generate_preview(image: Image, uid: str) -> None:
    image.thumbnail((1280, 720))


    image.save(
        f"{AppConfig.PROCESSED_FOLDER}/{uid}/preview.png",
        quality=50,
        optimize=True,
    )

def generate_normal_image(image: Image, uid: str, idx: int) -> None:
    image.thumbnail((3840, 2160))
    image.save(
        f"{AppConfig.PROCESSED_FOLDER}/{uid}/{idx}.png",
    )
