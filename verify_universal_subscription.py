#!/usr/bin/env python3
"""
Universal Subscription Button Verification Script
Verifies that the subscription button is properly implemented across all templates.
"""

import os
import re
from typing import Dict, List, Tuple

def analyze_template(file_path: str) -> Dict[str, bool]:
    """Analyze a template file for subscription button implementation."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for subscription button in navigation
        has_subscription_link = bool(re.search(r'onclick="openCustomerPortal\(\)"', content))
        
        # Check for subscription button with credit card icon
        has_credit_card_icon = bool(re.search(r'bi-credit-card.*Subscription', content, re.DOTALL))
        
        # Check for openCustomerPortal function definition
        has_function_def = bool(re.search(r'function openCustomerPortal\(\)', content))
        
        # Check for window.openCustomerPortal assignment
        has_global_assignment = bool(re.search(r'window\.openCustomerPortal\s*=\s*openCustomerPortal', content))
        
        return {
            'has_subscription_link': has_subscription_link,
            'has_credit_card_icon': has_credit_card_icon,
            'has_function_def': has_function_def,
            'has_global_assignment': has_global_assignment,
            'fully_implemented': has_subscription_link and has_function_def and has_global_assignment
        }
    
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {
            'has_subscription_link': False,
            'has_credit_card_icon': False,
            'has_function_def': False,
            'has_global_assignment': False,
            'fully_implemented': False
        }

def main():
    """Main verification function."""
    template_dir = "/Users/sevs/Documents/Programs/webapps/resume_builder/templates"
    
    # Templates that should have the subscription button
    templates_to_check = [
        'dashboard.html',
        'dashboard_new.html', 
        'dashboard_backup.html',
        'profile.html',
        'resumes.html',
        'cover_letters.html',
        'jobs.html',
        'interview_qa.html',
        'create_cover_letter.html'
    ]
    
    print("🔍 Universal Subscription Button Verification")
    print("=" * 50)
    
    results = {}
    all_passed = True
    
    for template in templates_to_check:
        file_path = os.path.join(template_dir, template)
        if os.path.exists(file_path):
            result = analyze_template(file_path)
            results[template] = result
            
            status = "✅ PASS" if result['fully_implemented'] else "❌ FAIL"
            print(f"{status} {template}")
            
            if not result['fully_implemented']:
                all_passed = False
                if not result['has_subscription_link']:
                    print(f"  ❌ Missing subscription link with onclick handler")
                if not result['has_function_def']:
                    print(f"  ❌ Missing openCustomerPortal function definition")
                if not result['has_global_assignment']:
                    print(f"  ❌ Missing window.openCustomerPortal assignment")
            else:
                print(f"  ✅ Subscription button fully implemented")
        else:
            print(f"❌ MISSING {template} (file not found)")
            all_passed = False
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    implemented_count = sum(1 for r in results.values() if r['fully_implemented'])
    total_count = len(templates_to_check)
    
    print(f"Templates with subscription button: {implemented_count}/{total_count}")
    print(f"Success rate: {(implemented_count/total_count)*100:.1f}%")
    
    if all_passed:
        print("\n🎉 ALL TEMPLATES HAVE SUBSCRIPTION BUTTON SUCCESSFULLY IMPLEMENTED!")
        print("\n✅ The universal subscription button is now available on:")
        for template in templates_to_check:
            if template in results and results[template]['fully_implemented']:
                page_name = template.replace('.html', '').replace('_', ' ').title()
                print(f"   • {page_name}")
    else:
        print("\n❌ Some templates are missing the subscription button implementation")
        print("❓ Templates that need updates:")
        for template, result in results.items():
            if not result['fully_implemented']:
                print(f"   • {template}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
