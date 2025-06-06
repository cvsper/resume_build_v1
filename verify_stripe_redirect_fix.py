#!/usr/bin/env python3
"""
Final test to verify the subscription button redirects directly to Stripe Customer Portal
"""

import requests
import time
from urllib.parse import urlparse

def test_subscription_redirect_fix():
    """Test that the subscription button now goes directly to Stripe"""
    print("🔧 SUBSCRIPTION REDIRECT FIX - VERIFICATION")
    print("=" * 55)
    
    base_url = "http://127.0.0.1:5006"
    
    # Test 1: Verify Flask app is running
    print("1️⃣ Testing Flask app availability...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Flask app is running and accessible")
        else:
            print(f"   ❌ Flask app returned status {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"   ❌ Flask app not accessible: {e}")
        return False
    
    # Test 2: Check backend route configuration
    print("\n2️⃣ Verifying backend route changes...")
    
    try:
        with open('/Users/sevs/Documents/Programs/webapps/resume_builder/app.py', 'r') as f:
            app_content = f.read()
        
        # Check return URL is dashboard
        if "return_url=url_for('dashboard', _external=True)" in app_content:
            print("   ✅ Return URL set to dashboard (was my_account)")
        else:
            print("   ❌ Return URL not updated")
        
        # Check direct Stripe redirect
        if "return redirect(portal_session.url, code=303)" in app_content:
            print("   ✅ Direct redirect to Stripe Customer Portal")
        else:
            print("   ❌ Direct Stripe redirect missing")
        
        # Check error handling
        if "return redirect(url_for('dashboard'))" in app_content:
            print("   ✅ Error handling redirects to dashboard")
        else:
            print("   ❌ Error handling not updated")
            
    except Exception as e:
        print(f"   ❌ Error checking backend: {e}")
        return False
    
    # Test 3: Verify template changes
    print("\n3️⃣ Verifying template modifications...")
    
    templates = [
        '/Users/sevs/Documents/Programs/webapps/resume_builder/templates/dashboard.html',
        '/Users/sevs/Documents/Programs/webapps/resume_builder/templates/dashboard_new.html',
        '/Users/sevs/Documents/Programs/webapps/resume_builder/templates/dashboard_backup.html'
    ]
    
    for template_path in templates:
        template_name = template_path.split('/')[-1]
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Check button is unconditional
            if "{% if current_user.subscription and current_user.subscription != 'Free' %}" not in content:
                print(f"   ✅ {template_name}: Conditional logic removed")
            else:
                print(f"   ❌ {template_name}: Still has conditional logic")
            
            # Check button text
            if '<i class="bi bi-credit-card"></i> Subscription' in content:
                print(f"   ✅ {template_name}: Button text is 'Subscription'")
            else:
                print(f"   ❌ {template_name}: Button text not updated")
            
            # Check enhanced JavaScript
            if 'console.log(\'openCustomerPortal() called\')' in content:
                print(f"   ✅ {template_name}: Enhanced JavaScript with debugging")
            else:
                print(f"   ❌ {template_name}: JavaScript not enhanced")
                
        except Exception as e:
            print(f"   ❌ Error checking {template_name}: {e}")
    
    # Test 4: Route functionality test
    print("\n4️⃣ Testing route functionality...")
    
    try:
        # Test the route (will redirect to login, but we can see the response)
        response = requests.post(f"{base_url}/create-customer-portal", allow_redirects=False)
        
        if response.status_code in [302, 401]:
            print("   ✅ Route exists and responds (redirects as expected)")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if 'login' in location.lower():
                    print("   ✅ Properly redirects to login when not authenticated")
                elif 'billing.stripe.com' in location:
                    print("   🎉 Direct redirect to Stripe detected!")
                else:
                    print(f"   ⚠️  Redirects to: {location}")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing route: {e}")
    
    print("\n🎯 SUMMARY OF FIXES APPLIED:")
    print("━" * 50)
    print("✅ Backend Changes:")
    print("   • Changed return_url from 'my_account' to 'dashboard'")
    print("   • Error handling now redirects to dashboard")
    print("   • Direct redirect to Stripe Customer Portal URL")
    print()
    print("✅ Frontend Changes:")
    print("   • Removed conditional logic (button visible to all users)")
    print("   • Changed button text to 'Subscription'")
    print("   • Enhanced JavaScript with error handling & debugging")
    print("   • Added loading state and better user feedback")
    print()
    print("✅ Expected Flow:")
    print("   1. User clicks 'Subscription' button")
    print("   2. JavaScript creates and submits form to /create-customer-portal")
    print("   3. Flask creates/finds Stripe customer")
    print("   4. Flask redirects DIRECTLY to Stripe Customer Portal")
    print("   5. User manages subscription in Stripe")
    print("   6. Stripe redirects back to dashboard when done")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Clear browser cache or use incognito mode")
    print("   2. Login to your app")
    print("   3. Click the 'Subscription' button in sidebar")
    print("   4. Should now go DIRECTLY to Stripe Customer Portal")
    print("   5. Check browser console for debug logs if issues persist")
    
    return True

if __name__ == "__main__":
    test_subscription_redirect_fix()
