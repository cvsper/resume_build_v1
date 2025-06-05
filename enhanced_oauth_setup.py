#!/usr/bin/env python3
"""
Enhanced OAuth Setup Assistant for Resume Builder
This script provides interactive guidance for setting up OAuth credentials.
"""

import os
import webbrowser
import time
from colorama import init, Fore, Style, Back

# Initialize colorama
init()

def print_header(text):
    print(f"\n{Back.BLUE}{Fore.WHITE}{'='*80}{Style.RESET_ALL}")
    print(f"{Back.BLUE}{Fore.WHITE}{text.center(80)}{Style.RESET_ALL}")
    print(f"{Back.BLUE}{Fore.WHITE}{'='*80}{Style.RESET_ALL}\n")

def print_step(step_num, description):
    print(f"{Fore.CYAN}Step {step_num}:{Style.RESET_ALL} {description}")

def print_success(message):
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")

def wait_for_user():
    return input(f"\n{Fore.YELLOW}Press Enter to continue or 'q' to quit: {Style.RESET_ALL}")

def check_env_file():
    """Check if .env file exists and has OAuth placeholders"""
    env_path = '.env'
    if not os.path.exists(env_path):
        print_error(".env file not found!")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
        
    google_placeholder = 'your_google_client_id_here' in content
    linkedin_placeholder = 'your_linkedin_client_id_here' in content
    
    if google_placeholder and linkedin_placeholder:
        print_warning("OAuth credentials are still using placeholder values")
        return True
    elif google_placeholder or linkedin_placeholder:
        print_warning("Some OAuth credentials are configured, others need setup")
        return True
    else:
        print_success("OAuth credentials appear to be configured")
        return True

def update_env_credentials(provider, client_id, client_secret):
    """Update .env file with new OAuth credentials"""
    env_path = '.env'
    
    # Read current content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update the specific provider credentials
    updated_lines = []
    for line in lines:
        if provider.upper() in line and 'CLIENT_ID' in line:
            updated_lines.append(f"{provider.upper()}_CLIENT_ID={client_id}\n")
        elif provider.upper() in line and 'CLIENT_SECRET' in line:
            updated_lines.append(f"{provider.upper()}_CLIENT_SECRET={client_secret}\n")
        else:
            updated_lines.append(line)
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print_success(f"{provider.title()} credentials updated in .env file")

