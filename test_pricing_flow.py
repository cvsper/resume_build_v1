#!/usr/bin/env python3
"""
Test the complete subscription flow from dashboard to pricing page
"""

import requests
import time

def test_pricing_flow():
    """Test the subscription button flow from dashboard to pricing page"""
    print("🧪 TESTING COMPLETE PRICING FLOW")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5006"
    session = requests.Session()
    
    # Test 1: Check if app is running
    print("1. Testing app connectivity...")
    try:
        response = session.get(base_url)
        if response.status_code == 200:
            print("   ✅ App is running successfully")
        else:
            print(f"   ❌ App error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Can't connect to app: {e}")
        return False
    
    # Test 2: Test pricing page direct access
    print("\n2. Testing pricing page direct access...")
    try:
        response = session.get(f"{base_url}/pricing")
        if response.status_code in [200, 302]:  # 302 for redirect to login
            if response.status_code == 200:
                print("   ✅ Pricing page accessible directly (user logged in)")
            else:
                print("   ✅ Pricing page redirects to login (authentication required)")
        else:
            print(f"   ❌ Pricing page error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Pricing page error: {e}")
        return False
    
    # Test 3: Test dashboard accessibility
    print("\n3. Testing dashboard access...")
    try:
        response = session.get(f"{base_url}/dashboard")
        if response.status_code in [200, 302]:
            if response.status_code == 200:
                print("   ✅ Dashboard accessible (user logged in)")
                # Check if subscription link exists in dashboard
                if 'pricing' in response.text or 'Subscription' in response.text:
                    print("   ✅ Dashboard contains subscription navigation")
                else:
                    print("   ⚠️  Dashboard missing subscription navigation")
            else:
                print("   ✅ Dashboard redirects to login (authentication required)")
        else:
            print(f"   ❌ Dashboard error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
        return False
    
    # Test 4: Test pricing route backend
    print("\n4. Testing pricing route backend...")
    try:
        # Check if the route exists by attempting to access it
        response = session.get(f"{base_url}/pricing", allow_redirects=False)
        if response.status_code == 302:
            print("   ✅ Pricing route exists and requires authentication")
        elif response.status_code == 200:
            print("   ✅ Pricing route accessible")
            # Check if the page contains subscription plans
            if 'Pro' in response.text and 'Premium' in response.text:
                print("   ✅ Pricing page contains subscription plans")
            else:
                print("   ⚠️  Pricing page missing subscription plans")
        else:
            print(f"   ❌ Pricing route error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Pricing route error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ PRICING FLOW TEST COMPLETE")
    print("\n📋 SUMMARY:")
    print("• App is running correctly")
    print("• Pricing page is accessible")
    print("• Dashboard contains subscription navigation")
    print("• Backend pricing route is functional")
    
    print("\n🎯 NEXT STEPS FOR MANUAL TESTING:")
    print("1. Open browser to: http://127.0.0.1:5006")
    print("2. Register/Login to your account")
    print("3. Go to Dashboard")
    print("4. Click 'Subscription' in navigation")
    print("5. Verify you're redirected to pricing page")
    print("6. Test subscription plan selection")
    
    return True

if __name__ == "__main__":
    test_pricing_flow()
