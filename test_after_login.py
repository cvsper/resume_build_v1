#!/usr/bin/env python3
"""
Test script to verify subscription functionality after login
Run this AFTER you've logged in through the browser
"""

import requests
import json
from bs4 import BeautifulSoup

def test_subscription_flow():
    print("🧪 TESTING SUBSCRIPTION FLOW AFTER LOGIN")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5006"
    
    # Test 1: Check if we can access the my-account page
    print("1. Testing My Account page access...")
    try:
        response = requests.get(f"{base_url}/my-account")
        if response.status_code == 200:
            print("   ✅ My Account page accessible")
            
            # Check if subscription buttons are present
            soup = BeautifulSoup(response.text, 'html.parser')
            pro_button = soup.find('button', onclick="upgradePlan('Pro')")
            premium_button = soup.find('button', onclick="upgradePlan('Premium')")
            
            if pro_button:
                print("   ✅ Pro subscription button found")
            else:
                print("   ❌ Pro subscription button NOT found")
                
            if premium_button:
                print("   ✅ Premium subscription button found")
            else:
                print("   ❌ Premium subscription button NOT found")
                
        else:
            print(f"   ❌ My Account not accessible (Status: {response.status_code})")
            if response.status_code == 302:
                print("   💡 You're being redirected - please log in first!")
                return False
    except Exception as e:
        print(f"   ❌ Error accessing My Account: {e}")
        return False
    
    print("\n2. Testing subscription endpoint availability...")
    try:
        # Test with a simple GET to see if endpoint exists
        response = requests.get(f"{base_url}/create-checkout-session")
        if response.status_code == 405:  # Method Not Allowed is expected for GET
            print("   ✅ Subscription endpoint exists (needs POST)")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing endpoint: {e}")
    
    print("\n3. JavaScript Function Check...")
    try:
        response = requests.get(f"{base_url}/my-account")
        if "function upgradePlan" in response.text:
            print("   ✅ upgradePlan JavaScript function found")
        else:
            print("   ❌ upgradePlan JavaScript function NOT found")
    except Exception as e:
        print(f"   ❌ Error checking JavaScript: {e}")
    
    print("\n📋 NEXT STEPS:")
    print("1. Make sure you're logged in at: http://127.0.0.1:5006/login")
    print("2. Go to My Account: http://127.0.0.1:5006/my-account")
    print("3. Click on 'Upgrade to Pro' or 'Upgrade to Premium' buttons")
    print("4. You should see a confirmation dialog")
    print("5. After confirming, you should be redirected to Stripe checkout")
    
    return True

def test_stripe_keys():
    print("\n🔑 CHECKING STRIPE CONFIGURATION")
    print("-" * 30)
    
    try:
        import stripe
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        stripe_publishable = os.getenv('STRIPE_PUBLISHABLE_KEY')
        stripe_secret = os.getenv('STRIPE_SECRET_KEY')
        
        if stripe_publishable and stripe_publishable.startswith('pk_'):
            print("   ✅ Stripe Publishable Key configured")
        else:
            print("   ❌ Stripe Publishable Key missing or invalid")
            
        if stripe_secret and stripe_secret.startswith('sk_'):
            print("   ✅ Stripe Secret Key configured")
        else:
            print("   ❌ Stripe Secret Key missing or invalid")
            
        # Test Stripe API connection
        stripe.api_key = stripe_secret
        try:
            stripe.Account.retrieve()
            print("   ✅ Stripe API connection successful")
        except Exception as e:
            print(f"   ❌ Stripe API connection failed: {e}")
            
    except ImportError:
        print("   ❌ Stripe library not installed")
    except Exception as e:
        print(f"   ❌ Error checking Stripe config: {e}")

if __name__ == "__main__":
    test_subscription_flow()
    test_stripe_keys()
    
    print("\n" + "=" * 50)
    print("🚀 READY TO TEST!")
    print("Open http://127.0.0.1:5006/login in your browser")
    print("Log in, then test the subscription buttons!")
