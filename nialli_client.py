import os
import requests
from dotenv import load_dotenv
from nialli_auth import auth_headers, invalidate_token_cache

# Load .env (safe even if already called elsewhere)
load_dotenv()

BASE_URL = os.environ.get("NIALLI_BASE_URL", "https://nvpapi.nialli.com").rstrip("/")


def _get_with_auto_refresh(url: str, **kwargs):
    """
    GET wrapper that:
    - uses a fresh token from auth_headers()
    - if it gets 401, invalidates the token cache and retries once
    """
    # First attempt
    resp = requests.get(url, headers=auth_headers(), **kwargs)
    if resp.status_code != 401:
        resp.raise_for_status()
        return resp

    # If 401, force a new token and retry once
    invalidate_token_cache()
    resp = requests.get(url, headers=auth_headers(), **kwargs)
    resp.raise_for_status()
    return resp


def get_subscriptions():
    url = f"{BASE_URL}/v1/Subscription/GetSubscriptionsForUser"
    resp = _get_with_auto_refresh(url)
    return resp.json()


def get_plans(subscription_id: str):
    url = f"{BASE_URL}/v1/Plan/GetPlanInfoForSubscription/{subscription_id}"
    resp = _get_with_auto_refresh(url)
    return resp.json()


def get_lanes(subscription_id: str, plan_id: str):
    url = f"{BASE_URL}/v1/Lane/GetLanesForPlan/{subscription_id}/{plan_id}"
    resp = _get_with_auto_refresh(url)
    return resp.json()


def get_activities(subscription_id: str, plan_id: str, skip: int = 0, take: int = 100):
    if take > 100:
        take = 100
    url = f"{BASE_URL}/v1/Activity/GetActivitiesForPlan/{subscription_id}/{plan_id}/{skip}/{take}"
    resp = _get_with_auto_refresh(url)
    return resp.json()


def get_activity_tags_for_plan(subscription_id: str, plan_id: str):
    url = f"{BASE_URL}/v1/ActivityTag/GetActivityTagsForPlan/{subscription_id}/{plan_id}"
    resp = _get_with_auto_refresh(url)
    return resp.json()


def get_tags_for_activity(subscription_id: str, plan_id: str, activity_id: str):
    url = f"{BASE_URL}/v1/ActivityTag/GetTagsForAnActivity/{subscription_id}/{plan_id}/{activity_id}"
    resp = _get_with_auto_refresh(url)
    return resp.json()