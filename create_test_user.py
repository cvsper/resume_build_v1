#!/usr/bin/env python3
"""Create test user for authentication testing"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_test_user():
    """Create or verify test user exists"""
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(email='test@example.com').first()
        
        if existing_user:
            print("✅ Test user already exists: test@example.com")
            return True
        
        # Create new test user
        try:
            test_user = User(
                email='test@example.com',
                password=generate_password_hash('password123'),
                name='Test User'
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Test user created successfully: test@example.com / password123")
            return True
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return False

if __name__ == "__main__":
    create_test_user()
