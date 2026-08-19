import logging
import os

import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import User

# Support a custom JWKS URL if configured, otherwise fallback to standard issuer endpoint
jwks_url = settings.CONFIG.OIDC_JWKS_URL
if not jwks_url:
    issuer = settings.CONFIG.OIDC_ISSUER
    if not issuer.endswith("/"):
        issuer += "/"
    jwks_url = f"{issuer}.well-known/jwks.json"

jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=360,
                              headers={"User-Agent": "Wallpaper-Backend"})

class OIDCAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        try:
            token = auth_header.split(" ")[1]
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            data = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=settings.CONFIG.OIDC_ISSUER,
                options={
                    "verify_signature": True,
                    # Allow expired tokens in debug mode, so we can test with old tokens
                    "verify_exp": not settings.DEBUG,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": False,
                    "verify_iss": True,
                },
            )

            name = data.get("name")
            email = data.get("email")
            avatar_url = data.get("picture") or data.get("avatar") or data.get("avatar_url")
            user_settings = data.get("settings")
            groups = data.get("groups")
            uid = data.get("sub")

            (user, created) = User.objects.get_or_create(uid=uid)

            if name:
                parts = name.split(" ", 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ""

            if email:
                user.email = email

            if avatar_url:
                user.avatar_url = avatar_url

            # Only initialize settings from OIDC if the local user settings are empty
            if user_settings and isinstance(user_settings, dict):

                if not isinstance(user.settings, dict):
                    user.settings = {}
                for key, val in user_settings.items():
                    if key not in user.settings:
                        user.settings[key] = val

            # Check for admin groups
            if groups and any(g in ["Admins", "admins"] for g in groups):
                user.is_staff = True

            user.save()

            return (user, None)
        except Exception as err:
            logging.error(f"Error authenticating: {err}")
            raise AuthenticationFailed from err


def set_user_wallpaper(sub: str, wallpaper_url: str):
    logging.debug(f"Setting wallpaper for {sub} to {wallpaper_url}")
    try:
        user = User.objects.get(uid=sub)
        if not isinstance(user.settings, dict):
            user.settings = {}
        user.settings["backgroundURL"] = wallpaper_url
        user.save()
        return True, "Wallpaper set"
    except User.DoesNotExist:
        return False, "User not found"
    except Exception as e:
        logging.error(f"Error setting wallpaper: {e}")
        return False, f"Error setting wallpaper: {e}"
