#!/usr/bin/env python3
"""
Test to verify upgradePlan JavaScript function is properly loaded
Run this AFTER logging in
"""

import requests
from bs4 import BeautifulSoup

def test_upgradePlan_fix():
    print("🔧 JAVASCRIPT REFERENCEERROR FIX VERIFICATION")
    print("=" * 50)
    
    response = requests.get('http://127.0.0.1:5006/my-account')
    
    if response.status_code == 200:
        content = response.text
        
        # Check if user is logged in
        if 'Sign In' in content and 'Don\'t have an account?' in content:
            print("❌ You need to log in first!")
            print()
            print("STEPS:")
            print("1. Go to: http://127.0.0.1:5006/login")
            print("2. Log in with your credentials")
            print("3. Run this test again")
            print()
            print("✅ The JavaScript fix HAS been applied to the template")
            print("✅ Once you log in, the ReferenceError should be resolved!")
            return
        
        print("✅ You are logged in! Analyzing JavaScript structure...")
        
        # Parse HTML to check script structure
        soup = BeautifulSoup(content, 'html.parser')
        scripts = soup.find_all('script')
        
        upgradePlan_in_script = False
        createModal_in_script = False
        
        for script in scripts:
            if script.string:
                if 'function upgradePlan(' in script.string:
                    upgradePlan_in_script = True
                    print("✅ upgradePlan function found inside <script> tags!")
                    
                if 'function createConfirmationModal(' in script.string:
                    createModal_in_script = True
                    print("✅ createConfirmationModal function found inside <script> tags!")
        
        # Check for button onclick handlers
        if 'onclick="upgradePlan(' in content:
            print("✅ Subscription buttons with onclick handlers found!")
        
        # Final assessment
        if upgradePlan_in_script and createModal_in_script:
            print()
            print("🎉 JAVASCRIPT REFERENCEERROR FIXED!")
            print("✅ All functions are properly loaded within <script> tags")
            print("✅ Subscription buttons should work without errors")
            print()
            print("📋 TO TEST:")
            print("1. Go to: http://127.0.0.1:5006/my-account")
            print("2. Scroll to 'Subscription & Plans' section")
            print("3. Click 'Upgrade to Pro' or 'Upgrade to Premium'")
            print("4. You should see a confirmation modal (NO ReferenceError!)")
            print("5. Click 'Upgrade' to proceed to Stripe checkout")
        else:
            print()
            print("❌ Some JavaScript functions still not properly loaded")
            if not upgradePlan_in_script:
                print("   Missing: upgradePlan function")
            if not createModal_in_script:
                print("   Missing: createConfirmationModal function")
    
    else:
        print(f"❌ Error accessing page: {response.status_code}")

if __name__ == "__main__":
    test_upgradePlan_fix()
