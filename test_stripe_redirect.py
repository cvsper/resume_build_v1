#!/usr/bin/env python3
"""
Test script to verify the Stripe Customer Portal redirect is working correctly
"""

import requests
import os
from urllib.parse import urlparse

def test_stripe_redirect():
    """Test that the subscription button redirects directly to Stripe Customer Portal"""
    print("🧪 Testing Direct Stripe Customer Portal Redirect")
    print("=" * 55)
    
    base_url = "http://127.0.0.1:5006"
    
    # Check if Flask app is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print("❌ Flask app not accessible")
            return False
    except requests.RequestException:
        print("❌ Flask app not running on http://127.0.0.1:5006")
        return False
    
    print("✅ Flask app is running")
    
    # Test the customer portal route
    print("\n🔍 Testing /create-customer-portal route...")
    
    try:
        # Test the route directly (will fail without authentication, but we can see the response)
        response = requests.post(f"{base_url}/create-customer-portal", allow_redirects=False)
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            if 'billing.stripe.com' in redirect_url:
                print("✅ Route correctly redirects to Stripe Customer Portal")
                print(f"   → Redirect URL: {redirect_url}")
            else:
                print(f"⚠️  Route redirects to: {redirect_url}")
                print("   (This might be a login redirect, which is expected)")
        elif response.status_code == 401:
            print("⚠️  Route requires authentication (expected behavior)")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Error testing route: {e}")
    
    # Check the backend code changes
    print("\n🔧 Verifying backend route configuration...")
    
    app_path = '/Users/sevs/Documents/Programs/webapps/resume_builder/app.py'
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            app_content = f.read()
        
        # Check return URL is set to dashboard
        if "return_url=url_for('dashboard', _external=True)" in app_content:
            print("✅ Return URL set to dashboard (instead of my_account)")
        elif "return_url=url_for('my_account', _external=True)" in app_content:
            print("❌ Return URL still set to my_account")
        else:
            print("⚠️  Return URL configuration not found")
        
        # Check error handling redirects to dashboard
        if "return redirect(url_for('dashboard'))" in app_content:
            print("✅ Error handling redirects to dashboard")
        elif "return redirect(url_for('my_account'))" in app_content:
            print("❌ Error handling still redirects to my_account")
        
        # Check direct Stripe redirect
        if "return redirect(portal_session.url, code=303)" in app_content:
            print("✅ Direct redirect to Stripe Customer Portal configured")
        else:
            print("❌ Direct Stripe redirect not found")
    
    print("\n🎯 Expected Behavior:")
    print("   1. User clicks 'Subscription' button in sidebar")
    print("   2. JavaScript confirms and POSTs to /create-customer-portal")
    print("   3. Flask route creates/finds Stripe customer")
    print("   4. Flask route creates Stripe Customer Portal session")
    print("   5. Flask route redirects DIRECTLY to Stripe portal URL")
    print("   6. User manages subscription in Stripe portal")
    print("   7. When done, Stripe redirects back to dashboard")
    
    print("\n📝 If you're still seeing My Account page:")
    print("   • Clear your browser cache")
    print("   • Try in an incognito/private window")
    print("   • Check browser console for JavaScript errors")
    print("   • Ensure you're logged in when testing")
    
    return True

if __name__ == "__main__":
    test_stripe_redirect()
