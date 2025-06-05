#!/usr/bin/env python3
"""
Simple test to verify subscription buttons work
"""

import requests
import time

def test_button_functionality():
    print("🔧 SUBSCRIPTION BUTTON DIAGNOSTIC")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:5006"
    
    # Test 1: Check if My Account page loads
    print("1. Testing My Account page...")
    try:
        response = requests.get(f"{base_url}/my-account")
        if response.status_code == 200:
            print("   ✅ My Account page loads successfully")
            
            # Check for subscription buttons
            page_content = response.text
            if 'onclick="upgradePlan(\'Pro\')"' in page_content:
                print("   ✅ Pro upgrade button found")
            else:
                print("   ❌ Pro upgrade button NOT found")
                
            if 'onclick="upgradePlan(\'Premium\')"' in page_content:
                print("   ✅ Premium upgrade button found")
            else:
                print("   ❌ Premium upgrade button NOT found")
                
            if 'function upgradePlan(' in page_content:
                print("   ✅ upgradePlan JavaScript function found")
            else:
                print("   ❌ upgradePlan JavaScript function NOT found")
                
            if 'function createConfirmationModal(' in page_content:
                print("   ✅ createConfirmationModal function found")
            else:
                print("   ❌ createConfirmationModal function NOT found")
                
        else:
            print(f"   ❌ Page failed to load (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Check checkout session endpoint
    print("\n2. Testing checkout session endpoint...")
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # First get the my-account page to get any session cookies
        session.get(f"{base_url}/my-account")
        
        # Now test the checkout endpoint with POST
        response = session.post(f"{base_url}/create-checkout-session", 
                               data={'plan': 'Pro'})
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            if 'checkout.stripe.com' in redirect_url:
                print("   ✅ Checkout endpoint works - redirects to Stripe!")
                print(f"   🔗 Redirect URL: {redirect_url[:50]}...")
            else:
                print(f"   ⚠️  Redirects to: {redirect_url}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Error testing checkout: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 MANUAL TEST STEPS:")
    print("1. Open: http://127.0.0.1:5006/my-account")
    print("2. Look for 'Upgrade to Pro' and 'Upgrade to Premium' buttons")
    print("3. Click on either button")
    print("4. You should see a confirmation dialog")
    print("5. Click 'Upgrade' in the dialog")
    print("6. You should be redirected to Stripe checkout")
    print("\n💡 If buttons don't work, open browser developer tools (F12)")
    print("   and check for JavaScript errors in the Console tab")

if __name__ == "__main__":
    test_button_functionality()
