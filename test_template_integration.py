#!/usr/bin/env python3
"""
Test script to verify template integration is working correctly
"""

import os
import sys

def test_template_files():
    """Test that all template files exist"""
    templates_dir = "templates/resume_templates"
    expected_templates = [
        'classic.html',
        'modern.html', 
        'elegant.html',
        'minimal.html',
        'professional.html',
        'executive.html',
        'creative.html'
    ]
    
    print("Testing template files...")
    missing_templates = []
    
    for template in expected_templates:
        template_path = os.path.join(templates_dir, template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
        else:
            print(f"✅ {template} exists")
    
    if missing_templates:
        print(f"❌ Missing templates: {missing_templates}")
        return False
    
    print("✅ All template files exist")
    return True

def test_thumbnail_files():
    """Test that all thumbnail files exist"""
    thumbnails_dir = "static/img/templates"
    expected_thumbnails = [
        'classic.png',
        'modern.png',
        'elegant.png', 
        'minimal.png',
        'professional.png',
        'executive.png',
        'creative.png'
    ]
    
    print("\nTesting thumbnail files...")
    missing_thumbnails = []
    
    for thumbnail in expected_thumbnails:
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail)
        if not os.path.exists(thumbnail_path):
            missing_thumbnails.append(thumbnail)
        else:
            # Check file size to ensure it's not empty
            file_size = os.path.getsize(thumbnail_path)
            if file_size > 0:
                print(f"✅ {thumbnail} exists ({file_size} bytes)")
            else:
                print(f"⚠️  {thumbnail} exists but is empty")
                missing_thumbnails.append(thumbnail)
    
    if missing_thumbnails:
        print(f"❌ Missing or empty thumbnails: {missing_thumbnails}")
        return False
        
    print("✅ All thumbnail files exist and have content")
    return True

def test_template_content():
    """Test basic template file content"""
    templates_dir = "templates/resume_templates"
    expected_templates = ['classic.html', 'modern.html', 'elegant.html', 'minimal.html', 'professional.html', 'executive.html', 'creative.html']
    
    print("\nTesting template content...")
    
    for template in expected_templates:
        template_path = os.path.join(templates_dir, template)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic checks
            if len(content) < 100:
                print(f"⚠️  {template} seems too short ({len(content)} chars)")
            elif 'resume.title' in content or 'resume.content' in content:
                print(f"✅ {template} has expected template variables")
            else:
                print(f"⚠️  {template} might be missing template variables")
                
        except Exception as e:
            print(f"❌ Error reading {template}: {e}")
            return False
    
    print("✅ All templates have basic content")
    return True

def main():
    print("Resume Template Integration Test")
    print("=" * 40)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    tests = [
        test_template_files,
        test_thumbnail_files, 
        test_template_content
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All tests passed! Template integration is complete.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
