# Features:
# - Login with authentik
# - Provide own URL

# - Install as a service

import argparse
import json
import os

import authentik_integration
import wallpaper_utils
import change_wallpaper

config_location = f"{wallpaper_utils.get_config_dir('heic-wallpaper')}/config.json"

parser = argparse.ArgumentParser(
    description="A CLI tool to change the wallpaper. When no arguments are provided, the wallpaper will be changed to the configured wallpaper. When no wallpaper is configured, no changes will be made",
    epilog="This is a CLI tool to change wallpaper based on timing info",
)

global_subparsers = parser.add_subparsers()
auth_subparser = global_subparsers.add_parser("auth",
                                              help="Login/out to the wallpaper service")
subparser_auth = auth_subparser.add_subparsers(dest='auth')
subparser_auth.add_parser("login", help="Login to the wallpaper service")
subparser_auth.add_parser("logout", help="Logout of the wallpaper service")

wallpaper_subparser = global_subparsers.add_parser("wallpaper",
                                                   help="Change the wallpaper")
wallpaper_subparser.add_argument(
    "uuid",
    help="The UUID or URL of the wallpaper to change to. Specify 'account' to change to the account wallpaper",
)

args = parser.parse_args()
print(args)


def write_to_config(key, value):
    if not os.path.exists(config_location):
        data = {}
    else:
        with open(config_location, "r") as f:
            data = json.load(f)

    data[key] = value

    with open(config_location, "w") as f:
        json.dump(data, f)


def read_from_config(key):
    if not os.path.exists(config_location):
        return None

    with open(config_location, "r") as f:
        data = json.load(f)
    return data[key]


if "auth" in args:
    if args.auth == "login":
        print("Trying to log in")
        if read_from_config("access_token") is None:
            access, id = authentik_integration.login_request()
            write_to_config("access_token", access)
            write_to_config("id_token", id)
        else:
            print("Already logged in")
            access = read_from_config("access_token")
        user = authentik_integration.get_user(access)
        print(f"Welcome {user['name']}")
        print("You can now use the wallpaper command to change the wallpaper")
    elif args.auth == "logout":
        print("Logging out")
        write_to_config("access_token", None)
        write_to_config("id_token", None)
elif "uuid" in args:
    if args.uuid == "account":
        access = read_from_config("access_token")
        if access is None:
            print("Please login first, using 'auth login'")
            exit(1)

        wallpaper_url = authentik_integration.get_user_background_url(access)
        if wallpaper_url is None:
            print(
                "No wallpaper set on your account, please set a wallpaper on the website")
            exit(1)
        print(f"Changing wallpaper to {wallpaper_url}")

        uuid = change_wallpaper.get_uuid_from_url(wallpaper_url)
    else:
        uuid = change_wallpaper.get_uuid_from_url(args.uuid)

    print(f"Changing wallpaper to {uuid}")
    change_wallpaper.make_available_offline(uuid)
    path = change_wallpaper.get_correct_photo_for_wallpaper(uuid)
    wallpaper_utils.set_wallpaper(path)
