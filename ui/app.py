import streamlit as st
import requests

# For now, we’ll call Nialli directly from the UI.
# Later you can swap this to call your own FastAPI backend instead.

BASE_URL = "https://nvpapi.test.nialli.com"
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlRCWWEwSTBSeEtMU2Nxb1BnUDBHVSJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOltdLCJodHRwczovL2xvY2FsaG9zdDo0NDQzNi9lbWFpbCI6Im1hcmt1cy5hbWFsYW5hdGhhbkBhZGlkZXZlbG9wbWVudHMuY29tIiwiYXV0aGVudGljYXRlZGVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLmVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLnVzZXJpZCI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImlzcyI6Imh0dHBzOi8vbmlhbGxpLXRlc3QudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImF1ZCI6Imh0dHBzOi8vbnZwYXBpLnRlc3QubmlhbGxpLmNvbS8iLCJpYXQiOjE3NjMzMTAwNzMsImV4cCI6MTc2MzM5NjQ3MywiZ3R5IjoicGFzc3dvcmQiLCJhenAiOiJlY2JMbWFxa0RpUkVjOG5xaEFPbjNZMnJyeTFadUxLUyIsInBlcm1pc3Npb25zIjpbInN1YnNjcmlwdGlvbjpnZXQiXX0.K6PiBqrgsUMAI9RNGY_onbc2utPHcr9R1EuebkiCwl08PggjTY87nPBslzxBX6m6ekXR60beggOE3GRTNlRik-euV-W-nml3WLAwthCpdPttCBeJfIZfZYUjI7VKRi34lyvivw1v13lWSFrypeOpcYetsLGxCKZvWbM_T8CSvnysjVUgQ-4apvWT8_pGBnmCDMUYC7-nZR7y-NDFxvEAj2V2WwbMrGqgaBg_3Cl2mrrox4ihaIzxpNvDJV72G5guFb8X1zWmTHNCCBu5T6XxP9dfzr3zF6BeEy1XusAmsJulIzSt6dXqE-Tej7aGfTZeBHMbShDuDj1xXfbLVJk22g"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# --- Real calls: Subscriptions, Plans, Lanes ---

def get_subscriptions():
    url = f"{BASE_URL}/v1/Subscription/GetSubscriptionsForUser"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def get_plans(subscription_id: str):
    url = f"{BASE_URL}/v1/Plan/GetPlanInfoForSubscription/{subscription_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def get_lanes(subscription_id: str, plan_id: str):
    url = f"{BASE_URL}/v1/Lane/GetLanesForPlan/{subscription_id}/{plan_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

# --- TEMP: Mock activities & tags while Activities endpoint is broken ---

def mock_activities_for_lane(plan_id: str, lane_id: str):
    # You can tweak this to resemble Nialli’s real Activity structure
    return [
        {
            "activityId": "act-1",
            "description": "Sample activity 1",
            "laneId": lane_id,
            "startDate": "2024-11-20",
            "endDate": "2024-11-21",
            "tags": ["SAMPLE", "CRITICAL"]
        },
        {
            "activityId": "act-2",
            "description": "Sample activity 2",
            "laneId": lane_id,
            "startDate": "2024-11-22",
            "endDate": "2024-11-23",
            "tags": ["SAMPLE"]
        }
    ]

# --- Streamlit UI ---

st.set_page_config(page_title="Nialli MVP Viewer", layout="wide")

st.title("🧱 Nialli Plan Explorer (MVP)")

# 1. Subscriptions
st.subheader("1. Select Subscription")
subs = get_subscriptions()
if not subs:
    st.error("No subscriptions found.")
    st.stop()

sub_options = {
    f'{s.get("subscriptionName", "Unnamed")} ({s.get("subscriptionId")})': s
    for s in subs
}

selected_sub_label = st.selectbox("Subscription", list(sub_options.keys()))
selected_sub = sub_options[selected_sub_label]
subscription_id = selected_sub.get("subscriptionId") or selected_sub.get("id")

# 2. Plans
st.subheader("2. Select Plan")
plans = get_plans(subscription_id)
if not plans:
    st.error("No plans for this subscription.")
    st.stop()

plan_options = {
    f'{p.get("planName", "Unnamed Plan")} ({p.get("planId")})': p
    for p in plans
}

selected_plan_label = st.selectbox("Plan", list(plan_options.keys()))
selected_plan = plan_options[selected_plan_label]
plan_id = selected_plan.get("planId") or selected_plan.get("id")

# 3. Lanes
st.subheader("3. Select Lane")
lanes = get_lanes(subscription_id, plan_id)
if not lanes:
    st.warning("No lanes found in this plan.")
    st.stop()

lane_options = {
    f'{l.get("laneName", "Unnamed Lane")} ({l.get("laneId")})': l
    for l in lanes
}

selected_lane_label = st.selectbox("Lane", list(lane_options.keys()))
selected_lane = lane_options[selected_lane_label]
lane_id = selected_lane.get("laneId") or selected_lane.get("id")
lane_name = selected_lane.get("laneName") or selected_lane.get("name", "Unnamed Lane")

# 4. Activities (mocked for now)
st.subheader("4. Activities in this Lane (mocked until API is fixed)")

if st.button("Load activities for this lane"):
    activities = mock_activities_for_lane(plan_id, lane_id)

    st.write(f"Showing {len(activities)} activities for lane **{lane_name}**")
    # Display in a nice table
    for act in activities:
        with st.expander(f'{act["description"]} ({act["activityId"]})'):
            st.markdown(f"**Start:** {act['startDate']}  \n**End:** {act['endDate']}")
            st.markdown("**Tags:** " + ", ".join(act["tags"]))
else:
    st.info("Click the button above to load mock activities.")