def setup_google_oauth():
    """Interactive Google OAuth setup"""
    print_header("GOOGLE OAUTH SETUP")
    
    print_step(1, "Opening Google Cloud Console")
    print_info("Opening: https://console.developers.google.com/")
    
    if input("Open Google Cloud Console? (y/n): ").lower() == 'y':
        webbrowser.open('https://console.developers.google.com/')
    
    print_step(2, "Create or Select Project")
    print_info("1. Create a new project or select an existing one")
    print_info("2. Give it a name like 'Resume Builder App'")
    
    wait_for_user()
    
    print_step(3, "Enable Google+ API")
    print_info("1. Go to 'APIs & Services' > 'Library'")
    print_info("2. Search for 'Google+ API'")
    print_info("3. Click 'Enable'")
    
    wait_for_user()
    
    print_step(4, "Create OAuth 2.0 Credentials")
    print_info("1. Go to 'APIs & Services' > 'Credentials'")
    print_info("2. Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print_info("3. Choose 'Web application'")
    print_info("4. Add authorized redirect URI:")
    print(f"   {Fore.GREEN}http://127.0.0.1:5006/auth/google/callback{Style.RESET_ALL}")
    print_info("5. For production, also add your domain:")
    print(f"   {Fore.GREEN}https://yourdomain.com/auth/google/callback{Style.RESET_ALL}")
    
    wait_for_user()
    
    print_step(5, "Copy Credentials")
    print_info("After creating, copy the Client ID and Client Secret")
    
    client_id = input(f"{Fore.CYAN}Enter Google Client ID: {Style.RESET_ALL}")
    client_secret = input(f"{Fore.CYAN}Enter Google Client Secret: {Style.RESET_ALL}")
    
    if client_id and client_secret:
        update_env_credentials('google', client_id, client_secret)
        return True
    else:
        print_warning("Credentials not provided, skipping update")
        return False

def setup_linkedin_oauth():
    """Interactive LinkedIn OAuth setup"""
    print_header("LINKEDIN OAUTH SETUP")
    
    print_step(1, "Opening LinkedIn Developers")
    print_info("Opening: https://www.linkedin.com/developers/")
    
    if input("Open LinkedIn Developers? (y/n): ").lower() == 'y':
        webbrowser.open('https://www.linkedin.com/developers/')
    
    print_step(2, "Create New App")
    print_info("1. Click 'Create App'")
    print_info("2. Fill in app details:")
    print_info("   - App name: Resume Builder")
    print_info("   - Company: Your company or personal")
    print_info("   - Privacy policy URL: (required)")
    print_info("   - App logo: Upload a logo")
    
    wait_for_user()
    
    print_step(3, "Configure OAuth Settings")
    print_info("1. Go to 'Auth' tab")
    print_info("2. Add authorized redirect URL:")
    print(f"   {Fore.GREEN}http://127.0.0.1:5006/auth/linkedin/callback{Style.RESET_ALL}")
    print_info("3. For production, also add:")
    print(f"   {Fore.GREEN}https://yourdomain.com/auth/linkedin/callback{Style.RESET_ALL}")
    
    wait_for_user()
    
    print_step(4, "Request Permissions")
    print_info("1. Go to 'Products' tab")
    print_info("2. Request 'Sign In with LinkedIn'")
    print_info("3. May require approval process")
    
    wait_for_user()
    
    print_step(5, "Copy Credentials")
    print_info("Go to 'Auth' tab and copy Client ID and Client Secret")
    
    client_id = input(f"{Fore.CYAN}Enter LinkedIn Client ID: {Style.RESET_ALL}")
    client_secret = input(f"{Fore.CYAN}Enter LinkedIn Client Secret: {Style.RESET_ALL}")
    
    if client_id and client_secret:
        update_env_credentials('linkedin', client_id, client_secret)
        return True
    else:
        print_warning("Credentials not provided, skipping update")
        return False

def test_oauth_integration():
    """Test OAuth integration after setup"""
    print_header("TESTING OAUTH INTEGRATION")
    
    print_step(1, "Restart Flask Application")
    print_info("The Flask app needs to be restarted to load new credentials")
    print_warning("Please restart your Flask application and return here")
    
    wait_for_user()
    
    print_step(2, "Test Social Login")
    print_info("1. Go to: http://127.0.0.1:5006/login")
    print_info("2. Click 'Sign in with Google' or 'Sign in with LinkedIn'")
    print_info("3. Complete the OAuth flow")
    print_info("4. Should redirect back to dashboard")
    
    if input("Open login page for testing? (y/n): ").lower() == 'y':
        webbrowser.open('http://127.0.0.1:5006/login')
    
    wait_for_user()
    
    result = input("Did OAuth login work successfully? (y/n): ")
    if result.lower() == 'y':
        print_success("OAuth integration working correctly!")
        return True
    else:
        print_error("OAuth integration needs troubleshooting")
        return False

def troubleshoot_oauth():
    """Provide troubleshooting guidance"""
    print_header("OAUTH TROUBLESHOOTING")
    
    print_info("Common issues and solutions:")
    print("1. 'Invalid client_id' error:")
    print("   - Check .env file has correct CLIENT_ID")
    print("   - Verify credentials are not placeholder values")
    
    print("2. 'Redirect URI mismatch' error:")
    print("   - Check redirect URI in OAuth app settings")
    print("   - Must exactly match: http://127.0.0.1:5006/auth/[provider]/callback")
    
    print("3. 'App not approved' error (LinkedIn):")
    print("   - LinkedIn may require app approval")
    print("   - Check developer console for approval status")
    
    print("4. Flask app not loading new credentials:")
    print("   - Restart Flask application")
    print("   - Check .env file is in correct directory")
    
    print("5. Still having issues?")
    print("   - Check Flask logs for detailed error messages")
    print("   - Verify API keys are active and not expired")

def main():
    print_header("ENHANCED OAUTH SETUP ASSISTANT")
    
    print("This assistant will guide you through setting up OAuth credentials")
    print("for Google and LinkedIn social authentication.")
    
    # Check current status
    if not check_env_file():
        return
    
    while True:
        print(f"\n{Fore.CYAN}Choose an option:{Style.RESET_ALL}")
        print("1. Setup Google OAuth")
        print("2. Setup LinkedIn OAuth")
        print("3. Test OAuth Integration")
        print("4. Troubleshoot OAuth Issues")
        print("5. View Current Status")
        print("6. Exit")
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice (1-6): {Style.RESET_ALL}")
        
        if choice == '1':
            setup_google_oauth()
        elif choice == '2':
            setup_linkedin_oauth()
        elif choice == '3':
            test_oauth_integration()
        elif choice == '4':
            troubleshoot_oauth()
        elif choice == '5':
            check_env_file()
        elif choice == '6':
            print_success("OAuth setup assistant completed!")
            break
        else:
            print_error("Invalid choice, please try again")

if __name__ == "__main__":
    main()
