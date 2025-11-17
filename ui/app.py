import streamlit as st
import requests

# For now, we’ll call Nialli directly from the UI.
# Later you can swap this to call your own FastAPI backend instead.

BASE_URL = "https://nvpapi.test.nialli.com"
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlRCWWEwSTBSeEtMU2Nxb1BnUDBHVSJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOltdLCJodHRwczovL2xvY2FsaG9zdDo0NDQzNi9lbWFpbCI6Im1hcmt1cy5hbWFsYW5hdGhhbkBhZGlkZXZlbG9wbWVudHMuY29tIiwiYXV0aGVudGljYXRlZGVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLmVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLnVzZXJpZCI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImlzcyI6Imh0dHBzOi8vbmlhbGxpLXRlc3QudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImF1ZCI6Imh0dHBzOi8vbnZwYXBpLnRlc3QubmlhbGxpLmNvbS8iLCJpYXQiOjE3NjMzOTY5MDMsImV4cCI6MTc2MzQ4MzMwMywiZ3R5IjoicGFzc3dvcmQiLCJhenAiOiJlY2JMbWFxa0RpUkVjOG5xaEFPbjNZMnJyeTFadUxLUyIsInBlcm1pc3Npb25zIjpbInN1YnNjcmlwdGlvbjpnZXQiXX0.Key8TzdXS0_p6Wj91uwa0HoUi62pvgLRQKisSccFBN0-wvINf0vhdHPctwN-Qu6xdN3Ygt-87jbDh4MWeCHiQa0dTTtYgsdY5Um95mAcDKin_ZgZT29qP1RxCmmzH5PnE8ggf_BmFO0rKm8xiqJs74Hp-NafZPMrfRKv-FhB8nYcveD8Q4blHTgO_p9ct--vIkyEViv3ED6I-92RA8mJSVJgl3Hpsj7FeJtgylvMrDdrouRG3dWMDAiWbA1dmxuqTASdBD_kptp-IZvF7YfyzSuNirwNOEwMVwa2ZtnROxvtGHjfrEK1sImnLfqJa6pwkMNFRc1zYNX5yVBYXkjZFw"
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

@st.cache_data(ttl=60)
def get_lanes_cached(subscription_id: str, plan_id: str):
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

sub_options = {}
for s in subs:
    # Try multiple possible keys for name & id
    sub_name = (
        s.get("subscriptionName")
        or s.get("name")
        or s.get("displayName")
        or "Subscription"
    )
    sub_id = s.get("subscriptionId") or s.get("id")

    label = f"{sub_name} ({sub_id})"
    sub_options[label] = s

selected_sub_label = st.selectbox("Subscription", list(sub_options.keys()))
selected_sub = sub_options[selected_sub_label]
subscription_id = selected_sub.get("subscriptionId") or selected_sub.get("id")

# After subs = get_subscriptions()
st.sidebar.checkbox("Show debug data", key="debug_flag")

if st.session_state.debug_flag:
    st.subheader("🔍 Debug: Raw subscriptions")
    st.json(subs)

# 2. Plans
st.subheader("2. Select Plan")
plans = get_plans(subscription_id)
if not plans:
    st.error("No plans for this subscription.")
    st.stop()

plan_options = {}
for p in plans:
    plan_name = (
        p.get("planName")
        or p.get("name")
        or p.get("plan_name")
        or "Plan"
    )
    plan_id_value = p.get("planId") or p.get("id")

    label = f"{plan_name} ({plan_id_value})"
    plan_options[label] = p

selected_plan_label = st.selectbox("Plan", list(plan_options.keys()))
selected_plan = plan_options[selected_plan_label]
plan_id = selected_plan.get("planId") or selected_plan.get("id")

if st.session_state.debug_flag:
    st.subheader("🔍 Debug: Raw plans")
    st.json(plans)

# 3. Lanes
st.subheader("3. Select Lane")

lanes = []
if "lanes" not in st.session_state:
    st.session_state.lanes = []

if st.button("Load lanes for this plan"):
    try:
        st.session_state.lanes = get_lanes_cached(subscription_id, plan_id)
    except requests.HTTPError as e:
        st.error(f"Failed to load lanes: {e}")
        st.stop()

lanes = st.session_state.lanes

if not lanes:
    st.info("Click the button above to load lanes.")
    st.stop()

lane_options = {
    f'{l.get("laneName") or l.get("name") or "Lane"} ({l.get("laneId") or l.get("id")})': l
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