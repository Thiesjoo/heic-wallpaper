import argparse

import authentik_integration
import wallpaper_utils
import heicwallpaper_utils
import service

from config_utils import read_from_config, write_to_config

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


def set_wallpaper_from_uuid_args(uuid_from_args: str):
    if uuid_from_args == "account":
        access = authentik_integration.get_current_token()

        if access is None:
            print("Please login first, using 'auth login'")
            exit(1)
        try:
            wallpaper_url = authentik_integration.get_user_background_url(access)
            if wallpaper_url is None:
                print(
                    "No wallpaper set on your account, please set a wallpaper on the website")
                exit(1)
        except Exception as e:
            print(f"Error when trying to fetch current wallpaper from your account: {e}")

            previous_wallpaper = read_from_config("last_account_wallpaper")
            if previous_wallpaper is None:
                print("No previous wallpaper to fall back to")
                exit(1)

            print("Falling back to previous wallpaper")
            wallpaper_url = previous_wallpaper

        uuid = wallpaper_url
        write_to_config("wallpaper", "account")
    else:
        uuid = uuid_from_args
        write_to_config("wallpaper", uuid)

    print(f"Changing wallpaper to {uuid}")
    wallpaper = heicwallpaper_utils.Wallpaper.from_uuid_or_url(uuid)
    wallpaper.make_available_offline()

    if uuid_from_args == "account":
        write_to_config("last_account_wallpaper", wallpaper.uid)

    path = wallpaper.get_correct_wallpaper_for_time()
    print("Setting wallpaper to path: ",path)
    wallpaper_utils.set_wallpaper(path)


if "auth" in args:
    if args.auth == "login":
        print("Trying to log in")
        if read_from_config("refresh_token") is None:
            tokens = authentik_integration.login_request()
            authentik_integration.save_tokens(tokens)
        else:
            print("Already logged in")

        active_token = authentik_integration.get_current_token()
        user = authentik_integration.get_user(active_token)
        print(f"Welcome {user['name']}")
        print("You can now use the wallpaper command to change the wallpaper")
    elif args.auth == "logout":
        print("Logging out")
        authentik_integration.logout()
        write_to_config("wallpaper", None)

elif "uuid" in args:
    set_wallpaper_from_uuid_args(args.uuid)
elif "action" in args:
    service.install_service()
else:
    print(
        "No arguments provided, changing to configured wallpaper. For help, use --help")
    wallpaper_uuid = read_from_config("wallpaper")
    if wallpaper_uuid is None:
        print("No wallpaper configured")
        exit(1)

    set_wallpaper_from_uuid_args(wallpaper_uuid)
