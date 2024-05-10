import requests
import time

AUTHENTIK_URL = "https://authentik.thies.dev"
AUTHENTIK_CLIENT_ID = "wallpaper-dev"
SCOPES = "openid profile email offline_access settings"


def login_request():
    form_data = {
        "client_id": AUTHENTIK_CLIENT_ID,
        "scopes": SCOPES,
    }
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
        form_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": response["device_code"],
            "client_id": AUTHENTIK_CLIENT_ID,
            "scopes": SCOPES,
        }
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
            print("Access token:", auth_response["access_token"], auth_response)
            return auth_response["access_token"], auth_response["id_token"]
        else:
            raise ValueError("No access token in response")
    else:
        raise ValueError("Link expired")


def get_user(token: str):
    request = requests.get(f"{AUTHENTIK_URL}/application/o/userinfo/", headers={
        "Authorization": f"Bearer {token}",
    })
    print(request.text)
    request.raise_for_status()
    return request.json()
