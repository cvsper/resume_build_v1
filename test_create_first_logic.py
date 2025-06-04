#!/usr/bin/env python3
"""
Template Testing Script for Create First Buttons
Tests the conditional logic and button functionality
"""

import sys
import os
from jinja2 import Environment, FileSystemLoader

def test_template_rendering():
    """Test that templates render correctly with empty and non-empty data"""
    
    # Set up Jinja2 environment
    template_dir = '/Users/sevs/Documents/Programs/webapps/resume_builder/templates'
    env = Environment(loader=FileSystemLoader(template_dir))
    
    print("🧪 Testing Create First Buttons Template Logic")
    print("=" * 60)
    
    # Test data
    empty_data = []
    sample_data = [
        {'id': 1, 'title': 'Sample Item', 'created_at': '2024-01-01'}
    ]
    
    # Test resumes.html
    print("\n📄 Testing resumes.html")
    try:
        template = env.get_template('resumes.html')
        
        # Test with empty data
        result_empty = template.render(resumes=empty_data)
        if 'create-first-section' in result_empty:
            print("✅ Empty state: Shows 'Create Your First Resume' section")
        else:
            print("❌ Empty state: Missing create-first-section")
            
        if 'Create Resume' in result_empty:
            print("✅ Empty state: Contains 'Create Resume' button")
        else:
            print("❌ Empty state: Missing 'Create Resume' button")
        
        # Test with data
        result_data = template.render(resumes=sample_data)
        if 'create-first-section' not in result_data:
            print("✅ With data: Hides create-first-section")
        else:
            print("❌ With data: Still showing create-first-section")
            
    except Exception as e:
        print(f"❌ Error testing resumes.html: {e}")
    
    # Test cover_letters.html
    print("\n📧 Testing cover_letters.html")
    try:
        template = env.get_template('cover_letters.html')
        
        # Test with empty data
        result_empty = template.render(cover_letters=empty_data)
        if 'Create Your First Cover Letter' in result_empty:
            print("✅ Empty state: Shows 'Create Your First Cover Letter' section")
        else:
            print("❌ Empty state: Missing create first cover letter text")
            
        # Test with data
        result_data = template.render(cover_letters=sample_data)
        if 'create-first-section' not in result_data:
            print("✅ With data: Hides create-first-section")
        else:
            print("❌ With data: Still showing create-first-section")
            
    except Exception as e:
        print(f"❌ Error testing cover_letters.html: {e}")
    
    # Test interview_qa.html
    print("\n🎤 Testing interview_qa.html")
    try:
        template = env.get_template('interview_qa.html')
        
        # Test with empty data
        result_empty = template.render(interview_qa_list=empty_data)
        if 'Create Your First Interview Q&A' in result_empty:
            print("✅ Empty state: Shows 'Create Your First Interview Q&A' section")
        else:
            print("❌ Empty state: Missing create first interview Q&A text")
            
        if 'job_title' in result_empty and 'form' in result_empty:
            print("✅ Empty state: Contains inline form with job_title input")
        else:
            print("❌ Empty state: Missing form elements")
            
        # Test with data
        result_data = template.render(interview_qa_list=sample_data)
        if 'create-first-section' not in result_data:
            print("✅ With data: Hides create-first-section")
        else:
            print("❌ With data: Still showing create-first-section")
            
    except Exception as e:
        print(f"❌ Error testing interview_qa.html: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Template Logic Testing Complete")
    print("\n🚀 Next Steps:")
    print("1. Test with actual Flask app")
    print("2. Verify button links work correctly")
    print("3. Test responsive design on different screen sizes")
    print("4. Validate create-first sections disappear after creating first item")

if __name__ == '__main__':
    test_template_rendering()
