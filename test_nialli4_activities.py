import requests
from datetime import datetime, date
import json

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
    
    # Debug: Discover all date-related fields in the response
    if data:
        print("\n=== DEBUG: First activity structure ===")
        print(json.dumps(data[0], indent=2, default=str))
        print("\n=== DEBUG: All keys in first activity ===")
        print(list(data[0].keys()))
        
        # Find all keys that might contain dates (look for 'date' in key name or date-like values)
        print("\n=== DEBUG: Scanning for date-related fields ===")
        date_fields = {}
        for act in data[:5]:  # Check first 5 activities
            for key, value in act.items():
                # Check if key name suggests a date
                if any(word in key.lower() for word in ['date', 'time', 'start', 'end', 'from', 'to', 'scheduled', 'planned', 'actual']):
                    if key not in date_fields:
                        date_fields[key] = []
                    date_fields[key].append(value)
                # Or check if value looks like a date string
                elif isinstance(value, str) and len(value) >= 10:
                    # Check for ISO date patterns like "2024-11-27" or "2024-11-27T..."
                    if value[4:5] == '-' and value[7:8] == '-':
                        if key not in date_fields:
                            date_fields[key] = []
                        date_fields[key].append(value)
        
        print("Potential date fields found:")
        for field_name, sample_values in date_fields.items():
            unique_values = list(set(str(v) for v in sample_values[:3]))  # Show up to 3 unique samples
            print(f"  '{field_name}': {unique_values}")
    
    # Filter activities to only show those that happen today
    today = date.today()
    filtered_activities = []
    activities_with_null_dates = []
    
    for act in data:
        # Try multiple possible date field names
        start_date_str = (act.get("startDate") or 
                         act.get("startDateTime") or 
                         act.get("scheduledStartDate") or
                         act.get("plannedStartDate") or
                         act.get("actualStartDate") or
                         act.get("start") or
                         act.get("dateStart") or
                         act.get("fromDate"))
        
        end_date_str = (act.get("endDate") or 
                       act.get("endDateTime") or 
                       act.get("scheduledEndDate") or
                       act.get("plannedEndDate") or
                       act.get("actualEndDate") or
                       act.get("end") or
                       act.get("dateEnd") or
                       act.get("toDate"))
        
        # Track activities with null dates for debugging
        if not start_date_str or not end_date_str:
            activities_with_null_dates.append({
                "activityId": act.get("activityId") or act.get("id"),
                "description": act.get("description") or act.get("activityName"),
                "all_keys": list(act.keys())
            })
            continue
        
        # Parse dates (handle both date-only and datetime strings)
        try:
            # Try parsing as date first (YYYY-MM-DD)
            if isinstance(start_date_str, str) and len(start_date_str) == 10:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            elif isinstance(start_date_str, str):
                # Try parsing as datetime and extract date
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
            else:
                continue
                
            if isinstance(end_date_str, str) and len(end_date_str) == 10:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            elif isinstance(end_date_str, str):
                # Try parsing as datetime and extract date
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()
            else:
                continue
        except (ValueError, AttributeError) as e:
            print(f"⚠️ Could not parse dates for activity {act.get('activityId')}: {e}")
            continue
        
        # Include activity if it overlaps with today
        # Activity overlaps with today if: start_date <= today <= end_date
        if start_date <= today <= end_date:
            filtered_activities.append(act)
    
    print(f"\n=== Filtered Activities (happening today: {today}) ===")
    print(f"Total activities fetched: {len(data)}")
    print(f"Activities happening today: {len(filtered_activities)}")
    print(f"Activities with null/missing dates: {len(activities_with_null_dates)}")
    
    # Print info about activities with null dates
    if activities_with_null_dates:
        print("\n=== Activities with null dates (first 5) ===")
        for idx, act_info in enumerate(activities_with_null_dates[:5]):
            print(f"{idx}: {act_info['description']} (ID: {act_info['activityId']})")
            print(f"   Available keys: {act_info['all_keys']}")
    
    for idx, act in enumerate(filtered_activities):
        desc = act.get("description") or act.get("activityName") or "<no name>"
        lane_id = act.get("laneId")
        act_id = act.get("activityId") or act.get("id")
        start_date_str = act.get("startDate") or act.get("startDateTime") or act.get("scheduledStartDate") or "N/A"
        end_date_str = act.get("endDate") or act.get("endDateTime") or act.get("scheduledEndDate") or "N/A"
        print(f"{idx}: {desc}  (activityId={act_id}, laneId={lane_id}, start={start_date_str}, end={end_date_str})")
    
    return filtered_activities



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
            activities = get_activities(sub_id, plan_id, skip=0, take=100)

        else:
            print("No plans found for this subscription.")
