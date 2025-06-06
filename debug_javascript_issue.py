#!/usr/bin/env python3
"""
Debug JavaScript Issue - Find the exact cause of the upgradePlan error
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_javascript_functions():
    """Debug JavaScript functions in the live application"""
    
    print("🔍 DEBUGGING JAVASCRIPT FUNCTIONS")
    print("=" * 50)
    
    try:
        # Get the page content
        response = requests.get('http://127.0.0.1:5006', timeout=10)
        print(f"✅ Page loaded successfully (Status: {response.status_code})")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all script tags
        scripts = soup.find_all('script')
        print(f"📄 Found {len(scripts)} script tags")
        
        # Combine all JavaScript content
        all_js = ""
        for i, script in enumerate(scripts):
            if script.string:
                all_js += f"// Script {i+1}\n{script.string}\n\n"
                
        # Check for function definitions
        upgrade_pattern = r'function\s+upgradePlan\s*\([^)]*\)\s*\{'
        downgrade_pattern = r'function\s+downgradePlan\s*\([^)]*\)\s*\{'
        
        upgrade_matches = re.findall(upgrade_pattern, all_js)
        downgrade_matches = re.findall(downgrade_pattern, all_js)
        
        print(f"\n🔍 FUNCTION DEFINITIONS:")
        print(f"   upgradePlan definitions: {len(upgrade_matches)}")
        print(f"   downgradePlan definitions: {len(downgrade_matches)}")
        
        # Check for window assignments
        window_upgrade = 'window.upgradePlan' in all_js
        window_downgrade = 'window.downgradePlan' in all_js
        
        print(f"\n🔍 WINDOW ASSIGNMENTS:")
        print(f"   window.upgradePlan: {window_upgrade}")
        print(f"   window.downgradePlan: {window_downgrade}")
        
        # Check for onclick handlers
        onclick_pattern = r'onclick="[^"]*upgradePlan[^"]*"'
        onclick_matches = re.findall(onclick_pattern, all_js)
        
        print(f"\n🔍 ONCLICK HANDLERS:")
        print(f"   Found {len(onclick_matches)} onclick handlers with upgradePlan")
        
        if onclick_matches:
            print("   Sample onclick handler:")
            print(f"   {onclick_matches[0][:100]}...")
            
        # Check order of definitions
        upgrade_pos = all_js.find('function upgradePlan(')
        window_pos = all_js.find('window.upgradePlan = upgradePlan')
        onclick_pos = all_js.find('onclick')
        
        print(f"\n🔄 EXECUTION ORDER:")
        print(f"   Function definition position: {upgrade_pos}")
        print(f"   Window assignment position: {window_pos}")
        print(f"   First onclick position: {onclick_pos}")
        
        # Check if functions are inside script tags
        script_positions = []
        for match in re.finditer(r'<script[^>]*>', all_js):
            script_positions.append(('script_start', match.start()))
        for match in re.finditer(r'</script>', all_js):
            script_positions.append(('script_end', match.start()))
            
        script_positions.sort(key=lambda x: x[1])
        
        print(f"\n📋 SCRIPT TAG ANALYSIS:")
        if upgrade_pos >= 0:
            inside_script = False
            for tag_type, pos in script_positions:
                if pos < upgrade_pos:
                    if tag_type == 'script_start':
                        inside_script = True
                    elif tag_type == 'script_end':
                        inside_script = False
                elif pos > upgrade_pos:
                    break
            
            print(f"   upgradePlan function inside script tags: {inside_script}")
        
        # Look for specific error patterns
        print(f"\n⚠️  POTENTIAL ISSUES:")
        
        if upgrade_pos >= 0 and window_pos >= 0:
            if upgrade_pos > window_pos:
                print("   ❌ Function defined AFTER window assignment")
            else:
                print("   ✅ Function defined BEFORE window assignment")
        else:
            print("   ❌ Function or window assignment not found")
            
        if onclick_pos >= 0 and upgrade_pos >= 0:
            if onclick_pos < upgrade_pos:
                print("   ❌ onclick handler BEFORE function definition")
            else:
                print("   ✅ onclick handler AFTER function definition")
        
        # Save the JavaScript for manual inspection
        with open('/Users/sevs/Documents/Programs/webapps/resume_builder/extracted_js_debug.js', 'w') as f:
            f.write(all_js)
        print(f"\n💾 JavaScript saved to extracted_js_debug.js")
        
        return all_js
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_test_page():
    """Create a minimal test page to verify JavaScript functions"""
    
    test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>JavaScript Function Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        button { padding: 10px 20px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🧪 JavaScript Function Test</h1>
    
    <div>
        <h2>Test Buttons:</h2>
        <button onclick="testDirectCall()">Test Direct upgradePlan Call</button>
        <button onclick="testWindowCall()">Test window.upgradePlan Call</button>
        <button onclick="testInlineCall()">Test Inline Call (like in HTML)</button>
        <button onclick="checkFunctionAvailability()">Check Function Availability</button>
    </div>
    
    <div id="results"></div>
    
    <script>
        function log(message, isError = false) {
            const div = document.createElement('div');
            div.className = 'result ' + (isError ? 'error' : 'success');
            div.textContent = new Date().toLocaleTimeString() + ': ' + message;
            document.getElementById('results').appendChild(div);
            console.log(message);
        }
        
        // Test if we can define the function here
        function upgradePlan(plan) {
            log('✅ upgradePlan called with plan: ' + plan);
            return true;
        }
        
        // Assign to window
        window.upgradePlan = upgradePlan;
        
        function testDirectCall() {
            try {
                upgradePlan('Pro');
            } catch (e) {
                log('❌ Direct call failed: ' + e.message, true);
            }
        }
        
        function testWindowCall() {
            try {
                window.upgradePlan('Pro');
            } catch (e) {
                log('❌ Window call failed: ' + e.message, true);
            }
        }
        
        function testInlineCall() {
            try {
                // This simulates the onclick handler
                console.log('Pro button clicked'); 
                upgradePlan('Pro');
            } catch(e) { 
                console.error('Error calling upgradePlan:', e); 
                log('❌ Inline call failed: ' + e.message, true);
            }
        }
        
        function checkFunctionAvailability() {
            log('🔍 Checking function availability...');
            
            if (typeof upgradePlan === 'function') {
                log('✅ upgradePlan is a function');
            } else {
                log('❌ upgradePlan is not a function: ' + typeof upgradePlan, true);
            }
            
            if (typeof window.upgradePlan === 'function') {
                log('✅ window.upgradePlan is a function');
            } else {
                log('❌ window.upgradePlan is not a function: ' + typeof window.upgradePlan, true);
            }
            
            // Check global scope
            if ('upgradePlan' in window) {
                log('✅ upgradePlan exists in global scope');
            } else {
                log('❌ upgradePlan does not exist in global scope', true);
            }
        }
        
        // Auto-run checks on page load
        window.addEventListener('DOMContentLoaded', function() {
            log('🚀 Page loaded, running automatic checks...');
            checkFunctionAvailability();
        });
    </script>
</body>
</html>'''
    
    with open('/Users/sevs/Documents/Programs/webapps/resume_builder/js_function_test.html', 'w') as f:
        f.write(test_html)
    
    print("✅ Created js_function_test.html")
    print("🌐 Open this file in a browser to test JavaScript functions")

if __name__ == "__main__":
    print("🚀 JAVASCRIPT DEBUGGING SESSION")
    print("=" * 60)
    
    js_content = debug_javascript_functions()
    create_test_page()
    
    print("\n" + "=" * 60)
    print("📋 DEBUGGING SUMMARY:")
    print("1. Check the extracted_js_debug.js file for the complete JavaScript")
    print("2. Open js_function_test.html in a browser to test basic function calls")
    print("3. Open http://127.0.0.1:5006 and check the browser console for errors")
    print("4. Try clicking the subscription buttons and note the exact error message")
    
    if js_content and 'function upgradePlan(' in js_content:
        print("\n✅ upgradePlan function found in JavaScript")
    else:
        print("\n❌ upgradePlan function NOT found in JavaScript")
        print("🔧 This indicates the function may not be included in the page")
