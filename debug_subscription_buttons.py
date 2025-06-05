#!/usr/bin/env python3
"""
Quick Debug Script for Subscription Button Issues
"""

import requests
import sys

def test_subscription_buttons():
    print("🔍 DEBUGGING SUBSCRIPTION BUTTON ISSUE")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5006"
    
    # Test 1: Check if app is running
    print("1. Testing app connectivity...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("   ✅ App is running")
        else:
            print(f"   ❌ App error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Can't connect to app: {e}")
        return
    
    # Test 2: Check if you can access My Account page
    print("2. Testing My Account page access...")
    try:
        response = requests.get(f"{base_url}/my-account")
        if response.status_code == 200:
            print("   ✅ My Account accessible (you're logged in)")
        elif response.status_code == 302:
            print("   ❌ Redirected to login (you need to log in)")
            print("   💡 Solution: Go to http://127.0.0.1:5006/login first")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error accessing account: {e}")
    
    # Test 3: Test subscription endpoint (without auth)
    print("3. Testing subscription endpoint...")
    try:
        response = requests.post(f"{base_url}/create-checkout-session", 
                               data={'plan': 'Pro'}, 
                               allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if 'login' in location:
                print("   ❌ Endpoint requires login")
                print("   💡 This is why the button doesn't work - you need to log in!")
            else:
                print(f"   ⚠️  Redirects to: {location}")
        elif response.status_code == 303:
            print("   ✅ Endpoint working (would redirect to Stripe)")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Endpoint error: {e}")
    
    print("\n🎯 SOLUTION:")
    print("1. Go to: http://127.0.0.1:5006/login")
    print("2. Log in to your account")
    print("3. Go to: http://127.0.0.1:5006/my-account")
    print("4. Try clicking the subscription buttons again")
    print("\n📝 The buttons require you to be logged in to work!")

if __name__ == "__main__":
    test_subscription_buttons()
