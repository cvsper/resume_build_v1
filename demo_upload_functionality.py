#!/usr/bin/env python3
"""
Create a test user and demonstrate the upload functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Resume
from werkzeug.security import generate_password_hash
import tempfile
import fitz
from resume.file_parser import parse_resume_file
from werkzeug.datastructures import FileStorage
from io import BytesIO

def create_test_user():
    """Create a test user for demonstration"""
    with app.app_context():
        # Check if test user already exists
        test_user = User.query.filter_by(email='test@example.com').first()
        
        if not test_user:
            # Create a new test user
            test_user = User(
                name='Test User',
                email='test@example.com',
                password=generate_password_hash('password123')
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created: test@example.com / password123")
        else:
            print("✅ Test user already exists: test@example.com / password123")
        
        return test_user

def create_test_pdf():
    """Create a comprehensive test PDF"""
    doc = fitz.open()
    page = doc.new_page()
    
    content = """SARAH JOHNSON
Senior Software Engineer
📧 sarah.johnson@email.com | 📱 (555) 987-6543 | 🔗 linkedin.com/in/sarahjohnson
San Francisco, CA 94102

PROFESSIONAL SUMMARY
Results-driven Senior Software Engineer with 6+ years of experience developing scalable web applications and leading cross-functional teams. Proven track record of delivering high-quality software solutions that improve user experience and business outcomes.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, SQL
Frontend Technologies: React, Vue.js, HTML5, CSS3, SASS, Bootstrap
Backend Technologies: Node.js, Express.js, Django, Flask, Spring Boot
Databases: PostgreSQL, MongoDB, MySQL, Redis
Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, Git, CI/CD
Tools & Frameworks: RESTful APIs, GraphQL, Microservices, Agile/Scrum

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechCorp Inc. | San Francisco, CA | Jan 2021 - Present
• Lead development of customer-facing web applications serving 500K+ active users
• Architected and implemented microservices infrastructure reducing system latency by 40%
• Mentored 3 junior developers and conducted code reviews for team of 8 engineers
• Collaborated with product managers and designers to deliver features ahead of schedule
• Implemented automated testing strategies improving code coverage from 65% to 90%

Software Engineer | InnovateTech Solutions | San Jose, CA | Jun 2018 - Dec 2020
• Developed and maintained RESTful APIs handling 1M+ requests daily
• Built responsive frontend interfaces using React and modern JavaScript frameworks
• Optimized database queries reducing average response time by 35%
• Participated in agile development process and sprint planning sessions
• Implemented authentication and authorization systems using JWT and OAuth

Junior Software Developer | StartupXYZ | Palo Alto, CA | Aug 2017 - May 2018
• Assisted in development of e-commerce platform using Python Django
• Created and maintained unit tests achieving 80% code coverage
• Collaborated with senior developers on feature implementation and bug fixes
• Participated in daily standups and weekly retrospectives

EDUCATION

Bachelor of Science in Computer Science | University of California, Berkeley | 2013 - 2017
• Magna Cum Laude, GPA: 3.8/4.0
• Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering
• Senior Project: Real-time Chat Application using WebSocket and Node.js

PROJECTS

Personal Finance Tracker (2023)
• Built full-stack web application using React, Node.js, and PostgreSQL
• Implemented secure user authentication and data encryption
• Deployed on AWS with auto-scaling capabilities serving 1000+ users

Open Source Contributions
• Contributor to popular Python web framework with 50+ commits
• Maintained documentation and fixed critical bugs
• Active member of local tech community with 500+ GitHub contributions

CERTIFICATIONS & ACHIEVEMENTS
• AWS Certified Developer - Associate (2022)
• Certified ScrumMaster (CSM) - Scrum Alliance (2021)
• Winner of TechCorp Hackathon 2022 - Best Innovation Award
• Speaker at Women in Tech Conference 2023: "Building Inclusive Engineering Teams"

LANGUAGES
• English (Native)
• Spanish (Conversational)
• Mandarin (Basic)"""
    
    # Insert text with better formatting
    page.insert_text((50, 50), content, fontsize=9, fontname="helv")
    
    # Save to temporary file
    pdf_path = tempfile.mktemp(suffix='.pdf')
    doc.save(pdf_path)
    doc.close()
    
    return pdf_path

def test_upload_functionality():
    """Test the upload functionality with a real user"""
    print("🧪 Testing Resume Upload Functionality")
    print("=" * 50)
    
    # Create test user
    test_user = create_test_user()
    
    # Create test PDF
    print("📄 Creating comprehensive test PDF...")
    pdf_path = create_test_pdf()
    
    try:
        with app.app_context():
            # Simulate file upload
            with open(pdf_path, 'rb') as f:
                file_data = f.read()
                
            file_obj = FileStorage(
                stream=BytesIO(file_data),
                filename='sarah_johnson_resume.pdf',
                content_type='application/pdf'
            )
            
            print("🔍 Parsing uploaded file...")
            parsed_data = parse_resume_file(file_obj, 'sarah_johnson_resume.pdf')
            
            print(f"✅ Title: {parsed_data['title']}")
            print(f"✅ Content Length: {len(parsed_data['content']):,} characters")
            print(f"✅ Sections Found: {len(parsed_data['sections'])}")
            print(f"✅ Contact Info Fields: {len(parsed_data['contact_info'])}")
            
            print("\n👤 EXTRACTED CONTACT INFO:")
            for key, value in parsed_data['contact_info'].items():
                print(f"   • {key.title()}: {value}")
            
            print("\n📋 EXTRACTED SECTIONS:")
            for i, section in enumerate(parsed_data['sections'], 1):
                print(f"   {i:2d}. {section['title']:35} ({len(section['content']):,} chars)")
            
            # Create resume in database
            print("\n💾 Creating resume in database...")
            new_resume = Resume(
                user_id=test_user.id, 
                title=parsed_data['title'], 
                content=parsed_data['content'], 
                template='classic'
            )
            
            db.session.add(new_resume)
            db.session.commit()
            
            print(f"✅ Resume created with ID: {new_resume.id}")
            
            # Show content preview
            print("\n📝 CONTENT PREVIEW (first 500 characters):")
            print("-" * 50)
            print(parsed_data['content'][:500] + "...")
            print("-" * 50)
            
            print("\n🎉 UPLOAD FUNCTIONALITY TEST COMPLETE!")
            print("=" * 50)
            print("✅ PDF parsing working")
            print("✅ Content extraction working")  
            print("✅ Database integration working")
            print("✅ Resume creation working")
            
            print("\n🔐 TO TEST IN BROWSER:")
            print("1. Go to http://127.0.0.1:5006/login")
            print("2. Login with: test@example.com / password123")
            print("3. Navigate to 'Upload Existing Resume'")
            print("4. Upload any PDF file")
            print("5. You should be redirected to edit the extracted content")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        os.unlink(pdf_path)

if __name__ == "__main__":
    success = test_upload_functionality()
    
    if success:
        print("\n🚀 Upload functionality is working correctly!")
    else:
        print("\n⚠️  There are issues that need to be addressed.")
