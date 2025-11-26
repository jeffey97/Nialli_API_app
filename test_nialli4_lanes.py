import requests

BASE_URL = "https://nvpapi.nialli.com"  # test environment
ACCESS_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InVRTVFfUlBfcDVLcDRvdU81NFpDRSJ9.eyJhdXRoZW50aWNhdGVkZW1haWwiOiJtYXJrdXMuYW1hbGFuYXRoYW5AYWRpZGV2ZWxvcG1lbnRzLmNvbSIsImF1dGhlbnRpY2F0ZWQuZW1haWwiOiJtYXJrdXMuYW1hbGFuYXRoYW5AYWRpZGV2ZWxvcG1lbnRzLmNvbSIsImF1dGhlbnRpY2F0ZWQudXNlcmlkIjoiYXV0aDB8Njg2N2YxNzM4MDFmOTI0MzZiZTYxN2IzIiwiaXNzIjoiaHR0cHM6Ly9uaWFsbGktcHJvZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8Njg2N2YxNzM4MDFmOTI0MzZiZTYxN2IzIiwiYXVkIjoiaHR0cHM6Ly9udnBhcGkubmlhbGxpLmNvbS8iLCJpYXQiOjE3NjQxODY0MDAsImV4cCI6MTc2NDI3MjgwMCwiZ3R5IjoicGFzc3dvcmQiLCJhenAiOiJpRXg4cjZXTjJEenR1U3NpVjZNV2dJbGllREtCUnh3aiIsInBlcm1pc3Npb25zIjpbInN1YnNjcmlwdGlvbjpnZXQiXX0.Q42E5tjvTYEgvqOYQ6k5gA1V911MNvjCTi_XR-1CIfnFilff-nMKYjTlhP1A-f3BMoUS1oiexL33bR6scZFvT9q_lgCKU5nm5PDY1xN_YaISdgZJOByJ4mv9nvLs1UuqWUdibISbyCLn_7Q9DCm7g6gXaRyV3abAwiy_eI4dXVEN-h82QZKnoLmwjlpkDlqss2ZNJ8KH-IXYd9WHe34zKyqZlo8nTLk1FJBR3TvG1h1hhAJMsaQg3XESes6ZGPmtsuWPON25mDadc2fkE-mpINp1LYHFotqvkW4pKNSFZhTPY8Ojc2ObgSYOE0rHNTOae7UbZt3MjWvlrYkOL2LSmw"
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
            selected_plan = plans[1]
            plan_id = selected_plan.get("planId") or selected_plan.get("id")
            print(f"\nUsing plan ID: {plan_id}")
            lanes = get_lanes(sub_id,plan_id)  

        else:
            print("No plans found for this subscription.")
