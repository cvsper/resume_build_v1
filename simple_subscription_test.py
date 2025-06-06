#!/usr/bin/env python3
"""Simple test to verify subscription button functionality"""

import requests
import re

def test_login_and_profile():
    print("🔄 Testing login and subscription buttons...")
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5006"
    
    # Test login
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    try:
        print("1. Attempting login...")
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
        print(f"   Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login successful!")
            
            # Test profile page
            print("2. Accessing profile page...")
            profile_response = session.get(f"{base_url}/profile")
            print(f"   Profile response status: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                print("✅ Profile page accessible!")
                
                # Check for subscription functions
                content = profile_response.text
                
                upgradePlan_count = len(re.findall(r'function upgradePlan', content))
                downgradePlan_count = len(re.findall(r'function downgradePlan', content))
                cancelSubscription_count = len(re.findall(r'function cancelSubscription', content))
                
                print(f"   Found upgradePlan function: {upgradePlan_count} times")
                print(f"   Found downgradePlan function: {downgradePlan_count} times") 
                print(f"   Found cancelSubscription function: {cancelSubscription_count} times")
                
                # Check for onclick handlers
                onclick_upgrade = 'onclick' in content and 'upgradePlan' in content
                onclick_downgrade = 'onclick' in content and 'downgradePlan' in content
                
                print(f"   Found onclick with upgradePlan: {onclick_upgrade}")
                print(f"   Found onclick with downgradePlan: {onclick_downgrade}")
                
                if upgradePlan_count > 0 and onclick_upgrade:
                    print("🎉 SUCCESS: Subscription functions are present and accessible!")
                    return True
                else:
                    print("❌ ISSUE: Functions or onclick handlers missing")
                    
            else:
                print(f"❌ Profile page not accessible: {profile_response.status_code}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_login_and_profile()
    
    if success:
        print("\n✅ TECHNICAL VERIFICATION COMPLETE!")
        print("🔄 NEXT: Manual browser testing required")
        print("📝 Instructions:")
        print("   1. Go to http://127.0.0.1:5006/login")
        print("   2. Login with: test@example.com / password123")
        print("   3. Navigate to profile page")
        print("   4. Test subscription buttons")
        print("   5. Check browser console for errors")
    else:
        print("\n❌ Technical verification failed - need to investigate further")
