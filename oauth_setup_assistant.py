#!/usr/bin/env python3
"""
OAuth Configuration Setup Script
This script helps setup OAuth applications for Google and LinkedIn
"""

import os
import webbrowser
from urllib.parse import quote

def setup_google_oauth():
    """Guide for setting up Google OAuth"""
    print("🔵 GOOGLE OAUTH SETUP")
    print("=" * 40)
    print("1. Visit Google Cloud Console")
    print("2. Create a new project or select existing")
    print("3. Enable Google+ API")
    print("4. Create OAuth 2.0 credentials")
    print("5. Add authorized redirect URIs:")
    print("   - Development: http://127.0.0.1:5006/callback/google")
    print("   - Production: https://yourdomain.com/callback/google")
    print("\nOpening Google Cloud Console...")
    
    try:
        webbrowser.open('https://console.cloud.google.com/apis/credentials')
    except:
        print("Please manually visit: https://console.cloud.google.com/apis/credentials")
    
    print("\nAfter creating credentials, update your .env file:")
    print("GOOGLE_CLIENT_ID=your_google_client_id_here")
    print("GOOGLE_CLIENT_SECRET=your_google_client_secret_here")

def setup_linkedin_oauth():
    """Guide for setting up LinkedIn OAuth"""
    print("\n🔷 LINKEDIN OAUTH SETUP")
    print("=" * 40)
    print("1. Visit LinkedIn Developers")
    print("2. Create a new app")
    print("3. Add required scopes:")
    print("   - r_liteprofile (basic profile)")
    print("   - r_emailaddress (email address)")
    print("4. Add authorized redirect URIs:")
    print("   - Development: http://127.0.0.1:5006/callback/linkedin")
    print("   - Production: https://yourdomain.com/callback/linkedin")
    print("\nOpening LinkedIn Developers...")
    
    try:
        webbrowser.open('https://www.linkedin.com/developers/apps')
    except:
        print("Please manually visit: https://www.linkedin.com/developers/apps")
    
    print("\nAfter creating app, update your .env file:")
    print("LINKEDIN_CLIENT_ID=your_linkedin_client_id_here")
    print("LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here")

def setup_test_oauth_credentials():
    """Set up test/demo OAuth credentials for development"""
    print("\n🔧 SETTING UP TEST CREDENTIALS")
    print("=" * 40)
    print("For development and testing, you can use placeholder credentials.")
    print("The app will work without real OAuth until you're ready to configure it.")
    
    env_file_path = '/Users/sevs/Documents/Programs/webapps/resume_builder/.env'
    
    # Read current .env file
    with open(env_file_path, 'r') as f:
        content = f.read()
    
    # Check if OAuth credentials are already set to real values
    has_real_google = 'GOOGLE_CLIENT_ID=your_google_client_id_here' not in content
    has_real_linkedin = 'LINKEDIN_CLIENT_ID=your_linkedin_client_id_here' not in content
    
    if has_real_google and has_real_linkedin:
        print("✅ OAuth credentials appear to be configured!")
        return
    
    print("\n⚠️  OAuth credentials are still placeholder values.")
    print("The social sign-in buttons will show appropriate messages until configured.")
    
def test_oauth_endpoints():
    """Test OAuth endpoints"""
    import requests
    
    print("\n🧪 TESTING OAUTH ENDPOINTS")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:5006"
    endpoints = [
        ('/auth/google', 'Google OAuth Start'),
        ('/auth/linkedin', 'LinkedIn OAuth Start'),
        ('/auth/apple', 'Apple OAuth Start'),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", allow_redirects=False)
            print(f"   {name}: {response.status_code}")
            if response.status_code == 302:
                print(f"      → Redirects to: {response.headers.get('Location', 'Unknown')[:50]}...")
        except Exception as e:
            print(f"   {name}: Error - {str(e)}")

def main():
    print("🔐 OAUTH SETUP ASSISTANT")
    print("=" * 50)
    print("This script will help you set up OAuth authentication")
    print("for Google, LinkedIn, and Apple Sign-In.\n")
    
    setup_google_oauth()
    setup_linkedin_oauth()
    setup_test_oauth_credentials()
    test_oauth_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ OAuth setup guide complete!")
    print("\n📋 Next Steps:")
    print("1. Configure OAuth apps using the opened browser tabs")
    print("2. Update .env file with real credentials")
    print("3. Test social sign-in on your application")
    print("4. Check /Users/sevs/Documents/Programs/webapps/resume_builder/OAUTH_SETUP_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()
