import requests

BASE_URL = "https://nvpapi.test.nialli.com"  # test environment
ACCESS_TOKEN= "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlRCWWEwSTBSeEtMU2Nxb1BnUDBHVSJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOltdLCJodHRwczovL2xvY2FsaG9zdDo0NDQzNi9lbWFpbCI6Im1hcmt1cy5hbWFsYW5hdGhhbkBhZGlkZXZlbG9wbWVudHMuY29tIiwiYXV0aGVudGljYXRlZGVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLmVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLnVzZXJpZCI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImlzcyI6Imh0dHBzOi8vbmlhbGxpLXRlc3QudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImF1ZCI6Imh0dHBzOi8vbnZwYXBpLnRlc3QubmlhbGxpLmNvbS8iLCJpYXQiOjE3NjQwMTg2MjIsImV4cCI6MTc2NDEwNTAyMiwiZ3R5IjoicGFzc3dvcmQiLCJhenAiOiJlY2JMbWFxa0RpUkVjOG5xaEFPbjNZMnJyeTFadUxLUyIsInBlcm1pc3Npb25zIjpbInN1YnNjcmlwdGlvbjpnZXQiXX0.Pp1SxijP4gd1r9dXeRyRsI80f5T7brPbGUH0PC85K1KwlfN_G0wDLPIGQWeiACDScZY6M-2FtuW3Bxux3OpMdPMhr5jPW4isHcg8RWYoixAWjH3qQlW0PiDki7SpHvdXtr_BKVp_5LyMKKBC8zD4-sTpCTBVW3zHPd8__-rli72XgT4nYOyyYOXNhlVFMD4JPRZAyU4XVesrWctJtQ6WOg0ly4diiVJdmkpSRv7T3DzjvQ3bS0idFKxLX64x2BarQMmoWFCag6-Bg2Ed6aB0eQQtJYxleVwonWW5WU2Ir9FtezE29bezl11aP8i96Vmza0d395EnmdDID1I-1WddIw"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def get_subscriptions():
    url = f"{BASE_URL}/v1/Subscription/GetSubscriptionsForUser"
    response = requests.get(url, headers=headers)

    print("=== Subscriptions ===")
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text)
    response.raise_for_status()

    data = response.json()
    # Print a simple list to see the shape
    for idx, s in enumerate(data):
        print(f"{idx}: {s}")
    return data

def get_plans(subscription_id: str):
    # Use subscriptionId as part of the path, not as ?subscriptionId=...
    url = f"{BASE_URL}/v1/Plan/GetPlanInfoForSubscription/{subscription_id}"
    response = requests.get(url, headers=headers)

    print("\n=== Plans for subscription ===")
    print("URL:", response.url)
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text)
    response.raise_for_status()

    data = response.json()
    for idx, p in enumerate(data):
        print(f"{idx}: {p}")
    return data

def get_lanes(subscription_id,plan_id: str):
    # NOTE: This path is an educated guess based on the other endpoints.
    # If you get a 404, open https://nvpapi.test.nialli.com/swagger
    # and search for "Lane" to copy the exact path they use.
    url = f"{BASE_URL}/v1/Lane/GetLanesForPlan/{subscription_id}/{plan_id}"
    response = requests.get(url, headers=headers)

    print("\n=== Lanes for plan ===")
    print("URL:", response.url)
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text)
    response.raise_for_status()

    data = response.json()
    for idx, lane in enumerate(data):
        name = lane.get("laneName") or lane.get("name")
        lid = lane.get("laneId") or lane.get("id")
        print(f"{idx}: {name}  (laneId={lid})")
    return data

def get_activities(subscription_id: str, plan_id: str, skip: int = 0, take: int = 100):
    url = f"{BASE_URL}/v1/Activity/GetActivitiesForPlan/{subscription_id}/{plan_id}/{skip}/{take}"
    response = requests.get(url, headers=headers)

    print("\n=== Activities for plan ===")
    print("URL:", response.url)
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text)

    if response.status_code != 200:
        # Log and return empty list so the rest of the script can continue
        print("⚠️ Activities endpoint failed, returning empty list for now.")
        return []

    data = response.json()
    for idx, act in enumerate(data):
        desc = act.get("description") or act.get("activityName") or "<no name>"
        lane_id = act.get("laneId")
        act_id = act.get("activityId") or act.get("id")
        print(f"{idx}: {desc}  (activityId={act_id}, laneId={lane_id})")
    return data



if __name__ == "__main__":
    subs = get_subscriptions()

    if not subs:
        print("No subscriptions returned.")
    else:
        first_sub = subs[0]
        sub_id = first_sub.get("subscriptionId") or first_sub.get("id")

        print(f"\nUsing subscription ID: {sub_id}")
        plans = get_plans(sub_id)

        print("\n=== Plan List (index : name / id) ===")
        for idx, p in enumerate(plans):
            name = p.get("planName") or p.get("name")
            pid = p.get("planId") or p.get("id")
            print(f"{idx}: {name}  (planId={pid})")

        # For now, just automatically pick the first plan
        if plans:
            selected_plan = plans[0]
            plan_id = selected_plan.get("planId") or selected_plan.get("id")
            print(f"\nUsing plan ID: {plan_id}")
            lanes = get_lanes(sub_id,plan_id)
            activities = get_activities(sub_id, plan_id, skip=0, take=100)

        else:
            print("No plans found for this subscription.")
