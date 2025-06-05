#!/usr/bin/env python3
"""
Stripe Payment Flow Manual Testing Script
This script guides you through testing the complete Stripe payment integration.
"""

import webbrowser
import time
from colorama import init, Fore, Style, Back

# Initialize colorama
init()

def print_header(text):
    print(f"\n{Back.GREEN}{Fore.WHITE}{'='*80}{Style.RESET_ALL}")
    print(f"{Back.GREEN}{Fore.WHITE}{text.center(80)}{Style.RESET_ALL}")
    print(f"{Back.GREEN}{Fore.WHITE}{'='*80}{Style.RESET_ALL}\n")

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

def wait_for_user(message="Press Enter to continue..."):
    return input(f"\n{Fore.YELLOW}{message}{Style.RESET_ALL}")

def test_successful_payment():
    """Test successful payment flow"""
    print_header("TEST 1: SUCCESSFUL PAYMENT")
    
    print_step(1, "Navigate to payment page")
    print_info("Go to a premium feature that requires payment")
    
    if wait_for_user("Open payment page? (y/n): ").lower() == 'y':
        webbrowser.open('http://127.0.0.1:5006/payment')
    
    print_step(2, "Fill payment form with test card")
    print_info("Use the following test card details:")
    print(f"   Card Number: {Fore.GREEN}4242 4242 4242 4242{Style.RESET_ALL}")
    print(f"   Expiry: {Fore.GREEN}12/34{Style.RESET_ALL} (any future date)")
    print(f"   CVC: {Fore.GREEN}123{Style.RESET_ALL} (any 3 digits)")
    print(f"   Name: {Fore.GREEN}Test User{Style.RESET_ALL}")
    
    wait_for_user()
    
    print_step(3, "Submit payment")
    print_info("Click 'Complete Payment' or similar button")
    
    result = wait_for_user("Was payment successful? (y/n): ")
    if result.lower() == 'y':
        print_success("Successful payment test passed!")
        return True
    else:
        print_error("Successful payment test failed")
        return False

def test_declined_payment():
    """Test declined payment flow"""
    print_header("TEST 2: DECLINED PAYMENT")
    
    print_step(1, "Navigate to payment page again")
    print_info("Go back to the payment form")
    
    print_step(2, "Use declined test card")
    print_info("Use the following test card details:")
    print(f"   Card Number: {Fore.RED}4000 0000 0000 0002{Style.RESET_ALL}")
    print(f"   Expiry: {Fore.GREEN}12/34{Style.RESET_ALL}")
    print(f"   CVC: {Fore.GREEN}123{Style.RESET_ALL}")
    print(f"   Name: {Fore.GREEN}Test User{Style.RESET_ALL}")
    
    wait_for_user()
    
    print_step(3, "Submit payment")
    print_info("This should be declined by Stripe")
    
    result = wait_for_user("Was payment properly declined with error message? (y/n): ")
    if result.lower() == 'y':
        print_success("Declined payment test passed!")
        return True
    else:
        print_error("Declined payment test failed")
        return False

def test_3d_secure():
    """Test 3D Secure authentication"""
    print_header("TEST 3: 3D SECURE AUTHENTICATION")
    
    print_step(1, "Navigate to payment page")
    print_info("Go back to the payment form")
    
    print_step(2, "Use 3D Secure test card")
    print_info("Use the following test card details:")
    print(f"   Card Number: {Fore.YELLOW}4000 0027 6000 3184{Style.RESET_ALL}")
    print(f"   Expiry: {Fore.GREEN}12/34{Style.RESET_ALL}")
    print(f"   CVC: {Fore.GREEN}123{Style.RESET_ALL}")
    print(f"   Name: {Fore.GREEN}Test User{Style.RESET_ALL}")
    
    wait_for_user()
    
    print_step(3, "Complete 3D Secure flow")
    print_info("Should redirect to 3D Secure authentication")
    print_info("Click 'Complete authentication' in the test modal")
    
    result = wait_for_user("Did 3D Secure authentication work? (y/n): ")
    if result.lower() == 'y':
        print_success("3D Secure test passed!")
        return True
    else:
        print_error("3D Secure test failed")
        return False

def test_insufficient_funds():
    """Test insufficient funds scenario"""
    print_header("TEST 4: INSUFFICIENT FUNDS")
    
    print_step(1, "Use insufficient funds test card")
    print_info("Use the following test card details:")
    print(f"   Card Number: {Fore.RED}4000 0000 0000 9995{Style.RESET_ALL}")
    print(f"   Expiry: {Fore.GREEN}12/34{Style.RESET_ALL}")
    print(f"   CVC: {Fore.GREEN}123{Style.RESET_ALL}")
    print(f"   Name: {Fore.GREEN}Test User{Style.RESET_ALL}")
    
    wait_for_user()
    
    result = wait_for_user("Was payment declined with insufficient funds error? (y/n): ")
    if result.lower() == 'y':
        print_success("Insufficient funds test passed!")
        return True
    else:
        print_error("Insufficient funds test failed")
        return False

