#!/usr/bin/env python3
"""
Production Stripe Integration Test
Tests the exact scenario that's failing in production
"""

import requests
import os
from dotenv import load_dotenv
import stripe

def test_production_stripe_issue():
    print("🔍 TESTING PRODUCTION STRIPE INTEGRATION ISSUE")
    print("="*55)
    
    # Load environment variables
    load_dotenv()
    
    # Check Stripe keys
    stripe_secret = os.getenv('STRIPE_SECRET_KEY')
    stripe_publishable = os.getenv('STRIPE_PUBLISHABLE_KEY')
    
    print(f"1. Checking Stripe keys...")
    if stripe_secret:
        print(f"   ✅ Stripe secret key found: {stripe_secret[:20]}...")
    else:
        print("   ❌ Stripe secret key missing")
        return False
        
    if stripe_publishable:
        print(f"   ✅ Stripe publishable key found: {stripe_publishable[:20]}...")
    else:
        print("   ❌ Stripe publishable key missing")
        
    # Test Stripe API connectivity
    print(f"\n2. Testing Stripe API connectivity...")
    try:
        stripe.api_key = stripe_secret
        account = stripe.Account.retrieve()
        print(f"   ✅ Stripe API connection successful")
        print(f"   Account ID: {account.id}")
    except Exception as e:
        print(f"   ❌ Stripe API error: {e}")
        return False
    
    # Test checkout session creation (similar to production scenario)
    print(f"\n3. Testing checkout session creation...")
    try:
        test_checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd', 
                    'unit_amount': 499, 
                    'product_data': {
                        'name': 'Resume PDF Download',
                        'description': 'Test Resume Download'
                    }
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://resume-build-v1.onrender.com/payment-success?resume_id=1',
            cancel_url='https://resume-build-v1.onrender.com/preview-resume-payment/1',
            metadata={
                'user_id': 'test_user',
                'resume_id': '1',
                'type': 'resume_download'
            }
        )
        print(f"   ✅ Checkout session created successfully")
        print(f"   Session ID: {test_checkout_session.id}")
        print(f"   Session URL: {test_checkout_session.url[:60]}...")
        
    except Exception as e:
        print(f"   ❌ Checkout session creation failed: {e}")
        return False
    
    print(f"\n4. Potential issues causing 400 errors:")
    print("   • Missing or invalid resume_id in POST data")
    print("   • Database connection issues")
    print("   • Resume ownership validation failures") 
    print("   • Stripe API rate limiting")
    print("   • Content-Type header issues from mobile browsers")
    
    print(f"\n🔧 RECOMMENDATIONS:")
    print("1. Check server logs for detailed error messages")
    print("2. Verify database connectivity on production")
    print("3. Test with different mobile browsers")
    print("4. Check if POST data is being sent correctly from mobile")
    print("5. Verify CSRF token handling (if enabled)")
    
    return True

if __name__ == "__main__":
    test_production_stripe_issue()
