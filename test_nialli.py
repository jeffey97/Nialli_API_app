import requests
import json
import base64
import time

BASE_URL = "https://nvpapi.test.nialli.com"
ACCESS_TOKEN = "yJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlRCWWEwSTBSeEtMU2Nxb1BnUDBHVSJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOltdLCJodHRwczovL2xvY2FsaG9zdDo0NDQzNi9lbWFpbCI6Im1hcmt1cy5hbWFsYW5hdGhhbkBhZGlkZXZlbG9wbWVudHMuY29tIiwiYXV0aGVudGljYXRlZGVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLmVtYWlsIjoibWFya3VzLmFtYWxhbmF0aGFuQGFkaWRldmVsb3BtZW50cy5jb20iLCJhdXRoZW50aWNhdGVkLnVzZXJpZCI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImlzcyI6Imh0dHBzOi8vbmlhbGxpLXRlc3QudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY3MzRjOTQ3MTQxNTlhZmQxMTFhZjJiMCIsImF1ZCI6Imh0dHBzOi8vbnZwYXBpLnRlc3QubmlhbGxpLmNvbS8iLCJpYXQiOjE3NjMxNzIwMjgsImV4cCI6MTc2MzI1ODQyOCwiZ3R5IjoicGFzc3dvcmQiLCJhenAiOiJlY2JMbWFxa0RpUkVjOG5xaEFPbjNZMnJyeTFadUxLUyIsInBlcm1pc3Npb25zIjpbInN1YnNjcmlwdGlvbjpnZXQiXX0.LZYMLhI5bpC8Wj3KXg5ZRQKJ4vqTykPbKLH28gbRt53M6iJaocuCpxAG5piApaTVwITlQTiCwDvgozlT-uW76ax7deBKSGhK3r0Ix-QBJkzi8nSUdxe8TmbaF4yRBec91AHljIUKGz1ZyNP2-_SGTc6ZZ73zmcFY_TFQ4KGdbqq0ZhWg_sY2a5Aw9eqB2PRMupCWdpScLVl16Yp4_Vk8DEFkGa_9OlDESwyV-CZmzgGB602FzAvKheV5eYW3EcYp6E1v6oRFX_AbzUdH5_FDwp6xJvbGWykPya9qMAgwWWtBlCbcoNUSKSZdjmJnlI6cjSiNk8vxQDXmk6u0z_TpaA"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def decode_token(token):
    """Decode JWT token to see its contents"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def get_subscriptions():
    url = f"{BASE_URL}/v1/Subscription/GetSubscriptionsForUser"
    
    # Debug: Show token info
    print("=" * 60)
    print("DEBUG INFO")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Authorization Header: Bearer {ACCESS_TOKEN[:50]}...")
    
    token_info = decode_token(ACCESS_TOKEN)
    if token_info:
        print(f"\nToken Details:")
        print(f"  Audience (aud): {token_info.get('aud')}")
        print(f"  Issuer (iss): {token_info.get('iss')}")
        print(f"  Permissions: {token_info.get('permissions')}")
        print(f"  Expires at: {token_info.get('exp')}")
        print(f"  Current time: {int(time.time())}")
        print(f"  Token expired: {int(time.time()) > token_info.get('exp', 0)}")
    print("=" * 60)
    print()
    
    try:
        print(f"Making GET request to: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print("\n" + "=" * 60)
        print("RESPONSE")
        print("=" * 60)
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print(f"\nResponse Body:\n{response.text}")
        print("=" * 60)
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                data = response.json()
                print("\n✅ SUCCESS - Parsed JSON:")
                print(json.dumps(data, indent=2))
            except ValueError:
                print("\n⚠️  Response is not valid JSON")
        elif response.status_code == 401:
            print("\n❌ Authentication failed - Token may be invalid or expired")
            print("   Check that the token audience matches the API URL")
        elif response.status_code == 403:
            print("\n❌ Forbidden - Token may not have required permissions")
            print(f"   Token has permissions: {token_info.get('permissions') if token_info else 'unknown'}")
        elif response.status_code == 404:
            print("\n❌ Not Found - The endpoint may not exist or URL is incorrect")
        else:
            print(f"\n⚠️  Request failed with status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - The server took too long to respond")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("   Check your internet connection and that the API server is accessible")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    get_subscriptions()
