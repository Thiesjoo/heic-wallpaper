from datetime import datetime
from typing import Literal

import requests
import wallpaper_utils
import os
import json

CONFIG_DIR = wallpaper_utils.get_config_dir("heic-wallpaper")


def url_from_uuid(wallpaper_uuid: str):
    return f'https://wallpaper.thies.dev/api/wallpaper/{wallpaper_uuid}'


def url_from_uuid_and_index(wallpaper_uuid: str,
                            index: int | Literal["preview"]) -> str:
    return f"https://static.wallpaper.thies.dev/{wallpaper_uuid}/{index}.png"


def id_from_static_url(url: str):
    filename = url.split('/')[-1]
    return filename.split('.')[0]


def fetch_and_save_wallpaper(wallpaper_uuid: str, index: int | Literal["preview"]):
    wallpaper_path = f'{CONFIG_DIR}/{wallpaper_uuid}/'

    if not os.path.exists(f'{wallpaper_path}/{index}.png'):
        request = requests.get(url_from_uuid_and_index(wallpaper_uuid, index))
        request.raise_for_status()

        with open(f'{wallpaper_path}/{index}.png', 'wb') as f:
            f.write(request.content)

    return f'{wallpaper_path}/{index}.png'


def make_available_offline(wallpaper_uuid: str):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    wallpaper_path = f'{CONFIG_DIR}/{wallpaper_uuid}/'
    os.makedirs(wallpaper_path, exist_ok=True)

    request = requests.get(f"{url_from_uuid(wallpaper_uuid)}/details")
    json_data = request.json()

    if "data" not in json_data:
        json_data["data"] = [{'i': 0, 't': 0}]

    for item in json_data['data']:
        fetch_and_save_wallpaper(wallpaper_uuid, item['i'])

    fetch_and_save_wallpaper(wallpaper_uuid, "preview")

    with open(f'{wallpaper_path}/data.json', 'wb') as f:
        f.write(json.dumps(json_data).encode())


def get_correct_photo_for_wallpaper(wallpaper_uuid: str):
    wallpaper_path = f'{CONFIG_DIR}/{wallpaper_uuid}/'
    if not os.path.exists(wallpaper_path):
        raise ValueError("Wallpaper is not saved for offline use")

    with open(f'{wallpaper_path}/data.json', 'rb') as f:
        data_raw = f.read()

    if data_raw is None:
        raise ValueError("Wallpaper data is missing")

    data = json.loads(data_raw)
    if "data" not in data:
        raise ValueError("Wallpaper data inside JSON is missing")

    timing_info = data['data']

    now = datetime.now().time()
    nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second

    # https://github.com/mczachurski/wallpapper
    last_one = timing_info[-1]
    for time in timing_info:
        if nowsecs > float(time["t"]) * 60 * 60 * 24:
            last_one = time
    index = last_one["i"]

    return f'{wallpaper_path}/{index}.png'


def main():
    uuid = "68333b06-c07c-4a45-b0c8-71f6d64072b9"

    make_available_offline(uuid)
    path = get_correct_photo_for_wallpaper(uuid)
    wallpaper_utils.set_wallpaper(path)


if __name__ == '__main__':
    main()

# TODO:
# Login with authentik and fetch current choice
# Install as a service
# Bundle for multiple platforms inside GH Actions

# BACKEND:
# Better validation for images
#     - Check exif
#     - Max filesize
#     - Correct filetype?
