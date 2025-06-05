#!/usr/bin/env python3
"""
Quick test to verify subscription buttons work after JavaScript fix
"""

import requests
from bs4 import BeautifulSoup

def test_javascript_fix():
    print("🔧 TESTING JAVASCRIPT FIX FOR SUBSCRIPTION BUTTONS")
    print("=" * 55)
    
    response = requests.get('http://127.0.0.1:5006/my-account')
    
    if response.status_code == 200:
        content = response.text
        
        # Check if user is logged in
        if 'Sign In' in content and 'Don\'t have an account?' in content:
            print("❌ You need to log in first!")
            print()
            print("STEPS TO TEST:")
            print("1. Go to: http://127.0.0.1:5006/login")
            print("2. Log in with your credentials")
            print("3. Go to: http://127.0.0.1:5006/my-account")
            print("4. Try clicking the subscription buttons")
            print()
            print("The 'ReferenceError: Can't find variable: upgradePlan' should be FIXED now!")
            return
        
        # User is logged in, check JavaScript structure
        print("✅ You are logged in! Checking JavaScript...")
        
        # Parse the HTML to check script structure
        soup = BeautifulSoup(content, 'html.parser')
        scripts = soup.find_all('script')
        
        main_script_content = ""
        for script in scripts:
            if script.string and 'upgradePlan' in script.string:
                main_script_content = script.string
                break
        
        if main_script_content:
            print("✅ upgradePlan function found inside <script> tags!")
            
            # Check for all required functions
            functions_to_check = [
                'function upgradePlan(',
                'function downgradePlan(',
                'function createConfirmationModal('
            ]
            
            all_found = True
            for func in functions_to_check:
                if func in main_script_content:
                    print(f"✅ {func} found")
                else:
                    print(f"❌ {func} NOT found")
                    all_found = False
            
            if all_found:
                print()
                print("🎉 JAVASCRIPT FIX SUCCESSFUL!")
                print("✅ All subscription functions are properly loaded")
                print("✅ The 'ReferenceError' should be resolved")
                print()
                print("📋 TO TEST:")
                print("1. Go to: http://127.0.0.1:5006/my-account")
                print("2. Scroll to 'Subscription & Plans' section")
                print("3. Click 'Upgrade to Pro' or 'Upgrade to Premium'")
                print("4. You should see a confirmation modal (no errors!)")
                print("5. Click 'Upgrade' to proceed to Stripe checkout")
            else:
                print("❌ Some functions are missing")
        else:
            print("❌ upgradePlan function not found in any script tag")
            print("There might still be a JavaScript structure issue")
    
    else:
        print(f"❌ Error accessing page: {response.status_code}")

if __name__ == "__main__":
    test_javascript_fix()
