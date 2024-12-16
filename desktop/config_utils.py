import os
import json

import wallpaper_utils

config_location = os.path.join(wallpaper_utils.get_config_dir('heic-wallpaper'), "config.json")

# TODO: Implement some kind of caching, to prevent continues IO operations during init

def get_config_full():
    data = {}
    try:
        if not os.path.exists(config_location):
            os.makedirs(os.path.dirname(config_location), exist_ok=True)
        else:
            with open(config_location, "r") as f:
                data = json.load(f)
    except Exception as err:
        print("Something went wrong with fetching the config from your disk", err)

    return data

def write_to_config(key, value):
    data = get_config_full()
    data[key] = value

    with open(config_location, "w") as f:
        json.dump(data, f)


def read_from_config(key):
    data = get_config_full()
    return data.get(key, None)