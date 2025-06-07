#!/usr/bin/env python3
"""
Simple Subscription Flow Test
Tests basic functionality of the subscription flow
"""

import requests
import sys

def main():
    base_url = "http://127.0.0.1:5006"
    
    print("🧪 Testing Subscription Flow")
    print("-" * 40)
    
    # Test 1: Server availability
    print("1. Testing server...")
    try:
        response = requests.get(base_url, timeout=5)
        print(f"   Server status: {response.status_code}")
    except Exception as e:
        print(f"   Server error: {e}")
        return
    
    # Test 2: Pricing page
    print("2. Testing pricing page...")
    try:
        response = requests.get(f"{base_url}/pricing", timeout=5)
        print(f"   Pricing page status: {response.status_code}")
        
        # Check for key elements
        content = response.text.lower()
        elements_found = []
        
        if 'sidebar' in content:
            elements_found.append('sidebar')
        if 'pricing' in content or 'plan' in content:
            elements_found.append('pricing_content')
        if 'pro' in content and 'premium' in content:
            elements_found.append('subscription_plans')
        if 'upgrade' in content or 'select' in content:
            elements_found.append('action_buttons')
            
        print(f"   Elements found: {', '.join(elements_found) if elements_found else 'none'}")
        
    except Exception as e:
        print(f"   Pricing page error: {e}")
    
    # Test 3: Dashboard navigation
    print("3. Testing dashboard navigation...")
    try:
        response = requests.get(f"{base_url}/dashboard", allow_redirects=True, timeout=5)
        print(f"   Dashboard status: {response.status_code}")
        
        content = response.text.lower()
        if '/pricing' in content:
            print("   ✅ Dashboard contains pricing links")
        else:
            print("   ⚠️  No pricing links found in dashboard")
            
    except Exception as e:
        print(f"   Dashboard error: {e}")
    
    print("-" * 40)
    print("✅ Basic tests complete!")
    print("🌐 Manual testing: http://127.0.0.1:5006/pricing")

if __name__ == "__main__":
    main()
