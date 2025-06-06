#!/usr/bin/env python3
"""
Debug JavaScript syntax in profile.html template
"""

import re
import subprocess
import tempfile
import os

def extract_javascript_from_template():
    """Extract JavaScript code from the profile.html template"""
    with open('/Users/sevs/Documents/Programs/webapps/resume_builder/templates/profile.html', 'r') as f:
        content = f.read()
    
    # Find the script block
    script_start = content.find('<script>')
    script_end = content.find('</script>')
    
    if script_start == -1 or script_end == -1:
        print("❌ Could not find script tags in template")
        return None
    
    # Extract JavaScript content
    js_content = content[script_start + 8:script_end]
    
    # Clean up Django template syntax that might interfere with JS parsing
    js_content = re.sub(r'{%.*?%}', '', js_content)
    js_content = re.sub(r'{{.*?}}', '""', js_content)
    
    return js_content

def check_js_syntax(js_content):
    """Check JavaScript syntax using Node.js"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_content)
        temp_file = f.name
    
    try:
        # Check syntax with Node.js
        result = subprocess.run(['node', '--check', temp_file], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ JavaScript syntax is valid")
            return True
        else:
            print("❌ JavaScript syntax errors found:")
            print(result.stderr)
            return False
    
    except FileNotFoundError:
        print("❌ Node.js not found. Skipping syntax check.")
        return None
    
    finally:
        os.unlink(temp_file)

def find_upgradePlan_function():
    """Find and check the upgradePlan function specifically"""
    with open('/Users/sevs/Documents/Programs/webapps/resume_builder/templates/profile.html', 'r') as f:
        content = f.read()
    
    # Find upgradePlan function
    match = re.search(r'function upgradePlan\([^}]+\}(?:\s*\})*', content, re.DOTALL)
    
    if match:
        print("✅ Found upgradePlan function:")
        func_content = match.group(0)
        print(f"Function starts at character: {match.start()}")
        print(f"Function length: {len(func_content)} characters")
        
        # Check for common issues
        if func_content.count('{') != func_content.count('}'):
            print("❌ Mismatched braces in upgradePlan function")
        else:
            print("✅ Braces are balanced in upgradePlan function")
        
        return True
    else:
        print("❌ upgradePlan function not found")
        return False

def check_button_onclick():
    """Check if buttons have correct onclick attributes"""
    with open('/Users/sevs/Documents/Programs/webapps/resume_builder/templates/profile.html', 'r') as f:
        content = f.read()
    
    # Find onclick attributes
    onclick_matches = re.findall(r'onclick="upgradePlan\([^"]*\)"', content)
    
    print(f"✅ Found {len(onclick_matches)} buttons with upgradePlan onclick:")
    for match in onclick_matches:
        print(f"  - {match}")

if __name__ == "__main__":
    print("🔍 Debugging JavaScript syntax in profile.html")
    print("=" * 50)
    
    # Extract JavaScript
    js_content = extract_javascript_from_template()
    if js_content:
        print(f"✅ Extracted {len(js_content)} characters of JavaScript")
        
        # Check syntax
        check_js_syntax(js_content)
    
    print("\n" + "=" * 50)
    
    # Check specific function
    find_upgradePlan_function()
    
    print("\n" + "=" * 50)
    
    # Check button onclick
    check_button_onclick()
