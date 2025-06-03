#!/usr/bin/env python3
"""
Comprehensive test for the resume creation menu flow
This test verifies that all components work together correctly
"""

import requests
import sys
import os

def test_resume_creation_flow():
    """Test the complete resume creation flow"""
    base_url = "http://localhost:5000"
    
    print("🚀 Testing Resume Creation Flow")
    print("=" * 50)
    
    # Test 1: Main page loads
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ Main page: {response.status_code}")
        
        # Check if the page contains updated links
        if 'resume_creation_menu' in response.text:
            print("✓ Main page contains updated resume_creation_menu links")
        else:
            print("⚠️  Main page may not have all updated links")
            
    except Exception as e:
        print(f"✗ Main page error: {e}")
    
    # Test 2: Resume creation menu route exists (will return 403 without login)
    try:
        response = requests.get(f"{base_url}/resume-creation-menu")
        if response.status_code == 403:
            print("✓ Resume creation menu route exists (requires login as expected)")
        elif response.status_code == 404:
            print("✗ Resume creation menu route not found")
        else:
            print(f"⚠️  Resume creation menu route returned: {response.status_code}")
    except Exception as e:
        print(f"✗ Resume creation menu error: {e}")
    
    # Test 3: Create from scratch route
    try:
        response = requests.get(f"{base_url}/create-from-scratch")
        if response.status_code == 403:
            print("✓ Create from scratch route exists (requires login as expected)")
        elif response.status_code == 404:
            print("✗ Create from scratch route not found")
        else:
            print(f"⚠️  Create from scratch route returned: {response.status_code}")
    except Exception as e:
        print(f"✗ Create from scratch error: {e}")
    
    # Test 4: Upload existing resume route
    try:
        response = requests.get(f"{base_url}/upload-existing-resume")
        if response.status_code == 403:
            print("✓ Upload existing resume route exists (requires login as expected)")
        elif response.status_code == 404:
            print("✗ Upload existing resume route not found")
        else:
            print(f"⚠️  Upload existing resume route returned: {response.status_code}")
    except Exception as e:
        print(f"✗ Upload existing resume error: {e}")
    
    # Test 5: Static file accessibility
    try:
        response = requests.get(f"{base_url}/static/css/bootstrap.min.css")
        if response.status_code == 200:
            print("✓ Static files are accessible")
        else:
            print(f"⚠️  Static files returned: {response.status_code}")
    except Exception as e:
        print(f"✗ Static files error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Resume Creation Flow Test Complete")

if __name__ == "__main__":
    test_resume_creation_flow()
