#!/usr/bin/env python3
"""
Quick test to register a user and test upload
"""

import requests
import tempfile
import fitz
import os

def create_test_pdf():
    """Create a simple test PDF"""
    doc = fitz.open()
    page = doc.new_page()
    
    content = """John Doe
Software Engineer
john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in web development.

WORK EXPERIENCE
Senior Software Engineer - Tech Corp (2020-Present)
• Developed scalable web applications
• Led team of 5 developers

EDUCATION
Bachelor of Science in Computer Science
University of Technology (2014-2018)

SKILLS
Python, JavaScript, React, SQL"""
    
    page.insert_text((50, 50), content, fontsize=11)
    
    pdf_path = tempfile.mktemp(suffix='.pdf')
    doc.save(pdf_path)
    doc.close()
    
    return pdf_path

def test_complete_flow():
    """Test the complete flow: register -> login -> upload"""
    base_url = "http://127.0.0.1:5006"
    session = requests.Session()
    
    print("🔄 Testing Complete Upload Flow...")
    
    # Test 1: Check if we can access the homepage
    try:
        response = session.get(base_url, timeout=10)
        print(f"✅ Homepage accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot access homepage: {e}")
        return
    
    # Test 2: Try to register a test user
    print("2. Testing registration...")
    try:
        register_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        response = session.post(f"{base_url}/register", data=register_data, timeout=10)
        print(f"   Registration response: {response.status_code}")
        
        if response.status_code == 200:
            print("   ⚠️  Registration form returned (may need to check validation)")
        elif response.status_code == 302:
            print("   ✅ Registration successful (redirected)")
        
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
    
    # Test 3: Try to login
    print("3. Testing login...")
    try:
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = session.post(f"{base_url}/login", data=login_data, timeout=10)
        print(f"   Login response: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Login successful (redirected)")
        elif response.status_code == 200:
            print("   ⚠️  Login form returned (check credentials)")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    # Test 4: Try to access upload page
    print("4. Testing upload page access...")
    try:
        response = session.get(f"{base_url}/upload-existing-resume", timeout=10)
        print(f"   Upload page response: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Upload page accessible after login")
        elif response.status_code == 302:
            print("   ❌ Still redirecting to login (authentication failed)")
        
    except Exception as e:
        print(f"   ❌ Upload page error: {e}")
    
    # Test 5: Try to upload a file
    print("5. Testing file upload...")
    pdf_path = create_test_pdf()
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'resume_file': ('test_resume.pdf', f, 'application/pdf')}
            response = session.post(f"{base_url}/upload-existing-resume", files=files, timeout=10)
            print(f"   Upload response: {response.status_code}")
            
            if response.status_code == 302:
                print("   ✅ Upload successful (redirected)")
                if 'edit-resume' in response.headers.get('Location', ''):
                    print("   ✅ Redirected to edit page as expected")
                else:
                    print("   ⚠️  Redirected but not to edit page")
            elif response.status_code == 200:
                print("   ⚠️  Upload returned form (may have validation errors)")
            
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
    
    finally:
        os.unlink(pdf_path)
    
    print("\n💡 TROUBLESHOOTING GUIDE:")
    print("If upload still doesn't work:")
    print("1. ✅ Make sure you're logged in first")
    print("2. ✅ Check browser console for JavaScript errors")
    print("3. ✅ Verify file is PDF/DOC/DOCX and under 10MB")
    print("4. ✅ Check Flask logs for error messages")
    print("5. ✅ Try a different browser or incognito mode")

if __name__ == "__main__":
    test_complete_flow()
