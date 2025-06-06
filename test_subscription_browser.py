#!/usr/bin/env python3
"""
Test script to verify subscription button functionality in browser
"""
import requests
import json

def test_profile_page_js():
    """Test if the profile page renders with the JavaScript functions"""
    session = requests.Session()
    
    # Login first
    login_data = {
        'email': 'debug@test.com',
        'password': 'testpassword123'
    }
    
    print("🔐 Logging in with test user...")
    try:
        login_response = session.post('http://127.0.0.1:5006/login', data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:
            print("✅ Login successful")
            
            # Get profile page
            print("📄 Fetching profile page...")
            profile_response = session.get('http://127.0.0.1:5006/profile')
            
            if profile_response.status_code == 200:
                html_content = profile_response.text
                
                # Check for JavaScript functions
                checks = [
                    ('function upgradePlan', 'upgradePlan function'),
                    ('function downgradePlan', 'downgradePlan function'), 
                    ('window.upgradePlan = upgradePlan', 'global assignment'),
                    ('onclick="try { console.log', 'button onclick handler'),
                    ('console.log.*subscription functions loaded', 'function loading confirmation')
                ]
                
                print("\n🔍 Checking JavaScript content...")
                for pattern, description in checks:
                    if pattern in html_content:
                        print(f"✅ Found: {description}")
                    else:
                        print(f"❌ Missing: {description}")
                
                # Check for button with onclick
                if "upgradePlan('Pro')" in html_content:
                    print("✅ Found Pro upgrade button with onclick handler")
                else:
                    print("❌ Pro upgrade button onclick handler not found")
                    
                # Save rendered HTML for inspection
                with open('rendered_profile_debug.html', 'w') as f:
                    f.write(html_content)
                print("💾 Saved rendered HTML to rendered_profile_debug.html")
                
            else:
                print(f"❌ Failed to get profile page: {profile_response.status_code}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_profile_page_js()
