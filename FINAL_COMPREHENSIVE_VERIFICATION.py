#!/usr/bin/env python3
"""
Final comprehensive verification of the subscription button fix
"""
import requests

def final_verification():
    """Complete verification that everything is working"""
    session = requests.Session()
    
    print("🎯 FINAL COMPREHENSIVE VERIFICATION")
    print("=" * 50)
    
    # Test 1: Template syntax
    print("\n📋 Test 1: Template Syntax")
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('profile.html')
        print("✅ Template compiles without syntax errors")
    except Exception as e:
        print(f"❌ Template error: {e}")
        return False
    
    # Test 2: Flask app loading
    print("\n📋 Test 2: Flask App Loading")
    try:
        from app import app
        print("✅ Flask app loads successfully")
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False
    
    # Test 3: Login and profile page access
    print("\n📋 Test 3: Profile Page Access")
    try:
        # Login
        login_data = {'email': 'debug@test.com', 'password': 'testpassword123'}
        login_response = session.post('http://127.0.0.1:5006/login', data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:
            print("✅ Login successful")
            
            # Access profile page
            profile_response = session.get('http://127.0.0.1:5006/profile')
            if profile_response.status_code == 200:
                print("✅ Profile page loads successfully")
                html_content = profile_response.text
                
                # Test 4: Function structure verification
                print("\n📋 Test 4: JavaScript Function Structure")
                
                # Count critical elements
                upgrade_func_count = html_content.count('function upgradePlan(')
                downgrade_func_count = html_content.count('function downgradePlan(')
                global_assign_count = html_content.count('window.upgradePlan = upgradePlan')
                button_onclick_count = html_content.count('upgradePlan(\'Pro\')')
                endblock_count = html_content.count('{% endblock %}')
                
                print(f"   - upgradePlan functions: {upgrade_func_count} (should be 1)")
                print(f"   - downgradePlan functions: {downgrade_func_count} (should be 1)")
                print(f"   - Global assignments: {global_assign_count} (should be 1)")
                print(f"   - Button onclick handlers: {button_onclick_count} (should be >= 1)")
                print(f"   - Template endblocks: {endblock_count} (should be 7)")
                
                # Test 5: Function positioning
                print("\n📋 Test 5: Function Definition Order")
                upgrade_pos = html_content.find('function upgradePlan(')
                global_pos = html_content.find('window.upgradePlan = upgradePlan')
                button_pos = html_content.find('upgradePlan(\'Pro\')')
                dom_ready_pos = html_content.find('DOMContentLoaded')
                
                if upgrade_pos < global_pos:
                    print("✅ Function defined before global assignment")
                else:
                    print("❌ Function defined after global assignment")
                
                if global_pos < button_pos:
                    print("✅ Global assignment before button usage")
                else:
                    print("❌ Global assignment after button usage")
                
                if upgrade_pos < dom_ready_pos:
                    print("✅ Function defined before DOMContentLoaded")
                else:
                    print("❌ Function defined after DOMContentLoaded")
                
                # Test 6: Critical elements check
                print("\n📋 Test 6: Critical Elements Present")
                critical_elements = [
                    ('CRITICAL: Define subscription functions FIRST', 'Function priority comment'),
                    ('console.log(\'✅ Subscription functions defined', 'Success logging'),
                    ('onclick="try { console.log(\'Pro button clicked\');', 'Enhanced error handling'),
                    ('createConfirmationModal', 'Helper function'),
                    ('submitSubscriptionForm', 'Submit helper')
                ]
                
                all_present = True
                for element, description in critical_elements:
                    if element in html_content:
                        print(f"✅ {description}")
                    else:
                        print(f"❌ Missing: {description}")
                        all_present = False
                
                # Final assessment
                print("\n" + "=" * 50)
                if (upgrade_func_count == 1 and 
                    global_assign_count == 1 and 
                    endblock_count == 7 and
                    upgrade_pos < global_pos < button_pos and
                    all_present):
                    print("🎉 SUCCESS! ALL TESTS PASSED!")
                    print("✅ Template syntax error RESOLVED")
                    print("✅ Subscription functions properly defined")
                    print("✅ Function execution order correct")
                    print("✅ No duplicate code remaining")
                    print("\n🚀 READY FOR BROWSER TESTING!")
                    print("The subscription upgrade/downgrade buttons should now work correctly.")
                    return True
                else:
                    print("⚠️  Some issues detected. Review test results above.")
                    return False
            else:
                print(f"❌ Profile page failed: {profile_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    final_verification()
