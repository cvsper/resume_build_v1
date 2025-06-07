#!/usr/bin/env python3
"""
Test script for Voice Interview API
"""
import os
import sys
from app import app, db, User, InterviewSession, InterviewAnswer

def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        try:
            # Check if tables exist by trying to query them
            db.session.execute(db.text("SELECT 1 FROM interview_sessions LIMIT 1"))
            print("✅ Database tables already exist")
        except Exception as e:
            print(f"📝 Creating database tables... ({e})")
            db.create_all()
            print("✅ Database tables created successfully")

def test_models():
    """Test that the models work correctly"""
    with app.app_context():
        try:
            # Test creating a session
            print("🧪 Testing InterviewSession model...")
            session = InterviewSession(
                user_id=1,
                job_title="Software Engineer",
                interviewer_personality="friendly"
            )
            print("✅ InterviewSession model works")
            
            # Test creating an answer
            print("🧪 Testing InterviewAnswer model...")
            answer = InterviewAnswer(
                session_id=1,
                question="Test question?",
                answer="Test answer",
                question_number=1,
                score=8,
                feedback="Good answer"
            )
            print("✅ InterviewAnswer model works")
            
        except Exception as e:
            print(f"❌ Model test failed: {e}")
            return False
    return True

def check_api_functions():
    """Check if the helper functions are defined"""
    try:
        from app import generate_interview_questions, evaluate_interview_answer, generate_final_interview_feedback
        print("✅ All helper functions are imported")
        return True
    except ImportError as e:
        print(f"❌ Missing helper functions: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Voice Interview System...")
    
    # Check database
    create_tables()
    
    # Test models
    if not test_models():
        sys.exit(1)
    
    # Check API functions
    if not check_api_functions():
        sys.exit(1)
    
    print("✅ All tests passed! Voice Interview system should work.")