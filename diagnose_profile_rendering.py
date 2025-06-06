#!/usr/bin/env python3
"""
Diagnostic script to check what's being rendered on the profile page
"""

import requests
import re

def diagnose_profile_page():
    print("🔍 Diagnosing profile page rendering...")
    
    session = requests.Session()
    
    # Login first
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword123'
    }
    
    login_response = session.post('http://127.0.0.1:5006/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    # Get profile page
    profile_response = session.get('http://127.0.0.1:5006/profile')
    html = profile_response.text
    
    print(f"Profile page status: {profile_response.status_code}")
    print(f"HTML length: {len(html)} characters")
    
    # Check template structure
    print("\n=== TEMPLATE STRUCTURE ===")
    if "base_dashboard.html" in html:
        print("✅ Using base_dashboard.html")
    else:
        print("❌ Not using base_dashboard.html")
        
    # Check for key profile elements
    print("\n=== PROFILE CONTENT ===")
    if "My Account" in html:
        print("✅ Profile title found")
    if "profile-settings" in html or "account-card" in html:
        print("✅ Profile-specific CSS classes found")
    else:
        print("❌ Profile-specific content not found")
        
    # Check for subscription elements
    print("\n=== SUBSCRIPTION CONTENT ===")
    if "subscription" in html.lower():
        print("✅ Subscription content found")
    if "upgrade" in html.lower():
        print("✅ Upgrade content found")
    if "select-plan-btn" in html:
        print("✅ Plan selection buttons found")
    else:
        print("❌ Plan selection buttons NOT found")
        
    # Check for JavaScript blocks
    print("\n=== JAVASCRIPT CONTENT ===")
    script_tags = html.count('<script>')
    print(f"Found {script_tags} script tags")
    
    if "extra_js" in html:
        print("✅ extra_js block marker found")
    else:
        print("❌ extra_js block marker NOT found")
        
    if "DOMContentLoaded" in html:
        print("✅ DOMContentLoaded listener found")
    else:
        print("❌ DOMContentLoaded listener NOT found")
        
    if "function upgradePlan" in html:
        print("✅ upgradePlan function found")
    else:
        print("❌ upgradePlan function NOT found")
        
    # Check what template is actually being used
    print("\n=== TEMPLATE DIAGNOSIS ===")
    title_match = re.search(r'<title>(.*?)</title>', html)
    if title_match:
        title = title_match.group(1)
        print(f"Page title: {title}")
        
        if "My Account" in title or "Profile" in title:
            print("✅ Correct profile page title")
        else:
            print("❌ Unexpected page title - wrong template?")
    
    # Look for any template rendering errors
    if "TemplateSyntaxError" in html or "Template Error" in html:
        print("❌ Template syntax error detected")
        
    # Check for any Flask/Jinja errors
    if "jinja2" in html.lower() or "werkzeug" in html.lower():
        print("❌ Flask/Jinja error detected")
        
    # Sample the HTML content
    print("\n=== HTML SAMPLE ===")
    print("First 200 characters:")
    print(html[:200])
    print("\nLast 200 characters:")
    print(html[-200:])
    
    # Check if we can find the specific subscription section
    subscription_section = re.search(r'<div[^>]*subscription[^>]*>.*?</div>', html, re.IGNORECASE | re.DOTALL)
    if subscription_section:
        print("\n✅ Found subscription section in HTML")
        print("Sample subscription content:")
        print(subscription_section.group(0)[:300] + "...")
    else:
        print("\n❌ No subscription section found in HTML")

if __name__ == "__main__":
    diagnose_profile_page()
