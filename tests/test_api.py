"""
Debug script to test premium endpoint access control
Run this to verify that researchers cannot access premium endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000"
RESEARCHER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo4LCJ1c2VybmFtZSI6IkZpenk1IiwiZW1haWwiOiJjYm5waXBzQGdtYWlsLmNvbSIsInJvbGUiOiJyZXNlYXJjaGVyIiwic3Vic2NyaXB0aW9uX2lkIjozLCJwbGFuX3R5cGUiOiJyZXNlYXJjaGVyIiwicGxhbl9uYW1lIjoiUmVzZWFyY2hlciBQcm8iLCJyYXRlX2xpbWl0Ijo1MDAwLCJmZWF0dXJlcyI6WyJBZHZhbmNlZCBhbmFseXRpY3MgZGFzaGJvYXJkIiwiOTAgZGF5cyBoaXN0b3JpY2FsIGRhdGEiLCJDU1YgYW5kIEpTT04gZXhwb3J0cyIsIlByZWRpY3RpdmUgaW5zaWdodHMiLCJQcmlvcml0eSBlbWFpbCBzdXBwb3J0IiwiUmVzZWFyY2ggY29sbGFib3JhdGlvbiB0b29scyIsIkN1c3RvbSBkYXRhIGZpbHRlcmluZyIsIkJ1bGsgZGF0YSBkb3dubG9hZHMiXSwic3Vic2NyaXB0aW9uX2VuZCI6IjIwMjUtMTItMDlUMTk6MzE6NDcuODYxOTgzKzAwOjAwIiwiZGF5c19yZW1haW5pbmciOjg5LCJpYXQiOjE3NTc1MzI3MzIsImV4cCI6MTc2MDEyNDczMiwic3Vic2NyaXB0aW9uX2FjdGl2ZSI6dHJ1ZSwiYXV0b19yZW5ldyI6dHJ1ZSwianRpIjoiYzE3MWRmZmE0MTVjNzJkYTQ3MWViNmVkNTRmNTRhM2MifQ.ydbUVI_axEolQmKj89bRPEW3u-zfXHvKiF9yhht1ya0"

def test_endpoint(endpoint, token, description):
    """Test a single endpoint with the given token"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"Token Type: Researcher (Fizy5)")
    print(f"{'='*60}")
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("❌ ACCESS GRANTED - This is a problem! Researchers should not access premium endpoints!")
            print("Response preview:")
            response_data = response.json()
            print(json.dumps(response_data, indent=2)[:500] + "...")
        elif response.status_code == 403:
            print("✅ ACCESS DENIED - Working correctly!")
            print("Error message:")
            response_data = response.json()
            if 'error' in response_data:
                print(f"  Error: {response_data['error']}")
            if 'message' in response_data:
                print(f"  Message: {response_data['message']}")
            if 'permission_analysis' in response_data.get('user_subscription_analysis', {}):
                analysis = response_data['user_subscription_analysis']['permission_analysis']
                print(f"  Permission Analysis:")
                print(f"    - {analysis.get('role_check_result', '')}")
                print(f"    - {analysis.get('plan_check_result', '')}")
                print(f"    - {analysis.get('overall_access', '')}")
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error testing endpoint: {e}")

def main():
    print("="*60)
    print("PREMIUM ENDPOINT ACCESS CONTROL TEST")
    print("Testing researcher token against premium endpoints")
    print("Expected: All premium endpoints should return 403 Forbidden")
    print("="*60)
    
    # Test premium endpoints that should be blocked
    premium_endpoints = [
        ("/premium/telemetry/full", "Premium Full Telemetry Data"),
        ("/premium/analytics/advanced", "Premium Advanced Analytics"),
    ]
    
    # Test research endpoints that should be allowed
    research_endpoints = [
        ("/research/telemetry", "Research Telemetry Data"),
        ("/research/analytics/salinity", "Research Salinity Analytics"),
    ]
    
    print("\n" + "="*60)
    print("TESTING PREMIUM ENDPOINTS (Should be BLOCKED)")
    print("="*60)
    
    for endpoint, description in premium_endpoints:
        test_endpoint(endpoint, RESEARCHER_TOKEN, description)
    
    print("\n" + "="*60)
    print("TESTING RESEARCH ENDPOINTS (Should be ALLOWED)")
    print("="*60)
    
    for endpoint, description in research_endpoints:
        test_endpoint(endpoint, RESEARCHER_TOKEN, description)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("""
    If you see:
    - ✅ ACCESS DENIED for premium endpoints = Working correctly
    - ❌ ACCESS GRANTED for premium endpoints = BUG - needs fixing
    - Research endpoints should show actual data (200 OK)
    
    The decorator should check:
    1. Role must be 'admin' for premium
    2. Plan type must be 'premium' for premium
    3. Both conditions must be met
    """)

if __name__ == "__main__":
    main()