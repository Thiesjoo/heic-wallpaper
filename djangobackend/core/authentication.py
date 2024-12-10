import jwt

from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import User

client_url = f"{settings.AUTHENTIK_API_URL}/application/o/{settings.AUTHENTIK_CLIENT_ID}/"
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
                audience=f"{settings.AUTHENTIK_CLIENT_ID}",
                options={
                    "verify_signature": True,
                    "verify_exp": True,
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

            user.name = name
            user.email = email
            user.settings = user_settings

            if groups and "authentik Admins" in groups:
                user.is_staff = True

            user.save()

            return (user, None)
        except Exception as err:
            print(f"Error: {err}")
            raise AuthenticationFailed from err

