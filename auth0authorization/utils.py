from django.contrib.auth import authenticate
import json
import jwt
import requests
from core.models import UserInfo


from server.settings.prod import AUTH0_AUDIENCE, AUTH0_DOMAIN

if not AUTH0_AUDIENCE or not AUTH0_DOMAIN:
    from server.settings.dev import AUTH0_AUDIENCE, AUTH0_DOMAIN

    if not AUTH0_AUDIENCE or not AUTH0_DOMAIN:
        raise Exception("Unable to locate AUTH0 -- Config")


def jwt_get_username_from_payload_handler(payload):
    username = payload.get("sub").replace("|", ".")

    # Creates a user if the user does not exist
    user = authenticate(remote_user=username)

    user_info = UserInfo.objects.filter(user=user)
    if not user_info.exists():
        user_info.create(user=user)

    return username


def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get("https://{}/.well-known/jwks.json".format(AUTH0_DOMAIN)).json()
    public_key = None
    for jwk in jwks["keys"]:
        if jwk["kid"] == header["kid"]:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception("Public key not found.")

    issuer = "https://{}/".format(AUTH0_DOMAIN)

    decoded = jwt.decode(
        token,
        public_key,
        audience=AUTH0_AUDIENCE,
        issuer=issuer,
        algorithms=["RS256"],
    )

    return decoded
