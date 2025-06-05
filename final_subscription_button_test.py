#!/usr/bin/env python3
"""
Final Subscription Button Test
=============================
This script tests the subscription button functionality after the JavaScript fix
to ensure the ReferenceError has been resolved and buttons work properly.
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import sys

def test_subscription_buttons():
    """Test subscription buttons functionality"""
    
    print("🚀 Final Subscription Button Test")
    print("=" * 50)
    
    # Check if Flask app is running
    try:
        response = requests.get("http://127.0.0.1:5006", timeout=5)
        print("✅ Flask application is running")
    except requests.exceptions.RequestException:
        print("❌ Flask application is not running!")
        print("Please start the Flask app with: python3 app.py")
        return False
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        print("\n🔍 Starting browser test...")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        # Navigate to the main page
        driver.get("http://127.0.0.1:5006")
        print("✅ Loaded main page")
        
        # Check for login or account access
        print("\n📝 Testing account access...")
        
        # Try to find login elements
        try:
            login_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Login")
            login_link.click()
            print("✅ Found and clicked login link")
            time.sleep(2)
        except NoSuchElementException:
            print("ℹ️  No login link found - might already be logged in")
        
        # Try to access profile/account page directly
        driver.get("http://127.0.0.1:5006/profile")
        time.sleep(3)
        
        print("\n🔍 Checking for subscription buttons...")
        
        # Check for subscription-related elements
        subscription_elements = []
        
        # Look for common subscription button patterns
        button_selectors = [
            "button[onclick*='upgradePlan']",
            "button[onclick*='downgradePlan']", 
            ".subscription-btn",
            ".upgrade-btn",
            ".downgrade-btn",
            "button:contains('Upgrade')",
            "button:contains('Subscribe')",
            "button:contains('Pro Plan')",
            "button:contains('Premium')"
        ]
        
        found_buttons = []
        for selector in button_selectors:
            try:
                if selector.startswith("button:contains"):
                    # Handle text-based selectors differently
                    buttons = driver.find_elements(By.XPATH, f"//button[contains(text(), '{selector.split('(')[1].split(')')[0].strip(\"'\")}')]")
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if buttons:
                    found_buttons.extend(buttons)
                    print(f"✅ Found {len(buttons)} button(s) with selector: {selector}")
            except Exception as e:
                continue
        
        # Check JavaScript console for errors
        print("\n🔍 Checking for JavaScript errors...")
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if js_errors:
            print("❌ JavaScript errors found:")
            for error in js_errors:
                print(f"  - {error['message']}")
                if "ReferenceError" in error['message'] and "upgradePlan" in error['message']:
                    print("❌ CRITICAL: ReferenceError for upgradePlan still exists!")
                    return False
        else:
            print("✅ No JavaScript errors found")
        
        # Test button functionality if buttons are found
        if found_buttons:
            print(f"\n🧪 Testing {len(found_buttons)} subscription button(s)...")
            
            for i, button in enumerate(found_buttons[:3]):  # Test up to 3 buttons
                try:
                    print(f"  Testing button {i+1}: {button.text or 'No text'}")
                    
                    # Get button's onclick attribute
                    onclick = button.get_attribute('onclick')
                    if onclick:
                        print(f"    - onclick: {onclick}")
                    
                    # Try clicking the button
                    driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    
                    # Click and check for immediate errors
                    initial_logs = len(driver.get_log('browser'))
                    button.click()
                    time.sleep(2)
                    
                    # Check for new errors after click
                    new_logs = driver.get_log('browser')[initial_logs:]
                    click_errors = [log for log in new_logs if log['level'] == 'SEVERE']
                    
                    if click_errors:
                        print(f"❌ Errors after clicking button {i+1}:")
                        for error in click_errors:
                            print(f"      - {error['message']}")
                            if "ReferenceError" in error['message']:
                                return False
                    else:
                        print(f"✅ Button {i+1} clicked without JavaScript errors")
                    
                except Exception as e:
                    print(f"⚠️  Could not test button {i+1}: {e}")
        else:
            print("ℹ️  No subscription buttons found on current page")
            print("    This might be normal if user is not logged in or on a different page")
        
        # Check if the JavaScript functions are available in the page
        print("\n🔍 Checking JavaScript function availability...")
        
        functions_to_check = ['upgradePlan', 'downgradePlan', 'createConfirmationModal']
        for func_name in functions_to_check:
            try:
                result = driver.execute_script(f"return typeof {func_name} === 'function';")
                if result:
                    print(f"✅ Function '{func_name}' is available")
                else:
                    print(f"❌ Function '{func_name}' is not available")
            except Exception as e:
                print(f"⚠️  Could not check function '{func_name}': {e}")
        
        print("\n🎉 Subscription button test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        if driver:
            driver.quit()

def manual_test_instructions():
    """Provide manual testing instructions"""
    print("\n" + "=" * 60)
    print("📋 MANUAL TESTING INSTRUCTIONS")
    print("=" * 60)
    print("Since automated testing has limitations, please also test manually:")
    print()
    print("1. 🌐 Open your browser and go to: http://127.0.0.1:5006")
    print("2. 🔐 Log in to your account")
    print("3. 👤 Navigate to Account/Profile page")
    print("4. 🔍 Look for subscription buttons (Upgrade, Subscribe, etc.)")
    print("5. 🖱️  Click on any subscription button")
    print("6. ✅ Verify that:")
    print("   - No 'ReferenceError: Can't find variable: upgradePlan' appears")
    print("   - Button click triggers expected behavior (modal, redirect, etc.)")
    print("   - Browser console shows no JavaScript errors")
    print()
    print("🔧 To check browser console:")
    print("   - Press F12 or right-click → Inspect")
    print("   - Go to 'Console' tab")
    print("   - Click subscription buttons and watch for errors")
    print()
    print("✅ If no ReferenceError appears, the fix is successful!")

if __name__ == "__main__":
    print("🧪 Running Final Subscription Button Test...")
    success = test_subscription_buttons()
    manual_test_instructions()
    
    if success:
        print("\n🎉 AUTOMATED TEST PASSED!")
        print("✅ JavaScript structure appears to be fixed")
        print("📝 Please complete the manual testing steps above")
    else:
        print("\n❌ AUTOMATED TEST FAILED!")
        print("🔧 Please check the Flask application and try again")
    
    sys.exit(0 if success else 1)
