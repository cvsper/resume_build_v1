#!/usr/bin/env python3
"""Test script to verify the authentication fix"""

import requests
import time

# Base URL for the Flask app
BASE_URL = "http://127.0.0.1:5006"

def test_auth_flow():
    """Test the complete authentication flow"""
    print("🔄 Testing Authentication Flow...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Test registration
    print("📝 Testing Registration...")
    register_data = {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    try:
        # First, check if user already exists by trying to register
        register_response = session.post(f"{BASE_URL}/register", data=register_data)
        if register_response.status_code == 200:
            if 'Email already registered' in register_response.text:
                print("✅ User already exists, proceeding to login test")
            else:
                print("✅ Registration form rendered successfully")
        else:
            print(f"⚠️  Registration returned status: {register_response.status_code}")
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False
    
    # Step 2: Test login
    print("🔐 Testing Login...")
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        if login_response.status_code == 200:
            # Check if we were redirected to dashboard (success)
            if 'dashboard' in login_response.url or login_response.history:
                print("✅ Login successful - redirected to dashboard")
                
                # Step 3: Test access to upload page
                print("📤 Testing Upload Page Access...")
                upload_response = session.get(f"{BASE_URL}/upload-existing-resume")
                if upload_response.status_code == 200:
                    print("✅ Upload page accessible after login")
                    return True
                else:
                    print(f"❌ Upload page returned status: {upload_response.status_code}")
                    print("Response content preview:", upload_response.text[:200])
            else:
                print("❌ Login failed - no redirect to dashboard")
                print("Response content preview:", login_response.text[:500])
        else:
            print(f"❌ Login returned status: {login_response.status_code}")
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False
    
    return False

def test_direct_upload_access():
    """Test direct access to upload page (should redirect to login)"""
    print("🔄 Testing Direct Upload Access (should redirect to login)...")
    
    try:
        response = requests.get(f"{BASE_URL}/upload-existing-resume", allow_redirects=False)
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if 'login' in location:
                print("✅ Upload page correctly redirects to login when not authenticated")
                return True
            else:
                print(f"⚠️  Upload page redirects to: {location}")
        else:
            print(f"❌ Expected redirect (302), got: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct access test failed: {e}")
    
    return False

def main():
    print("🚀 Starting Authentication Fix Verification\n")
    
    # Wait a moment for the server to be ready
    time.sleep(2)
    
    # Test if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running and accessible\n")
        else:
            print(f"⚠️  Server responded with status: {response.status_code}\n")
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        print("Make sure the Flask app is running on http://127.0.0.1:5006")
        return
    
    # Run tests
    direct_access_ok = test_direct_upload_access()
    print()
    auth_flow_ok = test_auth_flow()
    
    print("\n" + "="*50)
    print("📊 AUTHENTICATION FIX RESULTS:")
    print("="*50)
    print(f"Direct Access Protection: {'✅ PASS' if direct_access_ok else '❌ FAIL'}")
    print(f"Complete Auth Flow: {'✅ PASS' if auth_flow_ok else '❌ FAIL'}")
    
    if direct_access_ok and auth_flow_ok:
        print("\n🎉 Authentication fix is SUCCESSFUL!")
        print("✅ Users can now properly log in and access the upload functionality")
    else:
        print("\n❌ Authentication issues still exist")
        print("💡 Check the Flask app logs for more details")

if __name__ == "__main__":
    main()
