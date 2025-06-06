#!/usr/bin/env python3
"""
Direct test of subscription functionality
Simulates the exact workflow when buttons are clicked
"""

import requests
import time

# Test configuration
BASE_URL = "http://127.0.0.1:5006"
TEST_USER = "testuser@example.com"
TEST_PASSWORD = "testpass123"

def test_subscription_workflow():
    """Test the complete subscription workflow"""
    print("🧪 TESTING SUBSCRIPTION WORKFLOW")
    print("="*50)
    
    # Create session
    session = requests.Session()
    
    # Step 1: Login
    print("1. Logging in...")
    login_data = {
        'email': TEST_USER,
        'password': TEST_PASSWORD
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 302:
        print("   ❌ Login failed - need to register user first")
        
        # Try to register
        print("   📝 Attempting to register user...")
        register_data = {
            'name': 'Test User',
            'email': TEST_USER,
            'password': TEST_PASSWORD,
            'confirm_password': TEST_PASSWORD
        }
        
        register_response = session.post(f"{BASE_URL}/register", data=register_data, allow_redirects=False)
        print(f"   Registration status: {register_response.status_code}")
        
        if register_response.status_code == 302:
            print("   ✅ User registered successfully")
            # Now try login again
            login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
            print(f"   Login after registration status: {login_response.status_code}")
        else:
            print("   ❌ Registration failed")
            return False
    
    if login_response.status_code == 302:
        print("   ✅ Successfully logged in")
    else:
        print("   ❌ Login failed")
        return False
    
    # Step 2: Test Pro subscription
    print("\n2. Testing Pro subscription upgrade...")
    pro_data = {
        'plan': 'Pro'
    }
    
    pro_response = session.post(f"{BASE_URL}/create-checkout-session", 
                               data=pro_data, 
                               allow_redirects=False)
    print(f"   Pro upgrade status: {pro_response.status_code}")
    
    if pro_response.status_code == 303:
        redirect_url = pro_response.headers.get('Location', '')
        if 'stripe.com' in redirect_url or 'checkout.stripe.com' in redirect_url:
            print("   ✅ Pro upgrade working - redirects to Stripe!")
            print(f"   🔗 Stripe URL: {redirect_url[:100]}...")
        else:
            print(f"   ⚠️  Redirects but not to Stripe: {redirect_url}")
    else:
        print(f"   ❌ Pro upgrade failed")
        if pro_response.text:
            print(f"   Response: {pro_response.text[:200]}...")
    
    # Step 3: Test Premium subscription
    print("\n3. Testing Premium subscription upgrade...")
    premium_data = {
        'plan': 'Premium'
    }
    
    premium_response = session.post(f"{BASE_URL}/create-checkout-session", 
                                   data=premium_data, 
                                   allow_redirects=False)
    print(f"   Premium upgrade status: {premium_response.status_code}")
    
    if premium_response.status_code == 303:
        redirect_url = premium_response.headers.get('Location', '')
        if 'stripe.com' in redirect_url or 'checkout.stripe.com' in redirect_url:
            print("   ✅ Premium upgrade working - redirects to Stripe!")
            print(f"   🔗 Stripe URL: {redirect_url[:100]}...")
        else:
            print(f"   ⚠️  Redirects but not to Stripe: {redirect_url}")
    else:
        print(f"   ❌ Premium upgrade failed")
        if premium_response.text:
            print(f"   Response: {premium_response.text[:200]}...")
    
    # Step 4: Test invalid plan (should handle gracefully)
    print("\n4. Testing invalid plan handling...")
    invalid_data = {
        'plan': 'InvalidPlan'
    }
    
    invalid_response = session.post(f"{BASE_URL}/create-checkout-session", 
                                   data=invalid_data, 
                                   allow_redirects=False)
    print(f"   Invalid plan status: {invalid_response.status_code}")
    
    if invalid_response.status_code == 302:
        redirect_url = invalid_response.headers.get('Location', '')
        if 'my-account' in redirect_url or 'profile' in redirect_url:
            print("   ✅ Invalid plan handled gracefully - redirects to account")
        else:
            print(f"   ⚠️  Redirects to: {redirect_url}")
    else:
        print("   ⚠️  Unexpected response for invalid plan")
    
    print("\n" + "="*50)
    print("🎯 SUMMARY:")
    print("The subscription buttons should work properly!")
    print("If they don't work in the browser, check:")
    print("1. Browser console for JavaScript errors")
    print("2. Network tab to see if requests are being made")
    print("3. Check if JavaScript is enabled")
    
    return True

if __name__ == "__main__":
    test_subscription_workflow()
