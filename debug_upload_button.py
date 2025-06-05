#!/usr/bin/env python3
"""
Debug script to test the upload button functionality
"""

import logging
from app import app, db
from flask import session
import tempfile
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def test_upload_button():
    """Test the upload button functionality by simulating the workflow"""
    
    with app.test_client() as client:
        with app.app_context():
            # First, we need to simulate a logged-in user
            # Create a test user for this session
            from models import User
            from werkzeug.security import generate_password_hash
            
            # Check if test user exists
            test_user = User.query.filter_by(email='test_upload@example.com').first()
            if not test_user:
                test_user = User(
                    name='Test Upload User',
                    email='test_upload@example.com',
                    password=generate_password_hash('testpass')
                )
                db.session.add(test_user)
                db.session.commit()
            
            # Simulate login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user.id)
                sess['_fresh'] = True
            
            print("=== Testing Upload Route Access ===")
            
            # Test GET request to upload page
            response = client.get('/upload-existing-resume')
            print(f"GET /upload-existing-resume status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Upload page loads successfully")
                # Check if form elements are present
                html_content = response.get_data(as_text=True)
                if 'id="fileInput"' in html_content:
                    print("✅ File input found in HTML")
                else:
                    print("❌ File input missing from HTML")
                    
                if 'id="submitBtn"' in html_content:
                    print("✅ Submit button found in HTML")
                else:
                    print("❌ Submit button missing from HTML")
                    
                if 'enctype="multipart/form-data"' in html_content:
                    print("✅ Form has correct enctype for file upload")
                else:
                    print("❌ Form missing multipart enctype")
            else:
                print(f"❌ Upload page failed to load: {response.status_code}")
                return
            
            print("\n=== Testing File Upload POST ===")
            
            # Create a test file
            test_content = b"""
            John Doe
            Software Engineer
            Email: john.doe@example.com
            Phone: (555) 123-4567
            
            Experience:
            - Software Developer at Tech Company (2020-Present)
            - Junior Developer at Startup (2018-2020)
            
            Education:
            - Bachelor of Computer Science, University (2018)
            
            Skills:
            - Python, JavaScript, SQL
            """
            
            # Test POST request with file
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                tmp.write(test_content)
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, 'rb') as test_file:
                    data = {
                        'resume_file': (test_file, 'test_resume.pdf', 'application/pdf')
                    }
                    
                    response = client.post('/upload-existing-resume', 
                                         data=data, 
                                         content_type='multipart/form-data',
                                         follow_redirects=False)
                    
                    print(f"POST /upload-existing-resume status: {response.status_code}")
                    
                    if response.status_code == 302:
                        print(f"✅ Upload successful, redirecting to: {response.location}")
                    elif response.status_code == 200:
                        print("⚠️  Upload returned 200 - checking for errors in response")
                        response_text = response.get_data(as_text=True)
                        if 'error' in response_text.lower() or 'danger' in response_text:
                            print("❌ Error found in response")
                            # Extract error messages
                            import re
                            error_matches = re.findall(r'alert-danger[^>]*>([^<]+)', response_text)
                            for error in error_matches:
                                print(f"   Error: {error.strip()}")
                        else:
                            print("   No obvious errors found")
                    else:
                        print(f"❌ Upload failed with status: {response.status_code}")
                        print(f"Response: {response.get_data(as_text=True)[:500]}...")
                        
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
            
            print("\n=== Debug Information ===")
            print(f"Test user ID: {test_user.id}")
            print(f"Test user email: {test_user.email}")
            
            # Check if file parser module exists
            try:
                from resume.file_parser import parse_resume_file
                print("✅ File parser module available")
            except ImportError as e:
                print(f"❌ File parser module missing: {e}")
            except Exception as e:
                print(f"⚠️  File parser module issue: {e}")

if __name__ == '__main__':
    test_upload_button()
