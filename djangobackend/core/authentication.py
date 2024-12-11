import logging

import jwt
import requests

from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import User

client_url = f"{settings.CONFIG.AUTHENTIK_API_URL}/application/o/{settings.CONFIG.AUTHENTIK_CLIENT_ID}/"
jwks_client = jwt.PyJWKClient(f"{client_url}jwks/", cache_jwk_set=True, lifespan=360,
                              headers={"User-Agent": "Wallpaper-Backend"})

class AuthViaAuthentik(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        try:
            if not auth_header:
                return None
            token = auth_header.split(" ")[1]

            signing_key = jwks_client.get_signing_key_from_jwt(token)
            data = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=client_url,
                audience=f"{settings.CONFIG.AUTHENTIK_CLIENT_ID}",
                options={
                    "verify_signature": True,
                    # Allow expired tokens in debug mode, so we can test with old tokens
                    "verify_exp": not settings.DEBUG,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )

            name = data.get("name")
            email = data.get("email")
            user_settings = data.get("settings")
            groups = data.get("groups")
            uid = data.get("sub")

            (user, created) = User.objects.get_or_create(uid=uid)

            [first_name, last_name] = name.split(" ", 1)
            user.first_name = first_name
            user.last_name = last_name

            user.email = email
            user.settings = user_settings

            if groups and "authentik Admins" in groups:
                user.is_staff = True

            user.save()

            return (user, None)
        except Exception as err:
            logging.error(f"Error authenticating: {err}")
            raise AuthenticationFailed from err


def set_user_wallpaper(sub: str, wallpaper_url: str):
    logging.debug(f"Setting wallpaper for {sub} to {wallpaper_url}")
    try:
        original_attributes = requests.get(
            f"{settings.CONFIG.AUTHENTIK_API_URL}/api/v3/core/users/{sub}/",
            headers={"Authorization": f"Bearer {settings.CONFIG.AUTHENTIK_TOKEN}"}
        ).json()

        if "attributes" not in original_attributes:
            raise Exception("No attributes found")
        original_attributes = original_attributes["attributes"]
        if "settings" not in original_attributes:
            original_attributes["settings"] = {}

        logging.debug(f"Original attributes: {original_attributes}")

        original_attributes["settings"]["backgroundURL"] = wallpaper_url

        result = requests.patch(
            f"{settings.CONFIG.AUTHENTIK_API_URL}/api/v3/core/users/{sub}/",
            json={"attributes": original_attributes},
            headers={"Authorization": f"Bearer {settings.CONFIG.AUTHENTIK_TOKEN}"}
        )

        if result.status_code != 200:
            return False, "Error setting wallpaper"
    except Exception as e:
        logging.error(f"Error setting wallpaper: {e}")
        return False, "Error setting wallpaper"

    return True, "Wallpaper set"
