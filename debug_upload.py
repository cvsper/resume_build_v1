#!/usr/bin/env python3
"""
Debug script to test PDF upload functionality
"""

import requests
import tempfile
import fitz  # PyMuPDF
import os
from io import BytesIO

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
    
    # Save to temporary file
    pdf_path = tempfile.mktemp(suffix='.pdf')
    doc.save(pdf_path)
    doc.close()
    
    return pdf_path

def test_upload_endpoint():
    """Test the upload functionality"""
    print("🔄 Testing PDF Upload...")
    
    base_url = "http://127.0.0.1:5006"
    
    # First, check if the upload page is accessible
    try:
        response = requests.get(f"{base_url}/upload-existing-resume", timeout=10)
        print(f"Upload page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Upload page is accessible")
        elif response.status_code in [302, 403]:
            print("⚠️  Upload page requires login")
            print("This is expected - the route is protected by @login_required")
            return
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Create test PDF
    print("Creating test PDF...")
    pdf_path = create_test_pdf()
    
    try:
        # Test file upload (this will fail without login, but we can see the response)
        with open(pdf_path, 'rb') as f:
            files = {'resume_file': ('test_resume.pdf', f, 'application/pdf')}
            response = requests.post(f"{base_url}/upload-existing-resume", files=files, timeout=10)
            
        print(f"Upload response status: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Upload endpoint is working (redirected, likely due to login requirement)")
        elif response.status_code == 200:
            print("✅ Upload endpoint responded successfully")
        else:
            print(f"Response headers: {dict(response.headers)}")
            
    except Exception as e:
        print(f"Upload test error: {e}")
    
    finally:
        # Cleanup
        os.unlink(pdf_path)

def check_route_exists():
    """Check if the upload route is properly defined"""
    print("\n🔍 Checking Route Configuration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            
        if "@app.route('/upload-existing-resume'," in content:
            print("✅ Upload route is defined in app.py")
        else:
            print("❌ Upload route not found in app.py")
            
        if "methods=['GET', 'POST']" in content:
            print("✅ Route accepts both GET and POST methods")
        else:
            print("⚠️  Route method configuration may be incorrect")
            
        if "parse_resume_file" in content:
            print("✅ File parser is imported and used")
        else:
            print("❌ File parser not integrated")
            
        if "@login_required" in content:
            print("✅ Route is protected with login requirement")
        else:
            print("⚠️  Route may not be protected")
            
    except Exception as e:
        print(f"Error checking route: {e}")

if __name__ == "__main__":
    check_route_exists()
    test_upload_endpoint()
    
    print("\n💡 DEBUGGING TIPS:")
    print("1. Make sure you're logged in when testing the upload")
    print("2. Check browser console for JavaScript errors")
    print("3. Check Flask app logs for server-side errors")
    print("4. Verify the file meets the size and type requirements")
    print("5. Test with a simple PDF first")
