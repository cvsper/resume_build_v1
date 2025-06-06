#!/usr/bin/env python3
"""
Test script to reproduce the Invalid API Key error during resume download
"""

import requests
import json

def test_payment_flow():
    """Test the complete payment flow to identify where the API key error occurs"""
    session = requests.Session()
    
    try:
        # 1. Login
        print("🔐 Logging in...")
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        login_response = session.post('http://127.0.0.1:5006/login', data=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return
        
        # 2. Create a test resume
        print("📝 Creating test resume...")
        resume_data = {
            'name': 'Test User', 
            'content': 'Software Engineer with 5+ years experience in Python, JavaScript, and cloud technologies.'
        }
        create_response = session.post('http://127.0.0.1:5006/create-resume', data=resume_data)
        print(f"   Create resume status: {create_response.status_code}")
        
        # 3. Get the resume ID by checking the resumes page
        print("📄 Getting resume list...")
        resumes_response = session.get('http://127.0.0.1:5006/resumes')
        print(f"   Resumes page status: {resumes_response.status_code}")
        
        # Look for resume ID in the HTML
        import re
        resume_ids = re.findall(r'resume_id[=:](\d+)', resumes_response.text)
        if not resume_ids:
            # Try different patterns
            resume_ids = re.findall(r'/resumes/(\d+)/', resumes_response.text)
            if not resume_ids:
                resume_ids = re.findall(r'download-pdf/(\d+)', resumes_response.text)
        
        if resume_ids:
            resume_id = resume_ids[0]
            print(f"   Found resume ID: {resume_id}")
            
            # 4. Try to download (should redirect to payment)
            print("💰 Testing download process...")
            download_url = f'http://127.0.0.1:5006/download-pdf/{resume_id}'
            download_response = session.get(download_url, allow_redirects=False)
            print(f"   Download response: {download_response.status_code}")
            
            if download_response.status_code == 302:
                redirect_location = download_response.headers.get('Location', '')
                print(f"   Redirected to: {redirect_location}")
                
                # Follow redirect to payment page
                payment_response = session.get(redirect_location)
                print(f"   Payment page status: {payment_response.status_code}")
                
                # 5. Try to create a checkout session
                print("🛒 Testing checkout session creation...")
                checkout_data = {
                    'resume_id': resume_id
                }
                checkout_response = session.post('http://127.0.0.1:5006/create-checkout-session', 
                                               data=checkout_data, allow_redirects=False)
                print(f"   Checkout session status: {checkout_response.status_code}")
                
                if checkout_response.status_code != 303:  # Expected redirect to Stripe
                    print(f"   Checkout response headers: {dict(checkout_response.headers)}")
                    print(f"   Checkout response text: {checkout_response.text[:500]}")
                else:
                    print("   ✅ Checkout session created successfully!")
                    stripe_url = checkout_response.headers.get('Location', '')
                    if 'stripe' in stripe_url:
                        print(f"   ✅ Redirected to Stripe: {stripe_url[:100]}...")
                    else:
                        print(f"   ⚠️  Unexpected redirect: {stripe_url}")
                        
            else:
                print(f"   Unexpected download response: {download_response.status_code}")
                print(f"   Response text: {download_response.text[:300]}")
        else:
            print("❌ No resume ID found in the response")
            # Print part of the response to debug
            print(f"   Response length: {len(resumes_response.text)}")
            print(f"   Sample response: {resumes_response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing Resume Download Payment Flow")
    print("=" * 50)
    test_payment_flow()
    print("=" * 50)
