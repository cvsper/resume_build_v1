#!/usr/bin/env python3
"""
Direct test of Stripe checkout session creation to find the API key error
"""

import requests
import json

def test_checkout_session():
    """Test Stripe checkout session creation directly"""
    session = requests.Session()
    
    # Login first
    print("🔐 Logging in...")
    login_data = {'email': 'test@example.com', 'password': 'password123'}
    login_response = session.post('http://127.0.0.1:5006/login', data=login_data)
    
    if login_response.status_code == 302:  # Redirect after successful login
        print("✅ Login successful")
        
        # Try to create a checkout session for resume download
        print("🛒 Testing checkout session creation...")
        checkout_data = {'resume_id': '1'}  # Use a dummy resume ID
        
        checkout_response = session.post(
            'http://127.0.0.1:5006/create-checkout-session', 
            data=checkout_data, 
            allow_redirects=False
        )
        
        print(f"Status: {checkout_response.status_code}")
        print(f"Headers: {dict(checkout_response.headers)}")
        
        if checkout_response.status_code != 303:  # Not the expected redirect
            print("Response content:")
            print(checkout_response.text)
            
        return checkout_response.status_code == 303
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Stripe Checkout Session Creation")
    print("=" * 50)
    success = test_checkout_session()
    if success:
        print("✅ Checkout session test passed")
    else:
        print("❌ Checkout session test failed")
    print("=" * 50)
