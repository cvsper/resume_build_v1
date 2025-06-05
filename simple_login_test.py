#!/usr/bin/env python3
"""Simple test to verify login works with the test user"""

import requests

def test_login():
    print("🔐 Testing login with test user...")
    
    session = requests.Session()
    
    # Try to login with the test user credentials
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    try:
        # POST to login
        response = session.post('http://127.0.0.1:5006/login', 
                              data=login_data,
                              allow_redirects=True)
        
        print(f"Login response status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        # Check if we can access the upload page now
        upload_response = session.get('http://127.0.0.1:5006/upload-existing-resume')
        print(f"Upload page status after login: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            print("✅ SUCCESS: Login works and upload page is accessible!")
            return True
        else:
            print("❌ Upload page still not accessible after login")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    test_login()
