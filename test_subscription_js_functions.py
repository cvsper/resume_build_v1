#!/usr/bin/env python3
"""
Test the JavaScript functions in the profile.html template directly
"""

import sys
import os

def test_javascript_functions():
    """Test if all required JavaScript functions are present in profile.html"""
    print("🔍 Testing JavaScript Functions in profile.html")
    print("=" * 50)
    
    # Read the profile.html file
    profile_path = os.path.join(os.getcwd(), 'templates', 'profile.html')
    
    if not os.path.exists(profile_path):
        print(f"❌ Profile template not found at: {profile_path}")
        return False
    
    with open(profile_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required JavaScript functions
    required_functions = [
        'function upgradePlan(',
        'function downgradePlan(',
        'function createConfirmationModal(',
        'function openCustomerPortal(',
        'function loadBillingHistory(',
        'function hideBillingHistory(',
        'function cancelSubscription(',
        'function confirmDeleteAccount('
    ]
    
    all_present = True
    for func in required_functions:
        if func in content:
            print(f"   ✅ {func.replace('function ', '').replace('(', '')} - Found")
        else:
            print(f"   ❌ {func.replace('function ', '').replace('(', '')} - Missing")
            all_present = False
    
    # Check for enhanced error handling
    error_handling_patterns = [
        'try {',
        'catch (error)',
        'console.error(',
        'alert('
    ]
    
    error_handling_present = True
    for pattern in error_handling_patterns:
        if pattern in content:
            print(f"   ✅ Error handling pattern '{pattern}' - Found")
        else:
            print(f"   ❌ Error handling pattern '{pattern}' - Missing")
            error_handling_present = False
    
    # Check for subscription content
    subscription_elements = [
        'class="subscription-section"',
        'class="plan-cards"',
        'onclick="upgradePlan(',
        'onclick="downgradePlan(',
        'id="billing-history-section"'
    ]
    
    subscription_content_present = True
    for element in subscription_elements:
        if element in content:
            print(f"   ✅ Subscription element '{element}' - Found")
        else:
            print(f"   ❌ Subscription element '{element}' - Missing")
            subscription_content_present = False
    
    print("\n" + "=" * 50)
    
    if all_present and error_handling_present and subscription_content_present:
        print("🎉 ALL JAVASCRIPT FUNCTIONS AND CONTENT VERIFIED!")
        print("✅ Profile template is complete and ready for use")
        return True
    else:
        print("❌ Some JavaScript functions or content are missing")
        return False

def main():
    """Run the JavaScript function test"""
    if test_javascript_functions():
        print("\n🚀 SUCCESS: All subscription system components are present!")
        return 0
    else:
        print("\n❌ FAILURE: Missing subscription system components")
        return 1

if __name__ == "__main__":
    sys.exit(main())
