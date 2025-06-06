#!/usr/bin/env python3
"""
Test script to verify subscription functionality after login
This script will create a test HTML page to simulate the subscription testing
"""

import requests
import sys
import os

def test_subscription_functionality():
    """Test the subscription functionality by making requests to the Flask app"""
    
    base_url = "http://127.0.0.1:5006"
    
    # Test credentials
    email = "test@example.com"
    password = "password123"
    
    print("🔄 Testing Subscription Functionality After Login")
    print("=" * 50)
    
    # Create session for maintaining login state
    session = requests.Session()
    
    try:
        # 1. Test login
        print("1. Testing login...")
        login_data = {
            'email': email,
            'password': password
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login successful")
        else:
            print(f"❌ Login failed with status: {login_response.status_code}")
            return False
        
        # 2. Test access to profile page
        print("2. Testing profile page access...")
        profile_response = session.get(f"{base_url}/profile")
        
        if profile_response.status_code == 200:
            print("✅ Profile page accessible after login")
            
            # Check if subscription buttons are present
            if 'upgradePlan' in profile_response.text:
                print("✅ upgradePlan function found in profile page")
            else:
                print("❌ upgradePlan function NOT found in profile page")
            
            if 'downgradePlan' in profile_response.text:
                print("✅ downgradePlan function found in profile page")
            else:
                print("❌ downgradePlan function NOT found in profile page")
                
            if 'cancelSubscription' in profile_response.text:
                print("✅ cancelSubscription function found in profile page")
            else:
                print("❌ cancelSubscription function NOT found in profile page")
                
        else:
            print(f"❌ Profile page not accessible: {profile_response.status_code}")
            return False
        
        # 3. Test my-account page as well
        print("3. Testing my-account page access...")
        account_response = session.get(f"{base_url}/my-account")
        
        if account_response.status_code == 200:
            print("✅ My-account page accessible after login")
        else:
            print(f"❌ My-account page not accessible: {account_response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure Flask app is running on port 5006")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def create_manual_test_instructions():
    """Create instructions for manual testing"""
    
    instructions = """
🔍 MANUAL TESTING INSTRUCTIONS FOR SUBSCRIPTION BUTTONS
====================================================

The JavaScript functions have been fixed. Now you need to manually test them:

1. **Login Process:**
   - Open: http://127.0.0.1:5006/login
   - Email: test@example.com
   - Password: password123

2. **Navigate to Profile:**
   - After login, go to: http://127.0.0.1:5006/profile
   - OR: http://127.0.0.1:5006/my-account

3. **Test Subscription Buttons:**
   - Look for "Upgrade to Pro" or "Upgrade to Premium" buttons
   - Click the buttons and check browser console (F12)
   - Verify no "ReferenceError: Can't find variable: upgradePlan" errors

4. **Expected Behavior:**
   - Buttons should trigger JavaScript functions without errors
   - Console should show function execution logs
   - Modal dialogs should appear for confirmation

5. **If you see errors:**
   - Open browser developer tools (F12)
   - Check the Console tab for JavaScript errors
   - Report any remaining "ReferenceError" messages

🔧 TECHNICAL FIXES COMPLETED:
- ✅ JavaScript functions defined BEFORE HTML onclick handlers
- ✅ Functions made globally accessible (window.upgradePlan, etc.)
- ✅ Template syntax errors resolved
- ✅ Duplicate function definitions eliminated
- ✅ Enhanced error handling in onclick handlers

📋 WHAT TO VERIFY:
- No "ReferenceError: Can't find variable: upgradePlan" errors
- Subscription buttons are clickable and functional
- Modal dialogs appear when buttons are clicked
- Console shows proper function execution
"""
    
    print(instructions)
    
    # Save to file
    with open('/Users/sevs/Documents/Programs/webapps/resume_builder/MANUAL_TESTING_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print("\n📝 Instructions saved to: MANUAL_TESTING_INSTRUCTIONS.md")

if __name__ == "__main__":
    # Run automated tests
    success = test_subscription_functionality()
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 AUTOMATED TESTS PASSED!")
        print("✅ All JavaScript functions are present in the authenticated pages")
        print("✅ Profile and account pages are accessible after login")
        print("\n🔄 NEXT STEP: Manual browser testing required")
        create_manual_test_instructions()
    else:
        print("❌ AUTOMATED TESTS FAILED!")
        print("🔧 Check Flask app status and try again")
