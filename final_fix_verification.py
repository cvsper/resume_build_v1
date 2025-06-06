#!/usr/bin/env python3
"""
Final verification test for subscription button fix
"""
import requests
import re

def test_fixed_subscription():
    """Verify the subscription button fix is working"""
    session = requests.Session()
    
    # Login
    login_data = {
        'email': 'debug@test.com',
        'password': 'testpassword123'
    }
    
    print("🔧 Testing FINAL subscription button fix...")
    try:
        # Login first
        login_response = session.post('http://127.0.0.1:5006/login', data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:
            print("✅ Login successful")
            
            # Get profile page
            profile_response = session.get('http://127.0.0.1:5006/profile')
            
            if profile_response.status_code == 200:
                html_content = profile_response.text
                
                # Count function definitions
                upgrade_count = html_content.count('function upgradePlan(')
                downgrade_count = html_content.count('function downgradePlan(')
                global_assignments = html_content.count('window.upgradePlan = upgradePlan')
                
                print(f"📊 Function Analysis:")
                print(f"   - upgradePlan definitions: {upgrade_count} (should be 1)")
                print(f"   - downgradePlan definitions: {downgrade_count} (should be 1)")
                print(f"   - Global assignments: {global_assignments} (should be 1)")
                
                # Check for critical elements
                checks = [
                    ('CRITICAL: Define subscription functions FIRST', 'Functions defined at top'),
                    ('function upgradePlan(plan) {', 'upgradePlan function exists'),
                    ('window.upgradePlan = upgradePlan;', 'Global assignment exists'),
                    ('console.log(\'✅ Subscription functions defined', 'Success message'),
                    ('onclick="try { console.log(\'Pro button clicked\'); upgradePlan(\'Pro\');', 'Button onclick handler')
                ]
                
                all_good = True
                for pattern, description in checks:
                    if pattern in html_content:
                        print(f"✅ {description}")
                    else:
                        print(f"❌ Missing: {description}")
                        all_good = False
                
                # Check structure
                script_start = html_content.find('{% block extra_js %}')
                upgrade_func_pos = html_content.find('function upgradePlan(')
                button_pos = html_content.find('upgradePlan(\'Pro\')')
                
                if script_start < upgrade_func_pos < button_pos:
                    print("✅ Correct order: Script block → Function definition → Button usage")
                else:
                    print("❌ Incorrect order detected")
                    all_good = False
                
                if all_good and upgrade_count == 1 and global_assignments == 1:
                    print("\n🎉 SUCCESS! The subscription button fix is complete!")
                    print("✅ Functions are defined exactly once")
                    print("✅ Functions are defined at the top of the script")
                    print("✅ Functions are made globally accessible")
                    print("✅ Button onclick handlers should now work")
                    print("\n🔥 Ready for browser testing!")
                else:
                    print(f"\n⚠️  Issues detected. Function counts: upgrade={upgrade_count}, global={global_assignments}")
                    
            else:
                print(f"❌ Failed to get profile page: {profile_response.status_code}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fixed_subscription()
