#!/usr/bin/env python3
"""
Test JavaScript function execution in the profile page
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_subscription_javascript():
    print("🧪 Testing subscription JavaScript execution...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        # Navigate to login page
        print("📄 Loading login page...")
        driver.get("http://127.0.0.1:5006/login")
        
        # Login
        print("🔑 Logging in...")
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        
        email_field.send_keys("debug@test.com")
        password_field.send_keys("testpassword123")
        
        # Submit login form
        login_form = driver.find_element(By.TAG_NAME, "form")
        login_form.submit()
        
        # Wait for redirect and navigate to profile
        time.sleep(2)
        print("📄 Navigating to profile page...")
        driver.get("http://127.0.0.1:5006/profile")
        
        # Wait for page to load
        WebDriverWait(driver, 10).wait(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check console logs
        print("📋 Checking browser console logs...")
        logs = driver.get_log('browser')
        
        for log in logs:
            if log['level'] in ['INFO', 'WARNING', 'SEVERE']:
                print(f"  {log['level']}: {log['message']}")
        
        # Check if functions are available
        print("🔍 Checking function availability...")
        
        # Test upgradePlan function
        upgrade_available = driver.execute_script("return typeof window.upgradePlan === 'function';")
        print(f"window.upgradePlan available: {upgrade_available}")
        
        if upgrade_available:
            print("✅ upgradePlan function is available!")
            
            # Test calling the function
            try:
                result = driver.execute_script("""
                    console.log('Testing upgradePlan function from Selenium...');
                    try {
                        window.upgradePlan('Pro');
                        return 'SUCCESS: Function executed';
                    } catch (e) {
                        return 'ERROR: ' + e.message;
                    }
                """)
                print(f"Function test result: {result}")
                
            except Exception as e:
                print(f"Error testing function: {e}")
                
        else:
            print("❌ upgradePlan function is NOT available")
            
            # Check what functions are available
            available_functions = driver.execute_script("""
                var funcs = [];
                for (var prop in window) {
                    if (typeof window[prop] === 'function' && !prop.startsWith('_')) {
                        funcs.push(prop);
                    }
                }
                return funcs.slice(0, 20); // First 20 functions
            """)
            print(f"Available window functions: {available_functions}")
        
        # Try clicking an actual button
        print("🖱️ Testing actual button click...")
        try:
            upgrade_buttons = driver.find_elements(By.CSS_SELECTOR, ".select-plan-btn.upgrade")
            if upgrade_buttons:
                print(f"Found {len(upgrade_buttons)} upgrade button(s)")
                
                # Click the first button
                upgrade_buttons[0].click()
                
                # Wait a moment and check for any alerts or modals
                time.sleep(1)
                
                # Check if there are any alerts
                try:
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    print(f"Alert appeared: {alert_text}")
                    alert.accept()  # Close the alert
                except:
                    print("No alert appeared")
                
                # Check for modals
                modals = driver.find_elements(By.CSS_SELECTOR, ".modal")
                if modals:
                    print(f"Found {len(modals)} modal(s)")
                    for modal in modals:
                        if modal.is_displayed():
                            print("✅ Modal is visible - function worked!")
                        else:
                            print("Modal exists but not visible")
                else:
                    print("No modals found")
                    
            else:
                print("❌ No upgrade buttons found")
                
        except Exception as e:
            print(f"Error clicking button: {e}")
        
        # Get final console logs
        print("📋 Final console logs:")
        final_logs = driver.get_log('browser')
        for log in final_logs[-10:]:  # Last 10 logs
            print(f"  {log['level']}: {log['message']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_subscription_javascript()
