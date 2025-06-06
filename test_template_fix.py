#!/usr/bin/env python3
"""
Quick verification that the template syntax error is fixed
"""
import requests

def test_template_fix():
    """Test that the profile page loads without template errors"""
    session = requests.Session()
    
    # Login first
    login_data = {
        'email': 'debug@test.com',
        'password': 'testpassword123'
    }
    
    print("🔧 Testing template syntax fix...")
    try:
        # Login
        login_response = session.post('http://127.0.0.1:5006/login', data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:
            print("✅ Login successful")
            
            # Test profile page
            profile_response = session.get('http://127.0.0.1:5006/profile')
            
            if profile_response.status_code == 200:
                print("✅ Profile page loads successfully - no template syntax errors!")
                
                html_content = profile_response.text
                
                # Verify key elements are still present
                checks = [
                    ('function upgradePlan(plan) {', 'upgradePlan function'),
                    ('window.upgradePlan = upgradePlan;', 'global assignment'),
                    ('onclick="try { console.log(\'Pro button clicked\'); upgradePlan(\'Pro\');', 'button onclick'),
                    ('{% endblock %}', 'proper template ending')
                ]
                
                all_good = True
                for pattern, description in checks:
                    if pattern in html_content:
                        print(f"✅ {description} found")
                    else:
                        print(f"❌ {description} missing")
                        all_good = False
                
                # Count function definitions
                upgrade_count = html_content.count('function upgradePlan(')
                endblock_count = html_content.count('{% endblock %}')
                
                print(f"📊 Function Analysis:")
                print(f"   - upgradePlan definitions: {upgrade_count} (should be 1)")
                print(f"   - endblock tags: {endblock_count} (should be few)")
                
                if all_good and upgrade_count == 1:
                    print("\n🎉 SUCCESS! Template syntax error is fixed!")
                    print("✅ Profile page loads correctly")
                    print("✅ Subscription functions are present")
                    print("✅ Template structure is valid")
                else:
                    print(f"\n⚠️  Some issues remain. Check counts above.")
                    
            else:
                print(f"❌ Profile page failed to load: {profile_response.status_code}")
                if 'TemplateSyntaxError' in profile_response.text:
                    print("❌ Template syntax error still exists")
                else:
                    print("❌ Different error occurred")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_template_fix()
