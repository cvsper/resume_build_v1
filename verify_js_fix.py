#!/usr/bin/env python3
"""
Simple JavaScript Fix Verification
==================================

This script checks that the JavaScript fix has been applied correctly
by examining the profile template file directly.
"""

import re

def verify_javascript_fix():
    """Verify that the JavaScript functions are properly enclosed in script tags"""
    print("🔍 Verifying JavaScript Fix in Profile Template...")
    
    try:
        # Read the profile template file
        with open('/Users/sevs/Documents/Programs/webapps/resume_builder/templates/profile.html', 'r') as f:
            content = f.read()
        
        # Find all script sections
        script_sections = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        
        # Check for JavaScript functions
        functions_to_check = ['upgradePlan', 'downgradePlan', 'createConfirmationModal']
        functions_found = {}
        
        for func_name in functions_to_check:
            functions_found[func_name] = False
            
            # Check if function is defined within any script tag
            for script in script_sections:
                if f'function {func_name}(' in script:
                    functions_found[func_name] = True
                    break
        
        # Report results
        print("\n📊 JavaScript Function Check Results:")
        print("-" * 40)
        
        all_functions_found = True
        for func_name, found in functions_found.items():
            status = "✅ Found" if found else "❌ Missing"
            print(f"{func_name}: {status}")
            if not found:
                all_functions_found = False
        
        # Check for the specific fix - ensure functions are not outside script tags
        functions_outside_script = False
        
        # Remove all script sections from content
        content_without_scripts = content
        for script in script_sections:
            content_without_scripts = content_without_scripts.replace(f'<script>{script}</script>', '')
            content_without_scripts = content_without_scripts.replace(f'<script type="text/javascript">{script}</script>', '')
        
        # Check if any functions are still in the remaining content
        for func_name in functions_to_check:
            if f'function {func_name}(' in content_without_scripts:
                functions_outside_script = True
                print(f"⚠️  Warning: {func_name} function found outside script tags!")
        
        print("\n" + "=" * 50)
        
        if all_functions_found and not functions_outside_script:
            print("🎉 SUCCESS: JavaScript fix has been applied correctly!")
            print("✅ All functions are properly defined within script tags")
            print("✅ No functions found outside script tags")
            print("\n📋 Next Steps:")
            print("1. Open http://127.0.0.1:5006 in your browser")
            print("2. Log in to your account")
            print("3. Navigate to the Account/Profile page")
            print("4. Test the subscription buttons")
            print("5. You should no longer see the 'ReferenceError' and buttons should work")
            return True
        else:
            print("❌ ISSUES DETECTED:")
            if not all_functions_found:
                print("- Some JavaScript functions are missing")
            if functions_outside_script:
                print("- Some functions are still outside script tags")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying JavaScript fix: {e}")
        return False

if __name__ == "__main__":
    print("🚀 JavaScript Fix Verification")
    print("=" * 50)
    verify_javascript_fix()
