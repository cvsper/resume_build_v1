#!/usr/bin/env python3
"""
Debug the webhook endpoint issue
"""

import requests
import json

def test_webhook_debug():
    """Test webhook with different payloads to isolate the issue"""
    
    base_url = "http://127.0.0.1:5006"
    
    # First test the app is running
    print("1. Testing if app is running...")
    try:
        response = requests.get(base_url, timeout=5)
        print(f"   App status: {response.status_code}")
    except Exception as e:
        print(f"   App error: {e}")
        return
    
    # Test webhook endpoint with GET (should return 405)
    print("\n2. Testing webhook GET (should be 405)...")
    try:
        response = requests.get(f"{base_url}/stripe-webhook", timeout=5)
        print(f"   GET status: {response.status_code}")
    except Exception as e:
        print(f"   GET error: {e}")
    
    # Test webhook with empty POST
    print("\n3. Testing webhook with empty POST...")
    try:
        response = requests.post(f"{base_url}/stripe-webhook", timeout=5)
        print(f"   Empty POST status: {response.status_code}")
        print(f"   Empty POST response: {response.text}")
    except Exception as e:
        print(f"   Empty POST error: {e}")
    
    # Test webhook with invalid JSON
    print("\n4. Testing webhook with invalid JSON...")
    try:
        response = requests.post(
            f"{base_url}/stripe-webhook",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"   Invalid JSON status: {response.status_code}")
        print(f"   Invalid JSON response: {response.text}")
    except Exception as e:
        print(f"   Invalid JSON error: {e}")
    
    # Test webhook with valid JSON but no type
    print("\n5. Testing webhook with valid JSON (no type)...")
    try:
        response = requests.post(
            f"{base_url}/stripe-webhook",
            json={"test": "data"},
            timeout=5
        )
        print(f"   Valid JSON status: {response.status_code}")
        print(f"   Valid JSON response: {response.text}")
    except Exception as e:
        print(f"   Valid JSON error: {e}")

if __name__ == "__main__":
    test_webhook_debug()
