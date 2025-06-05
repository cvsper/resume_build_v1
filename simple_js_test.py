#!/usr/bin/env python3
"""
Simple JavaScript Function Test
===============================
Test to verify the subscription JavaScript functions are properly defined
"""

import requests

def test_profile_page_javascript():
    """Test that the profile page loads and JavaScript functions are properly embedded"""
    
    print("🚀 Testing Profile Page JavaScript")
    print("=" * 50)
    
    try:
        # Fetch the profile page HTML
        response = requests.get("http://127.0.0.1:5006/profile", timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            print("✅ Profile page loaded successfully")
            
            # Check for JavaScript functions in the HTML
            functions_to_check = [
                'function upgradePlan(',
                'function downgradePlan(',
                'function createConfirmationModal('
            ]
            
            functions_found = []
            for func_pattern in functions_to_check:
                if func_pattern in html_content:
                    functions_found.append(func_pattern.split(' ')[1].split('(')[0])
                    print(f"✅ Found: {func_pattern.split(' ')[1].split('(')[0]}")
                else:
                    print(f"❌ Missing: {func_pattern.split(' ')[1].split('(')[0]}")
            
            # Check script tag structure
            script_open_count = html_content.count('<script>')
            script_close_count = html_content.count('</script>')
            
            print(f"\n📊 Script Tag Analysis:")
            print(f"   <script> tags: {script_open_count}")
            print(f"   </script> tags: {script_close_count}")
            
            if script_open_count == script_close_count:
                print("✅ Script tags are balanced")
            else:
                print("❌ Script tags are not balanced!")
            
            # Check for function definitions within script tags
            script_sections = []
            start_pos = 0
            while True:
                script_start = html_content.find('<script>', start_pos)
                if script_start == -1:
                    break
                script_end = html_content.find('</script>', script_start)
                if script_end == -1:
                    break
                script_content = html_content[script_start:script_end + 9]
                script_sections.append(script_content)
                start_pos = script_end + 9
            
            print(f"\n🔍 Found {len(script_sections)} script sections")
            
            functions_in_scripts = 0
            for i, script in enumerate(script_sections):
                funcs_in_this_script = []
                for func_name in ['upgradePlan', 'downgradePlan', 'createConfirmationModal']:
                    if f'function {func_name}(' in script:
                        funcs_in_this_script.append(func_name)
                        functions_in_scripts += 1
                
                if funcs_in_this_script:
                    print(f"   Script {i+1}: Contains {', '.join(funcs_in_this_script)}")
            
            print(f"\n📈 Results Summary:")
            print(f"   Functions found in HTML: {len(functions_found)}/3")
            print(f"   Functions inside script tags: {functions_in_scripts}/3")
            
            if len(functions_found) == 3 and functions_in_scripts == 3:
                print("\n🎉 SUCCESS: All JavaScript functions are properly defined within script tags!")
                return True
            else:
                print("\n❌ ISSUE: Some JavaScript functions are missing or misplaced!")
                return False
                
        else:
            print(f"❌ Failed to load profile page (Status: {response.status_code})")
            if response.status_code == 302:
                print("   This might be a redirect to login page")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_profile_page_javascript()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS FOR MANUAL TESTING")
    print("=" * 60)
    print("1. Open http://127.0.0.1:5006 in your browser")
    print("2. Log in to your account")
    print("3. Go to Account/Profile page") 
    print("4. Open browser console (F12 → Console tab)")
    print("5. Click any subscription button")
    print("6. Check that no 'ReferenceError: upgradePlan' appears")
    print("7. Verify button functionality works as expected")
    
    if success:
        print("\n✅ JavaScript structure test PASSED!")
        print("🎯 The ReferenceError should now be fixed!")
    else:
        print("\n❌ JavaScript structure test FAILED!")
        print("🔧 There may still be issues with the JavaScript structure")
