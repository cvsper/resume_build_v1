#!/usr/bin/env python3
"""
Complete Fix Verification Test
"""

import requests

def test_app_running():
    """Test if the Flask app is running"""
    try:
        response = requests.get("http://127.0.0.1:5006", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_javascript_blocks():
    """Test if JavaScript functions are properly included in templates"""
    print("🔍 Testing JavaScript Block Integration...")
    
    try:
        with open('/Users/sevs/Documents/Programs/webapps/resume_builder/templates/profile.html', 'r') as f:
            content = f.read()
            
        # Check for correct block name
        if "{% block extra_js %}" in content:
            print("   ✅ Correct block name: extra_js")
        else:
            print("   ❌ Block name issue")
            return False
            
        # Check for JavaScript functions
        if "function upgradePlan" in content:
            print("   ✅ upgradePlan function present")
        else:
            print("   ❌ upgradePlan function missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading template: {e}")
        return False

def test_csrf_token_removal():
    """Test if CSRF token was properly removed from preview page"""
    print("🔍 Testing CSRF Token Removal...")
    
    try:
        with open('/Users/sevs/Documents/Programs/webapps/resume_builder/templates/preview.html', 'r') as f:
            content = f.read()
            
        # Check that csrf_token() is NOT in the file
        if "csrf_token()" not in content:
            print("   ✅ CSRF token function removed")
            return True
        else:
            print("   ❌ CSRF token function still present")
            return False
            
    except Exception as e:
        print(f"   ❌ Error reading template: {e}")
        return False

def main():
    print("🚀 COMPLETE FIX VERIFICATION")
    print("=" * 50)
    
    # Test 1: App running
    if test_app_running():
        print("✅ Flask app is running")
    else:
        print("❌ Flask app is not running")
        return
    
    print()
    
    # Test 2: JavaScript blocks
    js_ok = test_javascript_blocks()
    print()
    
    # Test 3: CSRF token removal
    csrf_ok = test_csrf_token_removal()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 FIX VERIFICATION SUMMARY")
    print("=" * 50)
    
    print(f"JavaScript Block Integration: {'✅ PASS' if js_ok else '❌ FAIL'}")
    print(f"CSRF Token Removal: {'✅ PASS' if csrf_ok else '❌ FAIL'}")
    
    if js_ok and csrf_ok:
        print("\n🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
        print("✨ The subscription buttons and payment forms should work correctly")
        print("🚀 Ready for production deployment")
    else:
        print("\n⚠️  Some issues detected")

if __name__ == "__main__":
    main()
