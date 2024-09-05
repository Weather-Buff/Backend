import base64
import os
import time

import jwt
import requests


def get_github_key() -> str:
    b64 = os.getenv("GH_PRIV_KEY")

    decoded_key = base64.b64decode(b64).decode()

    print(decoded_key)

    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 600,
        'iss': os.getenv("GH_APP_CLIENT_ID")
    }

    return jwt.encode(payload, decoded_key, algorithm='RS256')

def get_installation_access_token(jwt_token: str) -> str:
    installation_id = os.getenv("GH_INSTALLATION_ID")
    response = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers= {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    )

    response.raise_for_status()
    return response.json()["token"]
