import sys
import os
import random
import string
import json
from datetime import date

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.pipeline import PIIPipeline
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

# Manually load pipeline to ensure it's available for redact calls
print("Manually loading PIIPipeline...")
try:
    app.state.pii_pipeline = PIIPipeline()
    print("PIIPipeline loaded.")
except Exception as e:
    print(f"Failed to load pipeline: {e}")
    sys.exit(1)

def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def verify_stats():
    client = TestClient(app)
    
    # 1. Register a new user
    email = f"{get_random_string()}@example.com"
    password = "password123"
    print(f"\nRegistering user: {email}")
    
    register_response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password}
    )
    
    if register_response.status_code != 200:
        print(f"Registration failed: {register_response.text}")
        return

    print("Registration successful.")

    # 2. Login
    print("Logging in...")
    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful, token received.")

    # 3. Check initial stats (should be 0)
    print("Checking initial stats...")
    stats_response = client.get("/api/dashboard/user-stats", headers=headers)
    if stats_response.status_code != 200:
        print(f"Failed to get stats: {stats_response.text}")
        return
    
    stats = stats_response.json()
    print(f"Initial stats: {json.dumps(stats, indent=2)}")
    
    if stats["total_files_redacted"] != 0:
        print("Error: Initial total_files_redacted is not 0")
        return

    # 4. Perform some redactions
    print("Performing redaction actions...")
    
    # Redaction 1: Plain text
    redact_response = client.post(
        "/api/redact",
        headers=headers,
        json={"text": "My email is john@example.com"}
    )
    if redact_response.status_code != 200:
        print(f"Redaction 1 failed: {redact_response.text}")
        return
    
    # Redaction 2: Plain text
    redact_response = client.post(
        "/api/redact",
        headers=headers,
        json={"text": "Contact me at 555-0199"}
    )
    if redact_response.status_code != 200:
        print(f"Redaction 2 failed: {redact_response.text}")
        return

    print("Redactions completed.")

    # 5. Check stats again
    print("Checking updated stats...")
    stats_response = client.get("/api/dashboard/user-stats", headers=headers)
    if stats_response.status_code != 200:
        print(f"Failed to get stats: {stats_response.text}")
        return
    
    stats = stats_response.json()
    print(f"Updated stats: {json.dumps(stats, indent=2)}")

    # Verification
    if stats["total_files_redacted"] == 2:
        print("SUCCESS: total_files_redacted matched expected value (2)")
    else:
        print(f"FAILURE: total_files_redacted expected 2, got {stats['total_files_redacted']}")
        
    today_str = str(date.today())
    recent_entry = next((item for item in stats["recent_activity"] if item["date"] == today_str), None)
    
    if recent_entry and recent_entry["count"] == 2:
        print(f"SUCCESS: Recent activity for today correct: {recent_entry}")
    else:
        print(f"FAILURE: Recent activity for today incorrect. Expected 2, got {recent_entry}")

if __name__ == "__main__":
    verify_stats()
