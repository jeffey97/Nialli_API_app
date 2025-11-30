import os
import sys
import time
from datetime import date, datetime
import pandas as pd
import json
import requests
import streamlit as st


def _parse_date_only(value):
    if not value:
        return None
    s = str(value)
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None

# --- Ensure project root is on sys.path so we can import nialli_client.py ---
# app_cached.py is in /Users/.../Nialli_API_app/ui/app_cached.py
# project root is /Users/.../Nialli_API_app
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from nialli_client import (
    get_subscriptions,
    get_plans,
    get_lanes,
    get_activities,
    get_activity_tags_for_plan,
    get_tags_for_activity,
)

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
# Cached endpoint wrappers
# -------------------------------------------------------------------

@st.cache_data(ttl=600)  # 10 minutes
def get_subscriptions_cached():
    """
    Get all subscriptions for the current user.
    Cached because subscriptions rarely change minute-to-minute.
    """
    print("👉 [API] get_subscriptions() called (cache miss)")
    return get_subscriptions()


@st.cache_data(ttl=600)  # 10 minutes
def get_plans_cached(subscription_id: str):
    """
    Get plans for a given subscription.
    Cached per subscription ID.
    """
    print(f"👉 [API] get_plans({subscription_id}) called (cache miss)")
    return get_plans(subscription_id)


@st.cache_data(ttl=300)  # 5 minutes
def get_lanes_cached(subscription_id: str, plan_id: str):
    """
    Get lanes for a given plan within a subscription.
    Cached per (subscription_id, plan_id).
    """
    print(f"👉 [API] get_lanes({subscription_id}, {plan_id}) called (cache miss)")
    return get_lanes(subscription_id,plan_id)


@st.cache_data(ttl=300)  # 5 minutes cache
def get_activities_cached(subscription_id: str, plan_id: str):
    """
    Get ALL activities for a given plan as a flat list.
    Uses the high-level nialli_client.get_activities().
    Unwraps dict payloads into a list if needed.
    """
    print(f"👉 [API] get_activities({subscription_id}, {plan_id}) called (cache miss)")
    raw = get_activities(subscription_id, plan_id, skip=0, take=100)
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return (
            raw.get("activities")
            or raw.get("items")
            or raw.get("data")
            or raw.get("value")
            or []
        )
    return []

@st.cache_data(ttl=300)  # 5 minutes
def get_activity_tags_cached(subscription_id: str, plan_id: str):
    """
    Get all activity-tag rows for a given plan.
    Each row links activityId <-> tagLaneId/tagDay/etc.
    """
    print(f"👉 [API] get_activity_tags_for_plan({subscription_id}, {plan_id}) called (cache miss)")
    return get_activity_tags_for_plan(subscription_id, plan_id)


@st.cache_data(ttl=120)
def get_activities_for_plan(subscription_id: str, plan_id: str, skip: int, take: int):
    """
    Debug version: calls Activities endpoint via nialli_client and returns raw payload.
    """
    # be safe: clamp take to 100 in case the API has a max
    if take > 100:
        take = 100

    print(f"👉 [API DEBUG] get_activities_for_plan({subscription_id}, {plan_id}, skip={skip}, take={take})")
    return get_activities(subscription_id, plan_id, skip=skip, take=take)

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
subs = get_subscriptions_cached()
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
plans = get_plans_cached(subscription_id)
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
    st.session_state.lanes = get_lanes_cached(subscription_id, plan_id)

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

st.subheader("Lane activities (from Nialli)")

if st.button("Load activities for this lane", key="lane_activities_table_btn"):
    # 1) Fetch ALL activities for the plan
    activities = get_activities_cached(subscription_id, plan_id)

    # 1b) Try to fetch tags; if API errors, don't crash
    try:
        activity_tags = get_activity_tags_cached(subscription_id, plan_id)
    except requests.HTTPError as e:
        st.error("Could not load activity tags for this plan. "
                 "The ActivityTag endpoint returned an error.")
        if st.session_state.get("debug_flag"):
            st.exception(e)
        activity_tags = []

    if not activity_tags:
        st.info(
            "No activity tags available (or tag endpoint failed), "
            "so lane-based filtering via tags is not possible right now."
        )
        st.stop()


    # Debug: inspect payloads
    if st.session_state.get("debug_flag"):
        st.write(f"🔍 Debug: total activities returned for plan: {len(activities)}")
        if activities:
            st.write("🔍 Debug: first activity object:")
            st.json(activities[0])

        st.write(f"🔍 Debug: total activity-tags returned for plan: {len(activity_tags)}")
        if activity_tags:
            st.write("🔍 Debug: first activity-tag object:")
            st.json(activity_tags[0])

    # 2) Build activityId -> activity map
    activities_by_id = {}
    for a in activities:
        if not isinstance(a, dict):
            continue
        aid = a.get("activityId") or a.get("id")
        if aid:
            activities_by_id[str(aid)] = a

    # 3) From ActivityTags, pick those for this lane (optionally filter by date later)
    lane_activity_ids = set()
    today = date.today()  # if you want to filter by "today" later

    for t in activity_tags:
        if not isinstance(t, dict):
            continue

        # lane from ActivityTag schema
        tag_lane = t.get("tagLaneId") or t.get("laneId")
        if str(tag_lane) != str(lane_id):
            continue

        # OPTIONAL: filter by today using tagDay/day
        #tag_day_raw = t.get("tagDay") or t.get("day")
        #tag_day = _parse_date_only(tag_day_raw)
        #if tag_day != today:
             #continue

        act_id = t.get("activityId")
        if act_id:
            lane_activity_ids.add(str(act_id))

    if st.session_state.get("debug_flag"):
        st.write("🔍 Debug: activityIds linked to this lane via tags:", lane_activity_ids)

    # 4) Build the final list of activities for this lane
    lane_activities = []
    for aid in lane_activity_ids:
        act = activities_by_id.get(aid)
        if act:
            lane_activities.append(act)

    if not lane_activities:
        st.info(f"No activities found for lane **{lane_name}** via tags.")
    else:
        # 5) Flatten into a friendly table
        rows = []
        for a in lane_activities:
            rows.append({
                "Activity ID": a.get("activityId") or a.get("id"),
                "Description": a.get("description") or a.get("activityName") or a.get("name"),
                # laneId may still be null on the activity itself; lane is defined by the tag
                "Lane ID (from selection)": lane_id,
            })

        df = pd.DataFrame(rows)

        st.write(f"Found **{len(df)}** activities in lane **{lane_name}** (via tags)")
        st.dataframe(df, use_container_width=True)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download lane activities as CSV",
            data=csv_bytes,
            file_name=f"lane_{lane_name.replace(' ', '_')}_activities.csv",
            mime="text/csv",
        )
else:
    st.info("Click the button above to load activities for this lane.")

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

if st.button("Load activities for this lane",key="lane_activities_debug_btn"):
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
