#!/usr/bin/env python3
"""
Test Stripe API key configuration
"""

import os
import stripe
from dotenv import load_dotenv

def test_stripe_config():
    """Test if Stripe API keys are working"""
    print("🔑 STRIPE API KEY DIAGNOSTIC")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    stripe_secret = os.getenv('STRIPE_SECRET_KEY')
    stripe_publishable = os.getenv('STRIPE_PUBLISHABLE_KEY')
    
    print("1. Environment Variables:")
    if stripe_secret:
        print(f"   ✅ STRIPE_SECRET_KEY: {stripe_secret[:15]}...{stripe_secret[-4:]}")
    else:
        print("   ❌ STRIPE_SECRET_KEY: Not found")
        
    if stripe_publishable:
        print(f"   ✅ STRIPE_PUBLISHABLE_KEY: {stripe_publishable[:15]}...{stripe_publishable[-4:]}")
    else:
        print("   ❌ STRIPE_PUBLISHABLE_KEY: Not found")
    
    print("\n2. API Key Format:")
    if stripe_secret:
        if stripe_secret.startswith('sk_test_'):
            print("   ✅ Secret key format: Test key (correct format)")
        elif stripe_secret.startswith('sk_live_'):
            print("   ✅ Secret key format: Live key (correct format)")
        else:
            print("   ❌ Secret key format: Invalid format")
    
    if stripe_publishable:
        if stripe_publishable.startswith('pk_test_'):
            print("   ✅ Publishable key format: Test key (correct format)")
        elif stripe_publishable.startswith('pk_live_'):
            print("   ✅ Publishable key format: Live key (correct format)")
        else:
            print("   ❌ Publishable key format: Invalid format")
    
    print("\n3. Stripe API Connection Test:")
    if stripe_secret:
        try:
            stripe.api_key = stripe_secret
            
            # Test API connection
            account = stripe.Account.retrieve()
            print(f"   ✅ API Connection: Success")
            print(f"   📧 Account Email: {account.get('email', 'N/A')}")
            print(f"   🆔 Account ID: {account.get('id', 'N/A')}")
            
        except stripe.error.AuthenticationError as e:
            print(f"   ❌ API Authentication Error: {e}")
            print("   💡 This suggests the API key is invalid or has been revoked")
            
        except stripe.error.StripeError as e:
            print(f"   ❌ Stripe API Error: {e}")
            
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")
    
    print("\n4. Recommendations:")
    if stripe_secret and not stripe_secret.startswith(('sk_test_', 'sk_live_')):
        print("   🔧 Get new API keys from https://dashboard.stripe.com/apikeys")
    elif stripe_secret:
        print("   🔧 Check if API key was revoked in Stripe Dashboard")
        print("   🔧 Verify account is active and in good standing")
    else:
        print("   🔧 Set STRIPE_SECRET_KEY in .env file")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    test_stripe_config()
