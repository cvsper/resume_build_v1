#!/usr/bin/env python3
"""
Simple webhook test to isolate the 500 error
"""

import requests
import json

def test_webhook_simple():
    """Test webhook with minimal payload"""
    url = "http://127.0.0.1:5006/stripe-webhook"
    
    # Test with minimal valid JSON
    test_payloads = [
        {"test": "simple"},
        {"type": "test.event", "data": {"object": {}}},
        {"type": "checkout.session.completed", "data": {"object": {"id": "test", "mode": "payment"}}}
    ]
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\nTest {i}: {payload}")
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_webhook_simple()
