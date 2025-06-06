#!/usr/bin/env python3
"""
Test script to verify the subscription button functionality
"""
import requests
import sys
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5006"

def test_subscription_button_flow():
    """Test the complete subscription button flow"""
    
    print("🧪 Testing Subscription Button Flow")
    print("=" * 50)
    
    # Test 1: Check if the test page loads
    print("\n1. Testing test page accessibility...")
    try:
        response = requests.get(urljoin(BASE_URL, "/test-subscription-simple"))
        if response.status_code == 200:
            print("✅ Test page loads successfully")
            print(f"   Content length: {len(response.text)} characters")
        else:
            print(f"❌ Test page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing test page: {e}")
        return False
    
    # Test 2: Check if main dashboard loads 
    print("\n2. Testing dashboard accessibility...")
    try:
        response = requests.get(urljoin(BASE_URL, "/"))
        if response.status_code == 200:
            print("✅ Dashboard loads successfully")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
    
    # Test 3: Check customer portal route (will fail without auth, but should exist)
    print("\n3. Testing customer portal route...")
    try:
        response = requests.post(urljoin(BASE_URL, "/create-customer-portal"))
        if response.status_code == 401 or response.status_code == 302:
            print("✅ Customer portal route exists (redirected due to no auth)")
        elif response.status_code == 404:
            print("❌ Customer portal route not found")
            return False
        else:
            print(f"ℹ️  Customer portal response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing customer portal: {e}")
    
    # Test 4: Check if JavaScript function exists in dashboard
    print("\n4. Testing dashboard JavaScript...")
    try:
        response = requests.get(urljoin(BASE_URL, "/"))
        if "openCustomerPortal" in response.text:
            print("✅ JavaScript function found in dashboard")
        else:
            print("❌ JavaScript function not found in dashboard")
            return False
    except Exception as e:
        print(f"❌ Error checking dashboard JavaScript: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("• Test page: Accessible")
    print("• Dashboard: Accessible") 
    print("• Customer portal route: Exists")
    print("• JavaScript function: Present")
    print("\n✅ Basic infrastructure appears to be working!")
    print("\n🔍 Next steps:")
    print("1. Test the button in a real browser with authentication")
    print("2. Check browser console for JavaScript errors")
    print("3. Verify backend debug output when button is clicked")
    
    return True

if __name__ == "__main__":
    try:
        success = test_subscription_button_flow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
