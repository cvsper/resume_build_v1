#!/usr/bin/env python3
"""
Test subscription buttons after proper authentication
"""

import requests
import time

def test_with_authentication():
    print("🔑 Testing subscription buttons with authentication...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # First, try to access the profile page to see if we're redirected
        print("📄 Accessing profile page...")
        profile_response = session.get("http://127.0.0.1:5006/profile", timeout=10)
        
        print(f"Profile response status: {profile_response.status_code}")
        print(f"Response length: {len(profile_response.text)} characters")
        
        # Check if we're on the login page
        if "Sign In" in profile_response.text and "AI Job Hunter" in profile_response.text:
            print("🔐 Redirected to login page - user not authenticated")
            
            # Try to create a test user or login with existing credentials
            print("🧪 Attempting to create/login with test user...")
            
            # First try to register a test user
            register_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'testpassword123',
                'confirm_password': 'testpassword123'
            }
            
            register_response = session.post("http://127.0.0.1:5006/register", 
                                           data=register_data, 
                                           timeout=10)
            
            if register_response.status_code == 200:
                print("✅ Registration successful or user exists")
            else:
                print(f"Registration status: {register_response.status_code}")
            
            # Now try to login
            login_data = {
                'email': 'test@example.com',
                'password': 'testpassword123'
            }
            
            login_response = session.post("http://127.0.0.1:5006/login", 
                                        data=login_data, 
                                        timeout=10)
            
            print(f"Login response status: {login_response.status_code}")
            
            # Try to access profile page again after login
            print("📄 Accessing profile page after login...")
            profile_response_2 = session.get("http://127.0.0.1:5006/profile", timeout=10)
            
            print(f"Profile response status after login: {profile_response_2.status_code}")
            print(f"Response length after login: {len(profile_response_2.text)} characters")
            
            # Check if we now have the subscription functionality
            if "upgradePlan" in profile_response_2.text:
                print("✅ upgradePlan function found after authentication!")
            else:
                print("❌ upgradePlan function still not found")
                
            if "window.upgradePlan = upgradePlan" in profile_response_2.text:
                print("✅ Global function assignment found!")
            else:
                print("❌ Global function assignment not found")
                
            # Check for subscription-related content
            if "subscription" in profile_response_2.text.lower():
                print("✅ Subscription content found in authenticated page")
            else:
                print("❌ No subscription content found")
                
            # Look for upgrade buttons
            if "select-plan-btn upgrade" in profile_response_2.text:
                print("✅ Upgrade buttons found in HTML")
            else:
                print("❌ Upgrade buttons not found")
                
        else:
            print("✅ Already authenticated - checking subscription functionality...")
            
            # Check if we have the subscription functionality
            if "upgradePlan" in profile_response.text:
                print("✅ upgradePlan function found!")
            else:
                print("❌ upgradePlan function not found")
                        
    except Exception as e:
        print(f"❌ Error during authentication test: {str(e)}")

def main():
    test_with_authentication()

if __name__ == "__main__":
    main()
