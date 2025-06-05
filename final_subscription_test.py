#!/usr/bin/env python3
"""
Final verification script - run this AFTER logging in through the browser
"""

import requests
import time

def test_subscription_after_login():
    print("🔐 SUBSCRIPTION BUTTON VERIFICATION")
    print("=" * 45)
    print("This test checks if subscription buttons work after login")
    print()
    
    # Test 1: Check authentication status
    print("1. Testing authentication status...")
    session = requests.Session()
    response = session.get('http://127.0.0.1:5006/my-account')
    
    if response.status_code == 200:
        content = response.text
        
        # Check if it's the login page (means not authenticated)
        if 'Sign In' in content and 'Don\'t have an account?' in content:
            print("   ❌ You are NOT logged in")
            print("   💡 SOLUTION: Go to http://127.0.0.1:5006/login and log in first")
            print()
            print("🚨 IMPORTANT STEPS:")
            print("1. Open http://127.0.0.1:5006/login in your browser")
            print("2. Enter your email and password")
            print("3. Click 'Sign In'")
            print("4. Then go to http://127.0.0.1:5006/my-account")
            print("5. Look for subscription buttons")
            return False
            
        # Check if it's the actual profile page
        elif 'My Account' in content or 'Profile Settings' in content:
            print("   ✅ You are logged in!")
            
            # Test 2: Check for subscription components
            print("\n2. Checking subscription components...")
            
            components = {
                'Subscription section': 'subscription-section' in content,
                'Subscription heading': 'Subscription & Plans' in content,
                'Pro button': 'upgradePlan(\'Pro\')' in content,
                'Premium button': 'upgradePlan(\'Premium\')' in content,
                'upgradePlan function': 'function upgradePlan(' in content,
                'Modal function': 'function createConfirmationModal(' in content
            }
            
            all_present = True
            for component, present in components.items():
                status = "✅" if present else "❌"
                print(f"   {status} {component}")
                if not present:
                    all_present = False
            
            if all_present:
                print("\n🎉 SUCCESS! All subscription components are present!")
                print("   The subscription buttons should work perfectly now.")
                print()
                print("📋 TO TEST THE BUTTONS:")
                print("1. Go to: http://127.0.0.1:5006/my-account")
                print("2. Scroll down to 'Subscription & Plans' section")
                print("3. Click 'Upgrade to Pro' or 'Upgrade to Premium'")
                print("4. You should see a confirmation dialog")
                print("5. Click 'Upgrade' to proceed to Stripe checkout")
                
                # Test 3: Test the checkout endpoint
                print("\n3. Testing checkout endpoint...")
                checkout_response = session.post(
                    'http://127.0.0.1:5006/create-checkout-session',
                    data={'plan': 'Pro'}
                )
                
                if checkout_response.status_code == 303:
                    redirect_url = checkout_response.headers.get('Location', '')
                    if 'checkout.stripe.com' in redirect_url:
                        print("   ✅ Checkout endpoint works - would redirect to Stripe!")
                    else:
                        print(f"   ⚠️  Redirects to: {redirect_url}")
                elif checkout_response.status_code == 302:
                    print("   ⚠️  Checkout redirected (might need CSRF token)")
                else:
                    print(f"   ❌ Unexpected checkout response: {checkout_response.status_code}")
                
                return True
            else:
                print("\n❌ Some subscription components are missing.")
                print("   There might be a template error.")
                return False
        else:
            print("   ❌ Unknown page content")
            print(f"   Content preview: {content[:100]}...")
            return False
    else:
        print(f"   ❌ Error accessing my-account: {response.status_code}")
        return False

def create_test_user_guide():
    print("\n" + "=" * 60)
    print("🎯 COMPLETE TESTING GUIDE")
    print("=" * 60)
    print()
    print("STEP 1: LOGIN")
    print("• Go to: http://127.0.0.1:5006/login")
    print("• If you don't have an account, go to: http://127.0.0.1:5006/register")
    print("• Create account with any email/password")
    print()
    print("STEP 2: ACCESS MY ACCOUNT")
    print("• Go to: http://127.0.0.1:5006/my-account")
    print("• You should see your profile page with subscription options")
    print()
    print("STEP 3: TEST SUBSCRIPTION BUTTONS")
    print("• Scroll to 'Subscription & Plans' section")
    print("• Click 'Upgrade to Pro' ($9.99/month)")
    print("• Click 'Upgrade to Premium' ($19.99/month)")
    print("• Confirm in the dialog that appears")
    print("• You should be redirected to Stripe checkout")
    print()
    print("STEP 4: VERIFICATION")
    print("• Run this script again after logging in")
    print("• It should show all components as ✅")
    print()
    print("🔧 TROUBLESHOOTING:")
    print("• If buttons don't respond: Check browser console (F12) for errors")
    print("• If no subscription section: Clear browser cache and refresh")
    print("• If redirected to login: Your session expired, log in again")

if __name__ == "__main__":
    success = test_subscription_after_login()
    if not success:
        create_test_user_guide()
    
    print(f"\n{'🎉 READY TO TEST!' if success else '⏳ LOGIN REQUIRED'}")
    print("App running at: http://127.0.0.1:5006")
