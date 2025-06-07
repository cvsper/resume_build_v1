#!/usr/bin/env python3
"""
Test the Voice Interview API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5009"

def test_start_interview():
    """Test starting a voice interview"""
    print("🧪 Testing start interview API...")
    
    # Mock session cookie (you'll need to login first in browser)
    response = requests.post(
        f"{BASE_URL}/api/start-voice-interview",
        headers={"Content-Type": "application/json"},
        json={
            "job_title": "Software Engineer",
            "personality": "friendly"
        },
        # Note: This won't work without proper session cookie
        # You need to be logged in
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("❌ Need to be logged in - that's expected")
        return False
    elif response.status_code == 200:
        print("✅ API endpoint is working!")
        return True
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Voice Interview API...")
    test_start_interview()
    print("\n📋 To test properly:")
    print("1. Go to http://127.0.0.1:5009/login")
    print("2. Login to your account") 
    print("3. Go to http://127.0.0.1:5009/interview_qa")
    print("4. Try the AI Voice Interview section")