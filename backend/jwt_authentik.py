# https://authentik.thies.dev/application/o/wallpaper-dev/jwks/

import jwt
import requests

from backend.config import AppConfig

client_url = f"{AppConfig.AUTHENTIK_API_URL}/application/o/{AppConfig.AUTHENTIK_CLIENT_ID}/"
jwks_client = jwt.PyJWKClient(f"{client_url}jwks/", cache_jwk_set=True, lifespan=360,
                              headers={"User-Agent": "Wallpaper-Backend"})


def validate_access_token(token: str):
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        print(signing_key, flush=True)
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=client_url,
            audience=f"{AppConfig.AUTHENTIK_CLIENT_ID}",
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )
        return data
    except jwt.exceptions.PyJWTError as err:
        print(f"Error: {err}", flush=True)
        return False


def get_user_id(token: str):
    data = validate_access_token(token)

    if data:
        print(data)
        return data["sub"]
    return False


def set_user_wallpaper(token: str, wallpaper_uid: str):
    user_id = get_user_id(token)
    if user_id:
        try:
            original_attributes = requests.get(
                f"{AppConfig.AUTHENTIK_API_URL}/api/v3/core/users/{user_id}/",
                headers={"Authorization": f"Bearer {AppConfig.AUTHENTIK_TOKEN}"}
            ).json()

            print("original_attributes: ", original_attributes, flush=True)

            if "attributes" not in original_attributes:
                raise Exception("No attributes found")

            original_attributes = original_attributes["attributes"]

            print("original_attributes: ", original_attributes, flush=True)
            if "settings" not in original_attributes:
                original_attributes["settings"] = {}

            original_attributes["settings"]["backgroundURL"] = f"{AppConfig.PUBLIC_URL}/{wallpaper_uid}"

            result = requests.patch(
                f"{AppConfig.AUTHENTIK_API_URL}/api/v3/core/users/{user_id}/",
                json={"attributes": original_attributes},
                headers={"Authorization": f"Bearer {AppConfig.AUTHENTIK_TOKEN}"}
            )

            print("res: ", result.json(), flush=True)

            if result.status_code != 200:
                return False, "Error setting wallpaper"
        except Exception as e:
            print("Exeception in setting:",e, flush=True)
            return False, "Error setting wallpaper"

        return True, "Wallpaper set"

    return False, "Invalid token"
