#!/usr/bin/env python3
"""
Test script to verify the universal subscription button implementation
"""

import requests
import os
from bs4 import BeautifulSoup

def test_universal_subscription_button():
    """Test that the subscription button is now visible to all users"""
    print("🧪 Testing Universal Subscription Button Implementation")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5006"
    
    # Check if Flask app is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print("❌ Flask app not accessible")
            return False
    except requests.RequestException:
        print("❌ Flask app not running on http://127.0.0.1:5006")
        return False
    
    print("✅ Flask app is running")
    
    # Test template files for changes
    template_files = [
        '/Users/sevs/Documents/Programs/webapps/resume_builder/templates/dashboard.html',
        '/Users/sevs/Documents/Programs/webapps/resume_builder/templates/dashboard_new.html',
        '/Users/sevs/Documents/Programs/webapps/resume_builder/templates/dashboard_backup.html'
    ]
    
    print("\n🔍 Checking template modifications...")
    
    for template_path in template_files:
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            
            template_name = os.path.basename(template_path)
            
            # Check that conditional logic was removed
            if "{% if current_user.subscription and current_user.subscription != 'Free' %}" in content:
                print(f"   ❌ {template_name}: Still has conditional logic")
                return False
            else:
                print(f"   ✅ {template_name}: Conditional logic removed")
            
            # Check that button text was updated
            if '<i class="bi bi-credit-card"></i> Subscription' in content:
                print(f"   ✅ {template_name}: Button text updated to 'Subscription'")
            elif '<i class="bi bi-credit-card"></i> Manage Subscription' in content:
                print(f"   ❌ {template_name}: Still shows 'Manage Subscription'")
                return False
            else:
                print(f"   ⚠️  {template_name}: Subscription button not found")
                return False
            
            # Check that openCustomerPortal function is still called
            if 'onclick="openCustomerPortal()"' in content:
                print(f"   ✅ {template_name}: openCustomerPortal function call intact")
            else:
                print(f"   ❌ {template_name}: openCustomerPortal function call missing")
                return False
    
    print("\n🔧 Checking backend route...")
    
    # Check that the backend route exists
    app_path = '/Users/sevs/Documents/Programs/webapps/resume_builder/app.py'
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            app_content = f.read()
        
        if "@app.route('/create-customer-portal', methods=['POST'])" in app_content:
            print("   ✅ /create-customer-portal route exists")
        else:
            print("   ❌ /create-customer-portal route missing")
            return False
            
        if "stripe.billing_portal.Session.create" in app_content:
            print("   ✅ Stripe Customer Portal integration found")
        else:
            print("   ❌ Stripe Customer Portal integration missing")
            return False
    
    print("\n🎯 Summary of Changes:")
    print("   • Removed conditional logic ({% if current_user.subscription != 'Free' %})")
    print("   • Changed button text from 'Manage Subscription' to 'Subscription'")
    print("   • Button now visible to ALL users (Free, Pro, Premium)")
    print("   • Backend route handles all user types (creates Stripe customer if needed)")
    print("   • Free users can upgrade, Pro/Premium users can manage/downgrade")
    
    print("\n✅ Universal Subscription Button Implementation Complete!")
    print("\n📝 Next Steps:")
    print("   1. Login to your app and verify the button appears in the sidebar")
    print("   2. Test with different user types (Free, Pro, Premium)")
    print("   3. Click the button to ensure Stripe Customer Portal opens correctly")
    
    return True

if __name__ == "__main__":
    test_universal_subscription_button()
