import os
import time
from datetime import date, datetime
import json


import requests
import streamlit as st
from nialli_client import (
    get_subscriptions,
    get_plans,
    get_lanes,
    get_activities,
    get_activity_tags_for_plan,
)



# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------

st.set_page_config(page_title="Nialli MVP Viewer", layout="wide")

# BASE_URL and ACCESS_TOKEN are stored in .streamlit/secrets.toml
# Example:
# NIALLI_API_BASE_URL = "https://nvpapi.nialli.com"
# NIALLI_ACCESS_TOKEN = "your_real_token_here"

BASE_URL = st.secrets["NIALLI_API_BASE_URL"]
ACCESS_TOKEN = st.secrets["NIALLI_ACCESS_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# -------------------------------------------------------------------
# API diagnostics (stored in session_state)
# -------------------------------------------------------------------

if "api_stats" not in st.session_state:
    st.session_state.api_stats = {
        "total_calls": 0,
        "total_429s": 0,
        "last_path": None,
        "last_status": None,
        "last_error": None,
    }

# -------------------------------------------------------------------
# Low-level HTTP helper with rate-limit handling
# -------------------------------------------------------------------


def nialli_get(path: str, max_retries: int = 5):
    """
    Wrapper around requests.get for Nialli API.

    - Prefixes BASE_URL
    - Adds Authorization headers
    - Handles 429 (Too Many Requests) with backoff
    - Raises for non-429 HTTP errors
    - Updates simple diagnostics in st.session_state.api_stats
    """
    url = f"{BASE_URL}{path}"
    stats = st.session_state.api_stats
    stats["last_path"] = path

    for attempt in range(max_retries):
        stats["total_calls"] += 1
        try:
            resp = requests.get(url, headers=HEADERS)
            stats["last_status"] = resp.status_code
        except Exception as ex:
            stats["last_error"] = str(ex)
            raise

        # Handle rate limiting explicitly
        if resp.status_code == 429:
            stats["total_429s"] += 1

            retry_after = resp.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    wait = int(retry_after)
                except ValueError:
                    wait = 2 ** attempt
            else:
                # Exponential backoff: 1, 2, 4, 8, 16...
                wait = 2 ** attempt

            st.warning(
                f"Rate limited by Nialli (429). "
                f"Retrying in {wait} seconds... (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(wait)
            continue

        # For any non-429 error, raise as usual
        try:
            resp.raise_for_status()
        except requests.HTTPError as http_err:
            stats["last_error"] = str(http_err)
            raise

        stats["last_error"] = None
        return resp.json()

    # If we get here, we never got a non-429 success response
    err_msg = "Too many 429 responses from Nialli; giving up after retries."
    stats["last_error"] = err_msg
    raise requests.HTTPError(err_msg)


# -------------------------------------------------------------------
# Cached endpoint wrappers
# -------------------------------------------------------------------


@st.cache_data(ttl=600)  # 10 minutes
def get_subscriptions():
    """
    Get all subscriptions for the current user.
    Cached because subscriptions rarely change minute-to-minute.
    """
    print("👉 [API] get_subscriptions() called (cache miss)")
    return nialli_get("/v1/Subscription/GetSubscriptionsForUser")


@st.cache_data(ttl=600)  # 10 minutes
def get_plans(subscription_id: str):
    """
    Get plans for a given subscription.
    Cached per subscription ID.
    """
    print(f"👉 [API] get_plans({subscription_id}) called (cache miss)")
    return nialli_get(f"/v1/Plan/GetPlanInfoForSubscription/{subscription_id}")


@st.cache_data(ttl=300)  # 5 minutes
def get_lanes(subscription_id: str, plan_id: str):
    """
    Get lanes for a given plan within a subscription.
    Cached per (subscription_id, plan_id).
    """
    print(f"👉 [API] get_lanes({subscription_id}, {plan_id}) called (cache miss)")
    return nialli_get(f"/v1/Lane/GetLanesForPlan/{subscription_id}/{plan_id}")



@st.cache_data(ttl=120)
def get_activities_for_plan(subscription_id: str, plan_id: str, skip: int, take: int):
    """
    Debug version: calls Activities endpoint directly and shows 400 response body.
    Once things work, we can wire this back through nialli_get().
    """
    # be safe: clamp take to 100 in case the API has a max
    if take > 100:
        take = 100

    path = f"/v1/Activity/GetActivitiesForPlan/{subscription_id}/{plan_id}/{skip}/{take}"
    url = f"{BASE_URL}{path}"
    print("👉 [API] get_activities_for_plan calling:", url)

    resp = requests.get(url, headers=HEADERS)

    # If it's a 400, show the explanation from Nialli
    if resp.status_code == 400:
        try:
            body = resp.json()
        except Exception:
            body = resp.text

        st.error("Activities endpoint returned 400 Bad Request.")
        st.code(str(body), language="json")
        # Still raise so the UI "Failed to load activities" logic works
        resp.raise_for_status()

    resp.raise_for_status()
    return resp.json()

# -------------------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------------------

st.title("🧱 Nialli Plan Explorer (MVP)")

# Sidebar: options + diagnostics
st.sidebar.header("Options")
st.sidebar.checkbox("Show debug data", key="debug_flag")

st.sidebar.header("API Diagnostics")
api_stats = st.session_state.api_stats
st.sidebar.metric("Total API calls", api_stats["total_calls"])
st.sidebar.metric("Total 429s", api_stats["total_429s"])
st.sidebar.write(f"Last path: `{api_stats['last_path']}`")
st.sidebar.write(f"Last status: {api_stats['last_status']}")
if api_stats["last_error"]:
    st.sidebar.error(f"Last error: {api_stats['last_error']}")

st.title("Nialli MVP – Production Data")

# 1. Subscriptions
subs = get_subscriptions()
if not subs:
    st.error("No subscriptions found.")
    st.stop()

sub_options = {}
for s in subs:
    sub_name = s.get("subscriptionName") or s.get("name") or "Subscription"
    sub_id = s.get("subscriptionId") or s.get("id")
    sub_options[f"{sub_name} ({sub_id})"] = s

selected_sub_label = st.selectbox("Subscription", list(sub_options.keys()))
selected_sub = sub_options[selected_sub_label]
subscription_id = selected_sub.get("subscriptionId") or selected_sub.get("id")

# 2. Plans
plans = get_plans(subscription_id)
if not plans:
    st.error("No plans for this subscription.")
    st.stop()

plan_options = {}
for p in plans:
    plan_name = p.get("planName") or p.get("name") or "Plan"
    plan_id_val = p.get("planId") or p.get("id")
    plan_options[f"{plan_name} ({plan_id_val})"] = p

selected_plan_label = st.selectbox("Plan", list(plan_options.keys()))
selected_plan = plan_options[selected_plan_label]
plan_id = selected_plan.get("planId") or selected_plan.get("id")

# 3. Lanes (with button, like you had)
st.subheader("Select lane")
if "lanes" not in st.session_state:
    st.session_state.lanes = []

if st.button("Load lanes for this plan"):
    st.session_state.lanes = get_lanes(subscription_id, plan_id)

lanes = st.session_state.lanes

if not lanes:
    st.info("Click the button to load lanes.")
    st.stop()

lane_options = {}
for l in lanes:
    lane_name = l.get("laneName") or l.get("name") or "Lane"
    lane_id_val = l.get("laneId") or l.get("id")
    lane_options[f"{lane_name} ({lane_id_val})"] = l

selected_lane_label = st.selectbox("Lane", list(lane_options.keys()))
selected_lane = lane_options[selected_lane_label]
lane_id = selected_lane.get("laneId") or selected_lane.get("id")
lane_name = selected_lane.get("laneName") or selected_lane.get("name") or "Lane"

# --------------------------------------------------
# 4. Activities (real, from plan endpoint, filtered by lane)
# --------------------------------------------------

st.subheader("4. Activities in this Lane")

# Simple pagination controls for plan-level activities
col_skip, col_take = st.columns(2)
with col_skip:
    skip = st.number_input("Skip (offset)", min_value=0, step=50, value=0)
with col_take:
    take = st.number_input(
        "Take (page size)", min_value=1, max_value=500, step=50, value=200
    )

if st.button("Load activities for this lane"):
    try:
        # Fetch activities for the whole plan (paginated)
        raw = get_activities_for_plan(subscription_id, plan_id, int(skip), int(take))
    except requests.HTTPError as e:
        st.error(f"Failed to load activities: {e}")
        st.stop()

    # ----- Interpret the payload shape -----
    # Nialli might return either:
    #  - a list of activities
    #  - an object like { "activities": [ ... ] } or { "items": [ ... ] }
    if isinstance(raw, list):
        all_activities = raw
    elif isinstance(raw, dict):
        all_activities = (
            raw.get("activities")
            or raw.get("items")
            or raw.get("data")
            or raw.get("value")
            or []
        )
    else:
        all_activities = []

    if st.session_state.debug_flag:
        st.subheader("🔍 Debug: Raw activities payload (truncated)")
        # Show the raw structure to understand what's coming back
        st.json(raw if isinstance(raw, (dict, list)) else {"raw": str(raw)})
        st.write(f"Interpreted as {len(all_activities)} activities")

    if not all_activities:
        st.info(
            f"No activities returned for this plan (skip={skip}, take={take}). "
            "Check debug view to inspect the raw payload."
        )
        st.stop()

    # ----- Filter to lane -----
    lane_activities = []
    for act in all_activities:
        if not isinstance(act, dict):
            continue

        # Try several possible keys for lane ID
        act_lane_id = (
            act.get("laneId")
            or act.get("lane_id")
            or act.get("LaneId")
            or act.get("laneGuid")
            or act.get("swimlaneId")
            or act.get("swimLaneId")
        )

        if act_lane_id == lane_id:
            lane_activities.append(act)

    total = len(all_activities)
    matched = len(lane_activities)

    if matched == 0:
        st.warning(
            f"Loaded {total} activities for the plan, "
            f"but none matched laneId = `{lane_id}`.\n\n"
            "Showing ALL plan activities below for debugging."
        )
        activities_to_show = all_activities
    else:
        st.success(
            f"Loaded {total} activities for the plan; "
            f"{matched} matched lane **{lane_name}**."
        )
        activities_to_show = lane_activities

    # ----- Display activities -----
    for act in activities_to_show:
        if not isinstance(act, dict):
            continue

        desc = (
            act.get("description")
            or act.get("activityName")
            or act.get("name")
            or "Activity"
        )
        act_id = act.get("activityId") or act.get("id")
        start = (
            act.get("startDate")
            or act.get("plannedStartDate")
            or act.get("start")
            or ""
        )
        end = (
            act.get("endDate")
            or act.get("plannedEndDate")
            or act.get("end")
            or ""
        )
        tags = (
            act.get("tags")
            or act.get("Tags")
            or act.get("labels")
            or act.get("Labels")
            or []
        )

        with st.expander(f"{desc} ({act_id})"):
            st.markdown(f"**Lane ID (from activity):** `{act.get('laneId', '')}`")
            st.markdown(f"**Start:** {start}  \n**End:** {end}")
            if tags:
                if isinstance(tags, list):
                    tags_str = ", ".join(str(t) for t in tags)
                else:
                    tags_str = str(tags)
                st.markdown("**Tags:** " + tags_str)

            if st.session_state.debug_flag:
                st.markdown("**Raw activity JSON:**")
                st.json(act)
else:
    st.info("Click the button above to load activities for the selected lane.")

