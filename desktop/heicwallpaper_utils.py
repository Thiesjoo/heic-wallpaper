from datetime import datetime
from typing import Literal, Any

import requests
import wallpaper_utils
import os
import json
import shutil

CONFIG_DIR = wallpaper_utils.get_config_dir("heic-wallpaper")

BASE_URL_STATIC = "https://static.wallpaper.thies.dev/"
BASE_URL_API = "https://wallpaper.thies.dev/api/wallpaper/"
BASE_URL_API_DETAILS = "https://wallpaper.thies.dev/api/wallpapers/"

class Wallpaper:
    id: int
    uid: str

    data: Any
    saved_for_offline_use = False

    def __init__(self, id: int, uid: str, data: Any):
        self.id = id
        self.uid = uid
        self.data = data

    def __str__(self):
        return f"<class: Wallpaper, with id={self.id},uid={self.uid}>"

    def encode(self):
        return json.dumps({
            "id": self.id,
            "uid": self.uid,
            "data": self.data
        }).encode()

    def save_to_file(self):
        with open(os.path.join(self.get_path(), "data.json"), 'wb') as f:
            f.write(self.encode())

    @staticmethod
    def decode_from_uuid_file(uid: str):
        path = os.path.join(os.path.join(CONFIG_DIR, uid), "data.json")
        if not os.path.exists(path):
            raise ValueError(f"Wallpaper is not saved for offline use, path {path} doesn't exist")

        with open(path, "r") as f:
            json_data = json.load(f)
        tmp = Wallpaper(
            json_data['id'],
            json_data['uid'],
            json_data.get("data")
        )
        tmp.saved_for_offline_use = True
        return tmp

    def get_path(self) -> str:
        return os.path.join(CONFIG_DIR, self.uid)

    def get_path_for_image(self, index: int | Literal["preview"]) -> str:
        return os.path.join(self.get_path(), f"{index}.png")

    def get_static_url_for_image(self, index: int | Literal["preview"]) -> str:
        return f"{BASE_URL_STATIC}{self.uid}/{index}.png"

    @staticmethod
    def from_uuid_or_url(uuid_or_url: str) -> "Wallpaper":
        if len(uuid_or_url) == 36:
            print(f"Returning a local copy of {uuid_or_url}")
            # Because we don't do BASE_URL_STATIC parsing, this can only be a cached wallpaper
            return Wallpaper.decode_from_uuid_file(uuid_or_url)
        elif uuid_or_url.startswith("https://"):
            if uuid_or_url.startswith(BASE_URL_STATIC):
                raise ValueError("API doesn't support getting wallpaper details by uid")
            elif uuid_or_url.startswith(BASE_URL_API) or uuid_or_url.startswith(BASE_URL_API_DETAILS):
                uuid = id_from_api_url(uuid_or_url)
            else:
                raise ValueError("Non-supported url")
        else:
            raise ValueError("URL is not a wallpaper URL from our app")

        request = requests.get(url_from_uuid(uuid))

        request.raise_for_status()
        data = request.json()

        return Wallpaper(
            data['id'],
            data['uid'],
            data.get("data", [])
        )

    def fetch_and_save_single_image(self, index: int | Literal["preview"]):
        file_path = self.get_path_for_image(index)

        if not os.path.exists(file_path):
            print("Fresh download: ", self, index)
            request = requests.get(self.get_static_url_for_image(index))
            request.raise_for_status()

            with open(file_path, 'wb') as f:
                f.write(request.content)

        return file_path

    def make_available_offline(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        wallpaper_path = os.path.join(CONFIG_DIR, self.uid)

        if os.path.exists(wallpaper_path):
            # Make sure the data.json file is there
            if not os.path.exists(os.path.join(wallpaper_path, "data.json")):
                # remove entire directory
                shutil.rmtree(wallpaper_path)
                raise ValueError("Wallpaper directory exists, but no data is present. We deleted the directory, you should try again.")

            # Data can change, so always save timestamps. Images (should) never change
            self.save_to_file()
            self.saved_for_offline_use = True
            print(f"Wallpaper {self} is already available offline")
            return

        os.makedirs(wallpaper_path, exist_ok=True)

        print(f"Fetching wallpaper {self} for offline use")

        if type(self.data) != list or len(self.data) == 0:
            self.data = [{'i': 0, 't': 0}]

        for item in self.data:
            self.fetch_and_save_single_image(item.get('i'))
        self.fetch_and_save_single_image('preview')

        self.save_to_file()
        self.saved_for_offline_use = True
        print(f"Wallpaper {self} is now available offline")


    def get_correct_wallpaper_for_time(self):
        """
        Get the correct photo for the current time.

        :param wallpaper_uuid:
        :return:
        """
        wallpaper_path = self.get_path()
        if not os.path.exists(wallpaper_path):
            raise ValueError(f"Wallpaper is not saved for offline use, path {wallpaper_path} doesn't exist")

        timing_info = self.data

        now = datetime.now().time()
        nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second

        # https://github.com/mczachurski/wallpapper
        last_one = timing_info[-1]
        for time in timing_info:
            if nowsecs > float(time["t"]) * 60 * 60 * 24:
                last_one = time
        index = last_one["i"]

        return self.get_path_for_image(index)

def url_from_uuid(wallpaper_uuid: str):
    return f'{BASE_URL_API_DETAILS}{wallpaper_uuid}/'

def id_from_api_url(url: str):
    # Something that looks like this: https://wallpaper.thies.dev/api/wallpaper/68333b06-c07c-4a45-b0c8-71f6d64072b9/
    return url.split('/')[-2]

# TODO:
# Bundle for multiple platforms inside GH Actions