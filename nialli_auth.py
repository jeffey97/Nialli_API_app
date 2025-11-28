import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

AUTH_DOMAIN = os.environ.get("NIALLI_AUTH_DOMAIN")
CLIENT_ID = os.environ.get("NIALLI_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NIALLI_CLIENT_SECRET")
AUDIENCE = os.environ.get("NIALLI_AUDIENCE")
USERNAME = os.environ.get("NIALLI_USERNAME")
PASSWORD = os.environ.get("NIALLI_PASSWORD")

if not all([AUTH_DOMAIN, CLIENT_ID, CLIENT_SECRET, AUDIENCE, USERNAME, PASSWORD]):
    raise RuntimeError("Missing one or more NIALLI_* environment variables. Check your .env file.")

TOKEN_URL = AUTH_DOMAIN.rstrip("/") + "/oauth/token"

# In-memory token cache
_ACCESS_TOKEN = None
_ACCESS_TOKEN_EXPIRES_AT = 0  # unix timestamp
TOKEN_SAFETY_MARGIN = 60      # seconds before expiry to refresh


def _request_new_token() -> str:
    """
    Call Auth0 /oauth/token with the Resource Owner Password flow
    to get a new access token.
    """
    global _ACCESS_TOKEN, _ACCESS_TOKEN_EXPIRES_AT

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": AUDIENCE,
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
    }

    headers = {"Content-Type": "application/json"}
    resp = requests.post(TOKEN_URL, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    access_token = data["access_token"]
    expires_in = data.get("expires_in", 24 * 60 * 60)  # default 24h if not provided

    now = time.time()
    _ACCESS_TOKEN = access_token
    _ACCESS_TOKEN_EXPIRES_AT = now + expires_in

    return _ACCESS_TOKEN


def get_access_token() -> str:
    """
    Return a valid access token.
    Refreshes it automatically if expired or close to expiry.
    """
    global _ACCESS_TOKEN, _ACCESS_TOKEN_EXPIRES_AT

    now = time.time()
    if _ACCESS_TOKEN and now < _ACCESS_TOKEN_EXPIRES_AT - TOKEN_SAFETY_MARGIN:
        return _ACCESS_TOKEN

    # Missing or expired token → request new one
    return _request_new_token()


def auth_headers() -> dict:
    """
    Returns headers with a fresh Authorization bearer token.
    Use this in ALL Nialli API calls.
    """
    token = get_access_token()
    return {"Authorization": f"Bearer {token}"}


def invalidate_token_cache():
    """
    Force the next call to fetch a new token.
    Useful when you get a 401 from the API.
    """
    global _ACCESS_TOKEN, _ACCESS_TOKEN_EXPIRES_AT
    _ACCESS_TOKEN = None
    _ACCESS_TOKEN_EXPIRES_AT = 0