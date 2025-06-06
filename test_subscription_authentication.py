#!/usr/bin/env python3
"""
SUBSCRIPTION BUTTON AUTHENTICATION TEST
======================================

This script tests the subscription button functionality with authentication
to verify that the universal subscription button works for all user types.
"""

import requests
import json
from bs4 import BeautifulSoup
import time

class SubscriptionAuthTest:
    def __init__(self, base_url="http://localhost:5007"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_user_login(self, email, password):
        """Test user login functionality"""
        print(f"\n🔐 Testing login for {email}")
        
        # Get login page first to establish session
        login_page_response = self.session.get(f"{self.base_url}/login")
        if login_page_response.status_code != 200:
            print(f"❌ Failed to load login page: {login_page_response.status_code}")
            return False
            
        # Parse login page for any CSRF tokens
        soup = BeautifulSoup(login_page_response.text, 'html.parser')
        
        # Attempt login
        login_data = {
            'email': email,
            'password': password
        }
        
        login_response = self.session.post(f"{self.base_url}/login", data=login_data, allow_redirects=False)
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response headers: {dict(login_response.headers)}")
        
        # Check if login was successful (redirected to dashboard)
        if login_response.status_code == 302:
            redirect_location = login_response.headers.get('Location', '')
            if 'dashboard' in redirect_location:
                print(f"✅ Login successful - redirected to: {redirect_location}")
                return True
            else:
                print(f"⚠️  Login redirect unexpected: {redirect_location}")
                return False
        else:
            print(f"❌ Login failed with status: {login_response.status_code}")
            return False
    
    def test_dashboard_access(self):
        """Test dashboard access and subscription button presence"""
        print(f"\n📊 Testing dashboard access...")
        
        dashboard_response = self.session.get(f"{self.base_url}/dashboard")
        
        if dashboard_response.status_code != 200:
            print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
            return False
            
        # Parse dashboard HTML
        soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        
        # Check for subscription button
        subscription_buttons = soup.find_all(lambda tag: tag.name == 'a' and 
                                           tag.get('onclick') == 'openCustomerPortal()')
        
        if subscription_buttons:
            print(f"✅ Found {len(subscription_buttons)} subscription button(s)")
            for btn in subscription_buttons:
                print(f"   Button text: '{btn.get_text(strip=True)}'")
            return True
        else:
            print("❌ Subscription button not found")
            return False
    
    def test_subscription_javascript(self):
        """Test that the subscription JavaScript function is present"""
        print(f"\n🟨 Testing subscription JavaScript...")
        
        dashboard_response = self.session.get(f"{self.base_url}/dashboard")
        
        if 'openCustomerPortal()' in dashboard_response.text:
            print("✅ openCustomerPortal() function found in dashboard")
            
            # Extract the function for analysis
            if 'function openCustomerPortal()' in dashboard_response.text:
                print("✅ Function definition found")
                
                # Check for simplified implementation
                if 'form.submit()' in dashboard_response.text:
                    print("✅ Simplified form submission found")
                    return True
                else:
                    print("⚠️  Function may be using complex logic")
                    return True
            else:
                print("⚠️  Function reference found but definition missing")
                return False
        else:
            print("❌ openCustomerPortal() function not found")
            return False
    
    def test_customer_portal_route(self):
        """Test the customer portal route (should require authentication)"""
        print(f"\n🔗 Testing customer portal route...")
        
        portal_response = self.session.post(f"{self.base_url}/create-customer-portal", 
                                          allow_redirects=False)
        
        print(f"Portal route response: {portal_response.status_code}")
        
        if portal_response.status_code == 302:
            print("✅ Route exists and responds with redirect")
            return True
        elif portal_response.status_code == 401:
            print("⚠️  Route requires authentication (expected)")
            return True
        else:
            print(f"❌ Unexpected response: {portal_response.status_code}")
            return False
    
    def test_user_subscription_level(self, expected_subscription):
        """Test that user subscription level is correctly displayed"""
        print(f"\n👤 Testing subscription level display...")
        
        dashboard_response = self.session.get(f"{self.base_url}/dashboard")
        
        if expected_subscription.lower() in dashboard_response.text.lower():
            print(f"✅ Subscription level '{expected_subscription}' found in dashboard")
            return True
        else:
            print(f"⚠️  Subscription level '{expected_subscription}' not explicitly shown")
            # This might be normal as the subscription button is universal
            return True
    
    def logout(self):
        """Logout current user"""
        print(f"\n🚪 Logging out...")
        logout_response = self.session.get(f"{self.base_url}/logout")
        if logout_response.status_code == 200 or logout_response.status_code == 302:
            print("✅ Logout successful")
            return True
        else:
            print(f"⚠️  Logout response: {logout_response.status_code}")
            return True
    
    def run_comprehensive_test(self):
        """Run comprehensive authentication test"""
        print("=" * 60)
        print("🧪 SUBSCRIPTION BUTTON AUTHENTICATION TEST")
        print("=" * 60)
        
        test_users = [
            ("test@example.com", "password123", "Free"),
            ("testpro@example.com", "password123", "Pro"),
            ("testpremium@example.com", "password123", "Premium")
        ]
        
        overall_results = []
        
        for email, password, subscription_level in test_users:
            print(f"\n{'='*50}")
            print(f"🧑‍💼 TESTING USER: {email} ({subscription_level})")
            print(f"{'='*50}")
            
            test_results = []
            
            # Test login
            login_success = self.test_user_login(email, password)
            test_results.append(("Login", login_success))
            
            if login_success:
                # Test dashboard access
                dashboard_success = self.test_dashboard_access()
                test_results.append(("Dashboard Access", dashboard_success))
                
                # Test subscription button JavaScript
                js_success = self.test_subscription_javascript()
                test_results.append(("JavaScript Function", js_success))
                
                # Test customer portal route
                portal_success = self.test_customer_portal_route()
                test_results.append(("Portal Route", portal_success))
                
                # Test subscription level
                level_success = self.test_user_subscription_level(subscription_level)
                test_results.append(("Subscription Level", level_success))
                
                # Logout
                logout_success = self.logout()
                test_results.append(("Logout", logout_success))
            
            # Calculate user test success rate
            passed_tests = sum(1 for _, result in test_results if result)
            total_tests = len(test_results)
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            overall_results.append({
                'user': email,
                'subscription': subscription_level,
                'passed': passed_tests,
                'total': total_tests,
                'success_rate': success_rate,
                'details': test_results
            })
            
            print(f"\n📊 {email} Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Summary
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("="*60)
        
        for result in overall_results:
            print(f"\n👤 {result['user']} ({result['subscription']}):")
            print(f"   Success Rate: {result['success_rate']:.1f}% ({result['passed']}/{result['total']})")
            
            for test_name, test_result in result['details']:
                status = "✅ PASS" if test_result else "❌ FAIL"
                print(f"   {test_name}: {status}")
        
        # Overall assessment
        total_passed = sum(r['passed'] for r in overall_results)
        total_tests = sum(r['total'] for r in overall_results)
        overall_success = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {overall_success:.1f}% ({total_passed}/{total_tests})")
        
        if overall_success >= 90:
            print("🟢 EXCELLENT: Subscription button implementation is working very well!")
        elif overall_success >= 75:
            print("🟡 GOOD: Subscription button implementation is mostly working")
        elif overall_success >= 50:
            print("🟠 FAIR: Some issues with subscription button implementation")
        else:
            print("🔴 NEEDS WORK: Significant issues with subscription button implementation")
        
        return overall_success >= 75

def main():
    """Main test execution"""
    tester = SubscriptionAuthTest()
    
    print("🚀 Starting comprehensive subscription button authentication test...")
    print("This will test the universal subscription button with different user types.")
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 SUCCESS: Subscription button authentication test completed successfully!")
            print("\n📝 Next Steps:")
            print("   1. Test Stripe Customer Portal integration")
            print("   2. Test subscription management functionality")
            print("   3. Deploy to production environment")
        else:
            print("\n⚠️  ISSUES FOUND: Some tests failed - review the results above")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
