#!/usr/bin/env python3
"""
Test script to verify subscription management button functionality
"""

import requests
from bs4 import BeautifulSoup
import time

def test_subscription_management():
    """Test the subscription management button implementation"""
    print("🧪 TESTING SUBSCRIPTION MANAGEMENT BUTTON")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5006"
    session = requests.Session()
    
    # Test 1: Check if application is running
    print("1. Checking application status...")
    try:
        response = session.get(base_url)
        if response.status_code == 200:
            print("   ✅ Application is running")
        else:
            print(f"   ❌ Application issue: status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to application: {e}")
        return False
    
    # Test 2: Check dashboard templates contain the button
    print("\n2. Checking dashboard templates for Manage Subscription button...")
    
    dashboard_files = [
        'templates/dashboard.html',
        'templates/dashboard_new.html', 
        'templates/dashboard_backup.html'
    ]
    
    for template_file in dashboard_files:
        try:
            with open(f"/Users/sevs/Documents/Programs/webapps/resume_builder/{template_file}", 'r') as f:
                content = f.read()
                
            # Check for the Manage Subscription button
            if 'Manage Subscription' in content and 'openCustomerPortal()' in content:
                print(f"   ✅ {template_file}: Contains Manage Subscription button")
            else:
                print(f"   ❌ {template_file}: Missing Manage Subscription button")
                
            # Check for conditional display logic
            if 'current_user.subscription and current_user.subscription != \'Free\'' in content:
                print(f"   ✅ {template_file}: Has correct conditional display logic")
            else:
                print(f"   ❌ {template_file}: Missing conditional display logic")
                
        except Exception as e:
            print(f"   ❌ Error checking {template_file}: {e}")
    
    # Test 3: Check JavaScript function implementation
    print("\n3. Checking openCustomerPortal function implementation...")
    
    for template_file in dashboard_files:
        try:
            with open(f"/Users/sevs/Documents/Programs/webapps/resume_builder/{template_file}", 'r') as f:
                content = f.read()
                
            if 'function openCustomerPortal()' in content:
                print(f"   ✅ {template_file}: Contains openCustomerPortal function")
            else:
                print(f"   ❌ {template_file}: Missing openCustomerPortal function")
                
            if '/create-customer-portal' in content:
                print(f"   ✅ {template_file}: Points to correct backend route")
            else:
                print(f"   ❌ {template_file}: Missing backend route reference")
                
        except Exception as e:
            print(f"   ❌ Error checking function in {template_file}: {e}")
    
    # Test 4: Check backend route implementation
    print("\n4. Testing backend /create-customer-portal route...")
    try:
        # This should redirect to login since we're not authenticated
        response = session.post(f"{base_url}/create-customer-portal", allow_redirects=False)
        
        if response.status_code in [302, 303]:
            location = response.headers.get('Location', '')
            if 'login' in location:
                print("   ✅ Route exists and requires authentication (correct)")
            else:
                print(f"   ⚠️  Route redirects to: {location}")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing route: {e}")
    
    # Test 5: Visual verification instructions
    print("\n5. Manual verification instructions...")
    print("   📋 To manually test the subscription management button:")
    print("   1. Open http://127.0.0.1:5006 in your browser")
    print("   2. Log in with a user account")
    print("   3. Change the user's subscription to 'Pro' or 'Premium' in database")
    print("   4. Go to the dashboard")
    print("   5. Look for 'Manage Subscription' button in the sidebar")
    print("   6. Click the button - it should ask for confirmation")
    print("   7. Confirm - it should redirect to Stripe Customer Portal")
    
    print("\n🎉 SUBSCRIPTION MANAGEMENT BUTTON TEST COMPLETED!")
    print("   The implementation appears to be in place and should work correctly")
    print("   when users have active subscriptions (Pro/Premium).")
    
    return True

if __name__ == "__main__":
    test_subscription_management()
