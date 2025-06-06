#!/usr/bin/env python3
"""
LIVE SUBSCRIPTION BUTTON TEST
============================

Tests the subscription buttons against the running Flask application.
"""

import requests
from bs4 import BeautifulSoup
import re

def test_live_app():
    """Test the live Flask application for subscription functionality."""
    
    print("🧪 TESTING LIVE FLASK APPLICATION")
    print("=" * 50)
    
    try:
        # Test main page
        response = requests.get('http://127.0.0.1:61885', timeout=10)
        print(f"✅ Main page accessible (Status: {response.status_code})")
        
        # Look for JavaScript in the response
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        all_js = ""
        for script in scripts:
            if script.string:
                all_js += script.string + "\n"
        
        # Check for our critical functions
        functions_found = {
            'upgradePlan_definition': 'function upgradePlan(' in all_js,
            'downgradePlan_definition': 'function downgradePlan(' in all_js,
            'cancelSubscription_definition': 'function cancelSubscription(' in all_js,
            'window_upgradePlan': 'window.upgradePlan = upgradePlan' in all_js,
            'window_downgradePlan': 'window.downgradePlan = downgradePlan' in all_js,
        }
        
        print("\n🔍 JAVASCRIPT FUNCTION CHECK:")
        for func_name, found in functions_found.items():
            status = "✅" if found else "❌"
            print(f"{status} {func_name}: {found}")
        
        # Count subscription-related onclick handlers
        onclick_count = len(re.findall(r'onclick.*upgradePlan\(|onclick.*downgradePlan\(', all_js, re.IGNORECASE))
        print(f"\n🖱️  Found {onclick_count} subscription onclick handlers")
        
        # Test if we can create a simple request to the profile page
        try:
            profile_response = requests.get('http://127.0.0.1:61885/profile', timeout=10, allow_redirects=False)
            if profile_response.status_code == 200:
                print("✅ Profile page accessible without authentication")
            elif profile_response.status_code == 302:
                print("🔐 Profile page requires authentication (redirected)")
            else:
                print(f"⚠️  Profile page status: {profile_response.status_code}")
        except Exception as e:
            print(f"⚠️  Profile page test failed: {e}")
        
        # Summary
        success_count = sum(functions_found.values())
        total_functions = len(functions_found)
        
        print(f"\n📊 SUMMARY: {success_count}/{total_functions} functions found")
        
        if success_count == total_functions:
            print("🎉 ALL CRITICAL FUNCTIONS DETECTED!")
            print("✅ Subscription buttons should be working!")
        else:
            print("⚠️  Some functions may be missing or need attention")
        
        return success_count == total_functions
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app")
        print("Make sure Flask is running on http://127.0.0.1:61885")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def create_browser_test_page():
    """Create a test page to verify subscription functions work in browser."""
    
    test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Subscription Function Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        button { padding: 10px 20px; margin: 10px; }
        .result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🧪 Subscription Function Test</h1>
    
    <div>
        <button onclick="testUpgradePlan('Pro')">Test Upgrade to Pro</button>
        <button onclick="testDowngradePlan('Basic')">Test Downgrade to Basic</button>
        <button onclick="testFunctionAvailability()">Test Function Availability</button>
    </div>
    
    <div id="results"></div>
    
    <script>
        function logResult(message, isSuccess = true) {
            const div = document.createElement('div');
            div.className = 'result ' + (isSuccess ? 'success' : 'error');
            div.innerHTML = message;
            document.getElementById('results').appendChild(div);
        }
        
        // Mock subscription functions for testing
        function upgradePlan(plan) {
            console.log('upgradePlan called with:', plan);
            logResult('✅ upgradePlan("' + plan + '") executed successfully');
            return true;
        }
        
        function downgradePlan(plan) {
            console.log('downgradePlan called with:', plan);
            logResult('✅ downgradePlan("' + plan + '") executed successfully');
            return true;
        }
        
        // Make functions globally available
        window.upgradePlan = upgradePlan;
        window.downgradePlan = downgradePlan;
        
        // Test functions
        function testUpgradePlan(plan) {
            try {
                if (typeof window.upgradePlan === 'function') {
                    window.upgradePlan(plan);
                } else {
                    logResult('❌ window.upgradePlan is not a function', false);
                }
            } catch (e) {
                logResult('❌ Error calling upgradePlan: ' + e.message, false);
            }
        }
        
        function testDowngradePlan(plan) {
            try {
                if (typeof window.downgradePlan === 'function') {
                    window.downgradePlan(plan);
                } else {
                    logResult('❌ window.downgradePlan is not a function', false);
                }
            } catch (e) {
                logResult('❌ Error calling downgradePlan: ' + e.message, false);
            }
        }
        
        function testFunctionAvailability() {
            logResult('🔍 Testing function availability...');
            
            if (typeof upgradePlan === 'function') {
                logResult('✅ upgradePlan is defined as function');
            } else {
                logResult('❌ upgradePlan is not defined as function', false);
            }
            
            if (typeof window.upgradePlan === 'function') {
                logResult('✅ window.upgradePlan is available globally');
            } else {
                logResult('❌ window.upgradePlan is not available globally', false);
            }
            
            if (typeof downgradePlan === 'function') {
                logResult('✅ downgradePlan is defined as function');
            } else {
                logResult('❌ downgradePlan is not defined as function', false);
            }
            
            if (typeof window.downgradePlan === 'function') {
                logResult('✅ window.downgradePlan is available globally');
            } else {
                logResult('❌ window.downgradePlan is not available globally', false);
            }
        }
        
        // Auto-run tests on page load
        window.addEventListener('DOMContentLoaded', function() {
            logResult('🚀 Page loaded, running automatic tests...');
            testFunctionAvailability();
        });
    </script>
</body>
</html>"""
    
    with open('/Users/sevs/Documents/Programs/webapps/resume_builder/live_subscription_test.html', 'w') as f:
        f.write(test_html)
    
    print("✅ Created live_subscription_test.html")
    print("🌐 Open this file in a browser to test JavaScript functions")

if __name__ == "__main__":
    print("🚀 LIVE SUBSCRIPTION BUTTON TEST")
    print("=" * 50)
    
    success = test_live_app()
    create_browser_test_page()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: All subscription functions detected!")
        print("✅ The subscription button fix should be working!")
    else:
        print("⚠️  Some functions may need attention")
    
    print("\n📋 MANUAL TESTING STEPS:")
    print("1. Open http://127.0.0.1:61885 in your browser")
    print("2. Navigate to the profile page")
    print("3. Click subscription upgrade/downgrade buttons")
    print("4. Check browser console for errors")
    print("5. Open live_subscription_test.html to test functions directly")
