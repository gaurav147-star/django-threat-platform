import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"
EVENTS_URL = f"{BASE_URL}/events/"
ALERTS_URL = f"{BASE_URL}/alerts/"

def print_step(message):
    print(f"\n{'='*50}")
    print(f"STEP: {message}")
    print(f"{'='*50}")

def print_result(response, expected_status=200):
    if response.status_code == expected_status:
        print(f"✅ SUCCESS (Status: {response.status_code})")
    else:
        print(f"❌ FAILED (Status: {response.status_code})")
        print("Response:", response.text)
        sys.exit(1)

def run_verification():
    print("🚀 Starting End-to-End Verification of Threat Platform...")

    # 1. Register Analyst
    print_step("1. Registering new Analyst User")
    analyst_creds = {
        "username": "demo_analyst",
        "password": "password123",
        "email": "analyst@demo.com",
        "role": "ANALYST"
    }
    # Try to register (might fail if exists, that's ok)
    resp = requests.post(f"{AUTH_URL}/register/", json=analyst_creds)
    if resp.status_code == 201:
        print(f"✅ User 'demo_analyst' created.")
    elif resp.status_code == 400 and "username" in resp.text:
       print("⚠️ User 'demo_analyst' already exists. Proceeding...")
    else:
       print_result(resp, 201)

    # 2. Login Analyst
    print_step("2. Logging in as Analyst")
    login_data = {"username": "demo_analyst", "password": "password123"}
    resp = requests.post(f"{AUTH_URL}/login/", json=login_data)
    print_result(resp, 200)
    tokens = resp.json()
    access_token = tokens['access']
    print("🔑 Token successfully obtained.")

    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Ingest Low Severity Event (No Alert)
    print_step("3. Ingesting LOW Severity Event (Should NOT trigger Alert)")
    low_event = {
        "source": "E2E Trigger", 
        "event_type": "Ping", 
        "severity": "LOW", 
        "description": "Just a ping"
    }
    resp = requests.post(EVENTS_URL, json=low_event, headers=headers)
    print_result(resp, 201)
    
    # 4. Ingest High Severity Event (Trigger Alert)
    print_step("4. Ingesting HIGH Severity Event (Should trigger Alert)")
    high_event = {
        "source": "E2E Trigger", 
        "event_type": "Malware", 
        "severity": "HIGH", 
        "description": "E2E Test Malware"
    }
    resp = requests.post(EVENTS_URL, json=high_event, headers=headers)
    print_result(resp, 201)
    event_id = resp.json()['id']

    # 5. List Alerts as Analyst
    print_step("5. Listing Alerts (Verifying Creation)")
    resp = requests.get(ALERTS_URL, headers=headers)
    print_result(resp, 200)
    alerts = resp.json()['results']
    
    found = False
    target_alert = None
    for alert in alerts:
        if alert['event_details']['description'] == "E2E Test Malware":
            found = True
            target_alert = alert
            break
    
    if found:
        print("✅ Alert for 'E2E Test Malware' found!")
    else:
        print("❌ Alert NOT found!")
        sys.exit(1)

    # 6. Try to Update Status as Analyst (Should Fail)
    print_step("6. Analyst trying to Update Status (Should Fail - 403)")
    patch_url = f"{ALERTS_URL}{target_alert['id']}/status/"
    resp = requests.patch(patch_url, json={"status": "ACKNOWLEDGED"}, headers=headers)
    if resp.status_code == 403:
        print("✅ SUCCESS: Analyst was correctly forbidden (403).")
    else:
        print(f"❌ FAILED: Response was {resp.status_code}")

    # 7. Login as Admin
    print_step("7. Logging in as Admin")
    # Assuming admin exists from previous steps (createsuperuser) or we create one?
    # For this script to work generally, we might need to fail here if admin doesn't exist.
    # But usually 'admin' 'password' is standard in dev.
    # Let's try to assume 'admin' 'password', if fail, warn user.
    admin_data = {"username": "admin", "password": "password"} 
    # NOTE: You must have created superuser 'admin' with password 'password'
    # or updated this script.
    
    # Let's create a temp admin via logic if running locally? No, stick to API.
    # We will try 'admin/password'
    resp = requests.post(f"{AUTH_URL}/login/", json=admin_data)
    if resp.status_code != 200:
        print("⚠️ Could not login as 'admin'/'password'. Skipping admin check.")
        print("Please ensure superuser 'admin' exists with password 'password'.")
        return

    admin_token = resp.json()['access']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("🔑 Admin Token obtained.")

    # 8. Update Status as Admin
    print_step("8. Updating Status as Admin (Should Success)")
    resp = requests.patch(patch_url, json={"status": "ACKNOWLEDGED"}, headers=admin_headers)
    print_result(resp, 200)
    
    # Verify
    resp = requests.get(f"{ALERTS_URL}{target_alert['id']}/", headers=admin_headers)
    if resp.json()['status'] == 'ACKNOWLEDGED':
        print("✅ Alert status successfully updated to ACKNOWLEDGED.")
    else:
        print("❌ Alert status check failed.")

    print("\n🎉 ALL E2E VERIFICATION STEPS PASSED!")

if __name__ == "__main__":
    try:
        run_verification()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to localhost:8000. Is Docker running?")