def test_webhook_handling():
    """Test webhook handling"""
    print_header("TEST 5: WEBHOOK HANDLING")
    
    print_info("Webhooks are automatically tested when payments are processed")
    print_info("Check the Flask console logs for webhook events:")
    print("   - payment_intent.succeeded")
    print("   - payment_intent.payment_failed")
    print("   - invoice.payment_succeeded")
    
    print_step(1, "Check Flask logs")
    print_info("Look for webhook event logs in your Flask console")
    
    result = wait_for_user("Are webhook events being logged? (y/n): ")
    if result.lower() == 'y':
        print_success("Webhook test passed!")
        return True
    else:
        print_warning("Check webhook endpoint configuration")
        return False

def test_subscription_flow():
    """Test subscription payment flow"""
    print_header("TEST 6: SUBSCRIPTION FLOW")
    
    print_step(1, "Test monthly subscription")
    print_info("If your app has subscription features, test monthly billing")
    
    print_step(2, "Test subscription cancellation")
    print_info("Test the subscription cancellation flow")
    
    print_step(3, "Test subscription renewal")
    print_info("Simulate subscription renewal")
    
    result = wait_for_user("Does subscription flow work correctly? (y/n/skip): ")
    if result.lower() == 'y':
        print_success("Subscription test passed!")
        return True
    elif result.lower() == 'skip':
        print_warning("Subscription test skipped")
        return True
    else:
        print_error("Subscription test failed")
        return False

def test_payment_methods():
    """Test different payment methods"""
    print_header("TEST 7: PAYMENT METHODS")
    
    print_info("Test different card types:")
    
    cards = [
        ("Visa", "4242 4242 4242 4242"),
        ("Mastercard", "5555 5555 5555 4444"),
        ("American Express", "3782 822463 10005"),
        ("Discover", "6011 1111 1111 1117"),
        ("Diners Club", "3056 9300 0902 0004")
    ]
    
    for card_type, card_number in cards:
        print(f"   {card_type}: {Fore.GREEN}{card_number}{Style.RESET_ALL}")
    
    result = wait_for_user("Test different card types? (y/n): ")
    if result.lower() == 'y':
        for card_type, card_number in cards:
            print(f"\nTesting {card_type}...")
            test_result = wait_for_user(f"Did {card_type} work? (y/n): ")
            if test_result.lower() == 'y':
                print_success(f"{card_type} test passed!")
            else:
                print_error(f"{card_type} test failed")
        return True
    else:
        print_warning("Payment methods test skipped")
        return True

def generate_test_report(results):
    """Generate a test report"""
    print_header("PAYMENT TESTING REPORT")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Fore.GREEN}{passed_tests}{Style.RESET_ALL}")
    print(f"Failed: {Fore.RED}{total_tests - passed_tests}{Style.RESET_ALL}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = f"{Fore.GREEN}✅ PASS{Style.RESET_ALL}" if result else f"{Fore.RED}❌ FAIL{Style.RESET_ALL}"
        print(f"   {test_name}: {status}")
    
    if passed_tests == total_tests:
        print(f"\n{Fore.GREEN}🎉 ALL PAYMENT TESTS PASSED!{Style.RESET_ALL}")
        print("Your Stripe integration is working correctly.")
    else:
        print(f"\n{Fore.YELLOW}⚠️  SOME TESTS FAILED{Style.RESET_ALL}")
        print("Review failed tests and check your Stripe configuration.")

def main():
    print_header("STRIPE PAYMENT FLOW TESTING")
    
    print("This script will guide you through comprehensive testing of your Stripe payment integration.")
    print("Make sure your Flask application is running on http://127.0.0.1:5006")
    
    if wait_for_user("Ready to start testing? (y/n): ").lower() != 'y':
        print("Testing cancelled.")
        return
    
    # Dictionary to store test results
    results = {}
    
    # Run all tests
    results["Successful Payment"] = test_successful_payment()
    results["Declined Payment"] = test_declined_payment()
    results["3D Secure"] = test_3d_secure()
    results["Insufficient Funds"] = test_insufficient_funds()
    results["Webhook Handling"] = test_webhook_handling()
    results["Subscription Flow"] = test_subscription_flow()
    results["Payment Methods"] = test_payment_methods()
    
    # Generate report
    generate_test_report(results)
    
    print(f"\n{Fore.CYAN}Additional Testing Resources:{Style.RESET_ALL}")
    print("• Stripe Test Cards: https://stripe.com/docs/testing")
    print("• Webhook Testing: Use Stripe CLI for local testing")
    print("• Error Handling: Check Stripe dashboard for detailed logs")
    
    print_header("TESTING COMPLETE")

if __name__ == "__main__":
    main()
