#!/usr/bin/env python3
"""
Simple test to verify subscription buttons work
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def test_subscription_buttons():
    print("🚀 Testing subscription buttons functionality...")
    
    # Setup Chrome options for headless testing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        # Navigate to profile page
        print("📄 Loading profile page...")
        driver.get("http://127.0.0.1:5006/profile")
        
        # Wait for page to load
        WebDriverWait(driver, 10).wait(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check if upgradePlan function exists in global scope
        print("🔍 Checking if upgradePlan function is globally accessible...")
        function_exists = driver.execute_script("return typeof window.upgradePlan === 'function';")
        
        if function_exists:
            print("✅ upgradePlan function is globally accessible!")
            
            # Test calling the function directly
            print("🧪 Testing upgradePlan function call...")
            try:
                result = driver.execute_script("""
                    console.log('Testing upgradePlan function...');
                    window.upgradePlan('Pro');
                    return 'Function called successfully';
                """)
                print(f"✅ Function call result: {result}")
                
                # Check for any JavaScript errors
                logs = driver.get_log('browser')
                js_errors = [log for log in logs if log['level'] == 'SEVERE']
                
                if js_errors:
                    print("❌ JavaScript errors found:")
                    for error in js_errors:
                        print(f"  - {error['message']}")
                else:
                    print("✅ No JavaScript errors detected")
                
                # Test clicking actual button
                print("🖱️ Testing actual button click...")
                upgrade_buttons = driver.find_elements(By.CSS_SELECTOR, ".select-plan-btn.upgrade")
                
                if upgrade_buttons:
                    print(f"✅ Found {len(upgrade_buttons)} upgrade buttons")
                    
                    # Click the first upgrade button
                    try:
                        upgrade_buttons[0].click()
                        time.sleep(1)
                        
                        # Check if modal appeared
                        modal = driver.find_element(By.CSS_SELECTOR, ".modal")
                        if modal and modal.is_displayed():
                            print("✅ Modal appeared after button click!")
                        else:
                            print("⚠️ Modal not visible after button click")
                            
                    except Exception as e:
                        print(f"❌ Error clicking button: {str(e)}")
                else:
                    print("❌ No upgrade buttons found on page")
                    
            except Exception as e:
                print(f"❌ Error testing function: {str(e)}")
                
        else:
            print("❌ upgradePlan function is NOT globally accessible")
            
            # Check what functions are available
            available_functions = driver.execute_script("""
                var funcs = [];
                for (var prop in window) {
                    if (typeof window[prop] === 'function' && prop.includes('Plan')) {
                        funcs.push(prop);
                    }
                }
                return funcs;
            """)
            print(f"Available functions with 'Plan' in name: {available_functions}")
        
        # Check console log for our success message
        print("📋 Checking console logs...")
        logs = driver.get_log('browser')
        success_logs = [log for log in logs if 'Subscription functions loaded' in log['message']]
        
        if success_logs:
            print("✅ Found success message in console logs")
        else:
            print("❌ Success message not found in console logs")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        
    finally:
        if 'driver' in locals():
            driver.quit()

def main():
    # First check if the server is running
    try:
        response = requests.get("http://127.0.0.1:5006/profile", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running, proceeding with test...")
            test_subscription_buttons()
        else:
            print(f"❌ Server returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please make sure the Flask app is running on port 5006")
    except Exception as e:
        print(f"❌ Error checking server: {str(e)}")

if __name__ == "__main__":
    main()
