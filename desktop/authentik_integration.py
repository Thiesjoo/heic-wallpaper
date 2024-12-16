import base64
import json
import time

import requests

from config_utils import write_to_config, read_from_config

AUTHENTIK_URL = "https://authentik.thies.dev"
AUTHENTIK_CLIENT_ID = "wallpaper"
SCOPES = "openid profile email offline_access settings"


def login_request():
    form_data = {"client_id": AUTHENTIK_CLIENT_ID, "scope": SCOPES, }
    request = requests.post(f"{AUTHENTIK_URL}/application/o/device/", data=form_data,
                            headers={
                                "Content-Type": "application/x-www-form-urlencoded"})
    request.raise_for_status()
    response = request.json()

    print("Please visit the following URL to authenticate:")
    print(response["verification_uri_complete"])
    print(f"Link expires in {response['expires_in'] // 60} minute")

    start = time.time()
    while time.time() - start < response["expires_in"]:
        form_data = {"grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": response["device_code"], "client_id": AUTHENTIK_CLIENT_ID,
            "scopes": SCOPES, }
        request = requests.post(f"{AUTHENTIK_URL}/application/o/token/", data=form_data,
                                headers={
                                    "Content-Type": "application/x-www-form-urlencoded"})
        auth_response = request.json()

        if request.status_code == 400:
            print("Waiting for user to authenticate...")
            time.sleep(response["interval"])
            continue

        request.raise_for_status()
        if "access_token" in auth_response:
            return auth_response["access_token"], auth_response["id_token"], \
            auth_response.get("refresh_token")
        else:
            raise ValueError("No access token in response")
    else:
        raise ValueError("Link expired")


def save_tokens(tokens):
    (access, id, refresh) = tokens
    write_to_config("access_token", access)
    write_to_config("id_token", id)
    write_to_config("refresh_token", refresh)


def _obtain_new_access_token():
    cached_refresh: str = read_from_config("refresh_token")
    if not cached_refresh:
        raise ValueError("No refresh token found in config")

    form_data = {"grant_type": "refresh_token", "client_id": AUTHENTIK_CLIENT_ID,
        "scopes": SCOPES, "refresh_token": cached_refresh}
    request = requests.post(f"{AUTHENTIK_URL}/application/o/token/", data=form_data,
                            headers={
                                "Content-Type": "application/x-www-form-urlencoded"})
    request.raise_for_status()
    auth_response = request.json()

    if "access_token" in auth_response:
        save_tokens((auth_response["access_token"], auth_response["id_token"], auth_response.get("refresh_token")))
        return auth_response["access_token"]
    raise ValueError("Authentik did not provide us with a new refresh token, please reauthenticate")

def get_current_token():
    try:
        cached_access: str = read_from_config("access_token")
        if not cached_access:
            return None

        first_dot = cached_access.index(".")
        second_dot = cached_access.index(".", first_dot + 1)

        encoded_base64 = cached_access[first_dot + 1:second_dot]
        decoded = base64.b64decode(encoded_base64 + '==')

        exp = json.loads(decoded).get("exp", 0)
        if time.time() > exp:
            print("Your token expired, we are now going to try and request a new one")
            return _obtain_new_access_token()

        return cached_access
    except Exception as err:
        print("Something went wrong with getting your current token. please try to log out and in again.", err)

def logout():
    # TODO: To be nice, we should revoke the access/refresh tokens with authentik
    save_tokens((None, None, None))

def get_user(token: str):
    request = requests.get(f"{AUTHENTIK_URL}/application/o/userinfo/",
                           headers={"Authorization": f"Bearer {token}", })
    request.raise_for_status()
    return request.json()


def get_user_background_url(token: str):
    user = get_user(token)
    assert "settings" in user
    if "backgroundURL" not in user["settings"]:
        return None
    return user["settings"]["backgroundURL"]
