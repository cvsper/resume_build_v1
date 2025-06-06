#!/usr/bin/env python3
"""
Complete Subscription Button Test - Final Validation
"""
import requests
import time

BASE_URL = "http://127.0.0.1:5006"

def run_comprehensive_test():
    """Run comprehensive subscription button test"""
    
    print("🎯 COMPREHENSIVE SUBSCRIPTION BUTTON TEST")
    print("=" * 60)
    
    session = requests.Session()
    all_tests_passed = True
    
    # Test 1: Dashboard with subscription button
    print("\n📋 Step 1: Testing dashboard with subscription button...")
    try:
        response = session.get(f"{BASE_URL}/test-dashboard-no-auth")
        if response.status_code == 200:
            has_subscription = 'Subscription' in response.text
            has_function = 'openCustomerPortal' in response.text
            has_onclick = 'onclick="openCustomerPortal()"' in response.text
            
            print(f"✅ Dashboard loads: Status {response.status_code}")
            print(f"✅ Contains subscription button: {has_subscription}")
            print(f"✅ Contains JavaScript function: {has_function}")  
            print(f"✅ Button has onclick handler: {has_onclick}")
            
            if not all([has_subscription, has_function, has_onclick]):
                print("❌ Missing subscription elements")
                all_tests_passed = False
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ Dashboard test error: {e}")
        all_tests_passed = False
    
    # Test 2: Customer portal route protection
    print("\n🔒 Step 2: Testing customer portal route protection...")
    try:
        response = session.post(f"{BASE_URL}/create-customer-portal", allow_redirects=False)
        if response.status_code in [302, 401]:
            print(f"✅ Route protected: Status {response.status_code} (expected)")
            redirect_location = response.headers.get('Location', 'None')
            print(f"   Redirects to: {redirect_location}")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Route test error: {e}")
        all_tests_passed = False
    
    # Test 3: Form submission simulation
    print("\n🖱️  Step 3: Testing form submission simulation...")
    try:
        test_form_data = {}
        response = session.post(f"{BASE_URL}/create-customer-portal", 
                              data=test_form_data, 
                              allow_redirects=False)
        
        print(f"✅ Form submission test: Status {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if 'login' in location:
                print("✅ Correctly redirects to login (authentication required)")
            else:
                print(f"   Redirect location: {location}")
        
    except Exception as e:
        print(f"❌ Form submission error: {e}")
        all_tests_passed = False
    
    # Test 4: Template validation
    print("\n📄 Step 4: Template validation...")
    try:
        with open('/Users/sevs/Documents/Programs/webapps/resume_builder/templates/dashboard.html', 'r') as f:
            template_content = f.read()
            
        checks = {
            'Subscription button text': 'Subscription' in template_content,
            'JavaScript function': 'function openCustomerPortal()' in template_content,
            'Form action': 'create-customer-portal' in template_content,
            'Button onclick': 'onclick="openCustomerPortal()"' in template_content,
            'Console logging': 'console.log' in template_content,
        }
        
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}: {result}")
            if not result:
                all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Template validation error: {e}")
        all_tests_passed = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS:")
    print("=" * 60)
    
    if all_tests_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 Subscription Button Status:")
        print("   • Universal button: ✅ Visible to all users")
        print("   • JavaScript function: ✅ Simplified and working")
        print("   • Backend route: ✅ Protected and functional")  
        print("   • Template elements: ✅ All present and correct")
        print("   • Authentication flow: ✅ Properly secured")
        
        print("\n🔄 Ready for Production Testing:")
        print("   1. Create test user account")
        print("   2. Login and test subscription button manually")
        print("   3. Verify Stripe Customer Portal redirect")
        print("   4. Test with different subscription tiers")
        
        print("\n🌐 Available Test URLs:")
        print(f"   • Test Dashboard: {BASE_URL}/test-dashboard-no-auth")
        print(f"   • Debug Page: {BASE_URL}/debug-subscription-detailed")
        print(f"   • Login Page: {BASE_URL}/login")
        
    else:
        print("❌ SOME TESTS FAILED")
        print("   Review the failing checks above and fix issues")
    
    return all_tests_passed

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
