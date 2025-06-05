#!/usr/bin/env python3
"""Complete test of authentication and upload functionality"""

import requests
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_test_pdf():
    """Create a simple test PDF file"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    
    # Create a simple PDF with resume content
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    
    # Add content to the PDF
    c.drawString(100, 750, "JOHN DOE")
    c.drawString(100, 730, "Software Engineer")
    c.drawString(100, 710, "Email: john.doe@example.com")
    c.drawString(100, 690, "Phone: (555) 123-4567")
    c.drawString(100, 670, "")
    c.drawString(100, 650, "EXPERIENCE")
    c.drawString(100, 630, "Senior Developer at Tech Corp (2020-2023)")
    c.drawString(100, 610, "- Developed web applications using Python and JavaScript")
    c.drawString(100, 590, "- Led team of 3 developers")
    c.drawString(100, 570, "")
    c.drawString(100, 550, "EDUCATION")
    c.drawString(100, 530, "Bachelor of Science in Computer Science")
    c.drawString(100, 510, "University of Technology (2016-2020)")
    
    c.save()
    return temp_file.name

def test_complete_flow():
    """Test the complete authentication and upload flow"""
    print("🚀 Testing Complete Authentication and Upload Flow")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    base_url = "http://127.0.0.1:5006"
    
    # Step 1: Test initial redirect protection
    print("1️⃣ Testing upload page protection...")
    upload_response = session.get(f"{base_url}/upload-existing-resume", allow_redirects=False)
    if upload_response.status_code == 302:
        print("✅ Upload page correctly redirects when not logged in")
    else:
        print(f"❌ Expected 302 redirect, got {upload_response.status_code}")
        return False
    
    # Step 2: Test registration (if needed)
    print("2️⃣ Testing user registration...")
    register_data = {
        'name': 'Test User',
        'email': 'testflow@example.com',
        'password': 'testpass123'
    }
    
    register_response = session.post(f"{base_url}/register", data=register_data)
    if register_response.status_code == 200:
        if 'already registered' in register_response.text:
            print("✅ User already exists, proceeding to login")
        else:
            print("✅ Registration completed")
    
    # Step 3: Test login
    print("3️⃣ Testing login...")
    login_data = {
        'email': 'testflow@example.com',
        'password': 'testpass123'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
    if login_response.status_code == 200 and 'dashboard' in login_response.url:
        print("✅ Login successful - redirected to dashboard")
    else:
        print(f"❌ Login failed. Status: {login_response.status_code}, URL: {login_response.url}")
        return False
    
    # Step 4: Test upload page access after login
    print("4️⃣ Testing upload page access after login...")
    upload_page_response = session.get(f"{base_url}/upload-existing-resume")
    if upload_page_response.status_code == 200:
        print("✅ Upload page accessible after login")
    else:
        print(f"❌ Upload page not accessible after login. Status: {upload_page_response.status_code}")
        return False
    
    # Step 5: Test file upload
    print("5️⃣ Testing file upload...")
    
    # Create a test PDF
    test_pdf_path = create_test_pdf()
    
    try:
        with open(test_pdf_path, 'rb') as pdf_file:
            files = {'resume_file': ('test_resume.pdf', pdf_file, 'application/pdf')}
            upload_response = session.post(f"{base_url}/upload-existing-resume", files=files)
            
            if upload_response.status_code == 200:
                if 'edit-resume' in upload_response.url:
                    print("✅ File upload successful - redirected to edit page")
                    return True
                else:
                    print("⚠️  File uploaded but not redirected to edit page")
                    print(f"Response URL: {upload_response.url}")
            else:
                print(f"❌ File upload failed. Status: {upload_response.status_code}")
                return False
    finally:
        # Clean up the temp file
        if os.path.exists(test_pdf_path):
            os.unlink(test_pdf_path)
    
    return False

def main():
    """Main test function"""
    try:
        success = test_complete_flow()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Authentication is working correctly")
            print("✅ Upload functionality is accessible after login")
            print("✅ File upload and processing works")
            print("\n💡 The resume upload functionality is now fixed!")
        else:
            print("❌ Some tests failed")
            print("💡 Check the Flask app logs for more details")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
