import requests

BASE_URL = "https://nvpapi.test.nialli.com"  # test environment
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlRCWWEwSTBSeEtMU2Nxb1BnUDBHVSJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOltdLCJodHRwczovL2xvY2FsaG9zdDo0NDQzNi9lbWFpbCI6Im1hcmt1cy5hbWFsYW5hdGhhbkBhZGlkZXZlbG9wbWVudHMuY29tIiwiYXV0aGVudGljYXRlZGVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLmVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLnVzZXJpZCI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImlzcyI6Imh0dHBzOi8vbmlhbGxpLXRlc3QudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImF1ZCI6Imh0dHBzOi8vbnZwYXBpLnRlc3QubmlhbGxpLmNvbS8iLCJpYXQiOjE3NjMxNzIwMjgsImV4cCI6MTc2MzI1ODQyOCwiZ3R5IjoicGFzc3dvcmQiLCJhenAiOiJlY2JMbWFxa0RpUkVjOG5xaEFPbjNZMnJyeTFadUxLUyIsInBlcm1pc3Npb25zIjpbInN1YnNjcmlwdGlvbjpnZXQiXX0.LZYMLhI5bpC8Wj3KXg5ZRQKJ4vqTykPbKLH28gbRt53M6iJaocuCpxAG5piApaTVwITlQTiCwDvgozlT-uW76ax7deBKSGhK3r0Ix-QBJkzi8nSUdxe8TmbaF4yRBec91AHljIUKGz1ZyNP2-_SGTc6ZZ73zmcFY_TFQ4KGdbqq0ZhWg_sY2a5Aw9eqB2PRMupCWdpScLVl16Yp4_Vk8DEFkGa_9OlDESwyV-CZmzgGB602FzAvKheV5eYW3EcYp6E1v6oRFX_AbzUdH5_FDwp6xJvbGWykPya9qMAgwWWtBlCbcoNUSKSZdjmJnlI6cjSiNk8vxQDXmk6u0z_TpaA"

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
    url = f"{BASE_URL}/v1/Plan/GetPlanInfoForSubscription"
    params = {"subscriptionId": subscription_id}
    response = requests.get(url, headers=headers, params=params)

    print("\n=== Plans for subscription ===")
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text)
    response.raise_for_status()

    data = response.json()
    for idx, p in enumerate(data):
        print(f"{idx}: {p}")
    return data

if __name__ == "__main__":
    subs = get_subscriptions()

    # Safely pick the first subscription and get its ID field
    if not subs:
        print("No subscriptions returned.")
    else:
        first_sub = subs[0]
        # Try common key names; adjust if needed based on printed JSON
        sub_id = first_sub.get("subscriptionId") or first_sub.get("id")

        print(f"\nUsing subscription ID: {sub_id}")
        plans = get_plans(sub_id)
