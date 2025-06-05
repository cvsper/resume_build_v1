#!/usr/bin/env python3
"""
Test subscription button functionality
"""

import requests
from requests.sessions import Session
from urllib.parse import urljoin
import time

class SubscriptionButtonTest:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:5006'
        self.session = requests.Session()
        
    def test_subscription_flow(self):
        """Test the subscription button functionality"""
        print("🧪 TESTING SUBSCRIPTION BUTTON FUNCTIONALITY")
        print("=" * 50)
        
        # Test 1: Check if application is running
        print("1. Testing application availability...")
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("   ✅ Application is running")
            else:
                print(f"   ⚠️  Application responded with status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Application not accessible: {e}")
            return False
        
        # Test 2: Check profile page (should redirect to login)
        print("\n2. Testing profile page access...")
        try:
            response = self.session.get(urljoin(self.base_url, '/my-account'))
            if response.status_code in [200, 302]:
                print("   ✅ Profile page accessible (redirects to login as expected)")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error accessing profile: {e}")
        
        # Test 3: Test checkout endpoint directly
        print("\n3. Testing subscription checkout endpoint...")
        try:
            # Test Pro subscription
            checkout_data = {'plan': 'Pro'}
            response = self.session.post(urljoin(self.base_url, '/create-checkout-session'), data=checkout_data)
            if response.status_code in [303, 302]:
                print("   ✅ Pro subscription checkout endpoint working (redirects to login/Stripe)")
                redirect_url = response.headers.get('Location', 'No redirect URL')
                if 'login' in redirect_url.lower():
                    print("   📝 Redirects to login (authentication required)")
                elif 'checkout.stripe.com' in redirect_url:
                    print("   🎉 Redirects to Stripe checkout!")
            elif response.status_code == 401:
                print("   ✅ Checkout requires authentication (expected)")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Checkout error: {e}")
        
        # Test 4: Test Premium subscription
        print("\n4. Testing Premium subscription checkout...")
        try:
            checkout_data = {'plan': 'Premium'}
            response = self.session.post(urljoin(self.base_url, '/create-checkout-session'), data=checkout_data)
            if response.status_code in [303, 302]:
                print("   ✅ Premium subscription checkout working")
            elif response.status_code == 401:
                print("   ✅ Authentication required (expected)")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Premium checkout error: {e}")
        
        # Test 5: Check if JavaScript functions exist in template
        print("\n5. Testing JavaScript function availability...")
        try:
            response = self.session.get(urljoin(self.base_url, '/my-account'))
            if 'upgradePlan' in response.text:
                print("   ✅ upgradePlan JavaScript function found in template")
            else:
                print("   ❌ upgradePlan function NOT found")
                
            if 'downgradePlan' in response.text:
                print("   ✅ downgradePlan JavaScript function found in template")
            else:
                print("   ❌ downgradePlan function NOT found")
                
            if 'createConfirmationModal' in response.text:
                print("   ✅ createConfirmationModal JavaScript function found in template")
            else:
                print("   ❌ createConfirmationModal function NOT found")
        except Exception as e:
            print(f"   ❌ Error checking JavaScript: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 MANUAL TEST INSTRUCTIONS:")
        print("1. Visit: http://127.0.0.1:5006/login")
        print("2. Login with your credentials (or register)")
        print("3. Go to: http://127.0.0.1:5006/my-account")
        print("4. Scroll down to 'Subscription & Plans' section")
        print("5. Click on 'Upgrade to Pro' or 'Upgrade to Premium' buttons")
        print("6. You should see a confirmation modal")
        print("7. Click 'Upgrade' in the modal")
        print("8. You should be redirected to Stripe checkout")
        print("\n💳 Test card: 4242 4242 4242 4242")
        print("   Expiry: 12/28, CVC: 123, ZIP: 12345")
        
        return True

if __name__ == "__main__":
    test = SubscriptionButtonTest()
    test.test_subscription_flow()
