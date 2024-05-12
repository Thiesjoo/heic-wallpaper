import argparse
import json
import os

import authentik_integration
import wallpaper_utils
import heicwallpaper_utils
from desktop import service

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

service_subparser = global_subparsers.add_parser("service",
                                                 help="Install as a service")
service_subparser.add_argument(
    "action",
    help="The action to perform",
    choices=["install", "uninstall", "start", "stop", "restart"],
)

args = parser.parse_args()


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


def set_wallpaper_from_uuid_args(uuid_from_args: str):
    if uuid_from_args == "account":
        access = read_from_config("access_token")
        if access is None:
            print("Please login first, using 'auth login'")
            exit(1)
        try:
            wallpaper_url = authentik_integration.get_user_background_url(access)
            if wallpaper_url is None:
                print(
                    "No wallpaper set on your account, please set a wallpaper on the website")
                exit(1)
            write_to_config("last_account_wallpaper", wallpaper_url)
        except Exception as e:
            print(f"Error when trying to fetch current wallpaper from your account: {e}")

            previous_wallpaper = read_from_config("last_account_wallpaper")
            if previous_wallpaper is None:
                print("No previous wallpaper to fall back to")
                exit(1)

            print("Falling back to previous wallpaper")
            wallpaper_url = previous_wallpaper

        uuid = heicwallpaper_utils.get_uuid_from_url(wallpaper_url)
        write_to_config("wallpaper", "account")
    else:
        uuid = heicwallpaper_utils.get_uuid_from_url(uuid_from_args)
        write_to_config("wallpaper", uuid)

    print(f"Changing wallpaper to {uuid}")
    heicwallpaper_utils.make_available_offline(uuid)
    path = heicwallpaper_utils.get_correct_photo_for_wallpaper(uuid)
    wallpaper_utils.set_wallpaper(path)


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
        write_to_config("wallpaper", None)

elif "uuid" in args:
    set_wallpaper_from_uuid_args(args.uuid)
elif "action" in args:
    service.install_service()
else:
    print(
        "No arguments provided, changing to configured wallpaper. For help, use --help")
    wallpaper = read_from_config("wallpaper")
    if wallpaper is None:
        print("No wallpaper configured")
        exit(1)

    set_wallpaper_from_uuid_args(wallpaper)
