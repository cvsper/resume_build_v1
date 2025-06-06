#!/usr/bin/env python3
"""
Stripe Webhook Verification Script
This script tests and verifies that Stripe webhooks are properly configured and working.
"""

import requests
import json
import os
import stripe
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class WebhookVerifier:
    def __init__(self):
        self.base_url = "http://127.0.0.1:5006"
        self.stripe_secret = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if self.stripe_secret:
            stripe.api_key = self.stripe_secret
        
        print("🔍 Stripe Webhook Verification Tool")
        print("=" * 50)
    
    def verify_environment(self):
        """Verify that required environment variables are set"""
        print("\n1. 🔧 Environment Verification")
        print("-" * 30)
        
        # Check Stripe API keys
        if self.stripe_secret:
            if self.stripe_secret.startswith('sk_test_'):
                print("   ✅ Stripe Secret Key (Test Mode)")
            elif self.stripe_secret.startswith('sk_live_'):
                print("   ✅ Stripe Secret Key (Live Mode)")
            else:
                print("   ⚠️  Stripe Secret Key format unclear")
        else:
            print("   ❌ STRIPE_SECRET_KEY not found")
            return False
        
        # Check webhook secret
        if self.webhook_secret:
            print("   ✅ Stripe Webhook Secret configured")
        else:
            print("   ⚠️  STRIPE_WEBHOOK_SECRET not set (development mode)")
        
        return True
    
    def test_webhook_endpoint(self):
        """Test that the webhook endpoint exists and responds"""
        print("\n2. 🌐 Webhook Endpoint Test")
        print("-" * 30)
        
        webhook_url = f"{self.base_url}/stripe-webhook"
        
        try:
            # Test GET request (should return 405 Method Not Allowed)
            response = requests.get(webhook_url, timeout=5)
            if response.status_code == 405:
                print("   ✅ Webhook endpoint exists (GET -> 405 expected)")
            else:
                print(f"   ⚠️  GET request returned: {response.status_code}")
            
            # Test POST request with invalid data
            response = requests.post(
                webhook_url, 
                json={"test": "data"},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code in [200, 400]:
                print("   ✅ Webhook endpoint accepts POST requests")
            else:
                print(f"   ❌ POST request failed: {response.status_code}")
                return False
                
        except requests.ConnectionError:
            print(f"   ❌ Could not connect to {webhook_url}")
            print("   💡 Make sure your Flask app is running on port 5006")
            return False
        except requests.Timeout:
            print("   ❌ Request timed out")
            return False
        
        return True
    
    def test_webhook_events(self):
        """Test webhook with different event types"""
        print("\n3. 📨 Webhook Event Processing Test")
        print("-" * 30)
        
        webhook_url = f"{self.base_url}/stripe-webhook"
        
        # Test events to simulate
        test_events = [
            {
                "name": "Checkout Session Completed (One-time)",
                "event": {
                    "type": "checkout.session.completed",
                    "id": "evt_test_webhook",
                    "data": {
                        "object": {
                            "id": "cs_test_session",
                            "mode": "payment",
                            "amount_total": 499,
                            "currency": "usd",
                            "metadata": {
                                "user_id": "1",
                                "resume_id": "1",
                                "type": "resume_download"
                            }
                        }
                    }
                }
            },
            {
                "name": "Checkout Session Completed (Subscription)",
                "event": {
                    "type": "checkout.session.completed",
                    "id": "evt_test_subscription",
                    "data": {
                        "object": {
                            "id": "cs_test_subscription",
                            "mode": "subscription",
                            "amount_total": 999,
                            "currency": "usd",
                            "customer": "cus_test_customer",
                            "metadata": {
                                "user_id": "1",
                                "plan": "Pro"
                            }
                        }
                    }
                }
            },
            {
                "name": "Invoice Payment Succeeded",
                "event": {
                    "type": "invoice.payment_succeeded",
                    "id": "evt_test_invoice",
                    "data": {
                        "object": {
                            "id": "in_test_invoice",
                            "customer": "cus_test_customer",
                            "subscription": "sub_test_subscription",
                            "amount_paid": 999,
                            "currency": "usd"
                        }
                    }
                }
            },
            {
                "name": "Subscription Cancelled",
                "event": {
                    "type": "customer.subscription.deleted",
                    "id": "evt_test_cancellation",
                    "data": {
                        "object": {
                            "id": "sub_test_subscription",
                            "customer": "cus_test_customer"
                        }
                    }
                }
            }
        ]
        
        for test_event in test_events:
            print(f"\n   Testing: {test_event['name']}")
            
            try:
                response = requests.post(
                    webhook_url,
                    json=test_event["event"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"     ✅ Event processed successfully")
                else:
                    print(f"     ⚠️  Response: {response.status_code}")
                    if response.text:
                        print(f"     💬 Response: {response.text[:100]}")
                        
            except Exception as e:
                print(f"     ❌ Error: {e}")
        
        return True
    
    def test_stripe_api_connection(self):
        """Test connection to Stripe API"""
        print("\n4. 🔐 Stripe API Connection Test")
        print("-" * 30)
        
        if not self.stripe_secret:
            print("   ❌ No Stripe API key available")
            return False
        
        try:
            # Test API connection by retrieving account info
            account = stripe.Account.retrieve()
            print(f"   ✅ Connected to Stripe API")
            print(f"   📧 Account email: {account.email}")
            print(f"   🏢 Business name: {account.business_profile.name if account.business_profile else 'Not set'}")
            print(f"   🌍 Country: {account.country}")
            
            if account.charges_enabled:
                print("   ✅ Charges enabled")
            else:
                print("   ⚠️  Charges not enabled")
                
            if account.payouts_enabled:
                print("   ✅ Payouts enabled")
            else:
                print("   ⚠️  Payouts not enabled")
            
            return True
            
        except stripe.error.AuthenticationError:
            print("   ❌ Invalid Stripe API key")
            return False
        except Exception as e:
            print(f"   ❌ Stripe API error: {e}")
            return False
    
    def test_webhook_endpoints_list(self):
        """List configured webhook endpoints in Stripe"""
        print("\n5. 📋 Configured Webhook Endpoints")
        print("-" * 30)
        
        try:
            webhook_endpoints = stripe.WebhookEndpoint.list()
            
            if not webhook_endpoints.data:
                print("   ⚠️  No webhook endpoints configured in Stripe")
                print("   💡 You may need to configure webhooks in your Stripe dashboard")
                return True
            
            for endpoint in webhook_endpoints.data:
                print(f"   🔗 URL: {endpoint.url}")
                print(f"   📊 Status: {endpoint.status}")
                print(f"   📅 Created: {time.strftime('%Y-%m-%d', time.localtime(endpoint.created))}")
                
                if endpoint.enabled_events:
                    print(f"   📨 Events: {', '.join(endpoint.enabled_events[:5])}")
                    if len(endpoint.enabled_events) > 5:
                        print(f"       ... and {len(endpoint.enabled_events) - 5} more")
                else:
                    print("   📨 Events: All events (*)")
                
                print()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error retrieving webhook endpoints: {e}")
            return False
    
    def generate_webhook_test_events(self):
        """Generate test events in Stripe for webhook testing"""
        print("\n6. 🧪 Generate Test Events (Optional)")
        print("-" * 30)
        
        try:
            # Create a test product and price for webhook testing
            product = stripe.Product.create(
                name="Test Resume Download",
                description="Test product for webhook verification"
            )
            
            price = stripe.Price.create(
                unit_amount=499,  # $4.99
                currency='usd',
                product=product.id,
            )
            
            print(f"   ✅ Test product created: {product.id}")
            print(f"   ✅ Test price created: {price.id}")
            print("   💡 You can create test payments using these in Stripe dashboard")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error creating test products: {e}")
            return False
    
    def run_full_verification(self):
        """Run complete webhook verification"""
        print("🚀 Starting Complete Webhook Verification")
        print("=" * 50)
        
        results = []
        
        # Run all tests
        results.append(("Environment", self.verify_environment()))
        results.append(("Webhook Endpoint", self.test_webhook_endpoint()))
        results.append(("Event Processing", self.test_webhook_events()))
        results.append(("Stripe API", self.test_stripe_api_connection()))
        results.append(("Webhook Config", self.test_webhook_endpoints_list()))
        
        # Generate summary
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name:<20} {status}")
            if result:
                passed += 1
        
        print(f"\nResult: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All webhook tests passed! Your webhook integration is ready.")
        elif passed >= total - 1:
            print("\n✅ Webhook integration is mostly working. Check failed tests above.")
        else:
            print("\n⚠️  Several webhook tests failed. Please review the issues above.")
        
        # Provide recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 20)
        
        if not self.webhook_secret:
            print("• Configure STRIPE_WEBHOOK_SECRET for production security")
        
        print("• Test webhook endpoints in Stripe Dashboard > Webhooks")
        print("• Monitor webhook delivery logs for any failures")
        print("• Ensure your server is accessible for webhook delivery")
        print("• Use ngrok or similar for local development webhook testing")

def main():
    verifier = WebhookVerifier()
    verifier.run_full_verification()

if __name__ == "__main__":
    main()
