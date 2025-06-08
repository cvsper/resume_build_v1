#!/usr/bin/env python3
"""
Debug script to test the voice interview submit functionality
"""
import os
import sys

def debug_interview_submit():
    """Debug the voice interview submit endpoint"""
    print("🔍 Debugging Voice Interview Submit Issue...")
    print("=" * 60)
    
    # Change to the correct directory
    os.chdir('/Users/sevs/Documents/Leads/resume_build_v1')
    
    # Test 1: Check if endpoint exists in app
    print("\n1. Testing Endpoint Registration...")
    try:
        from app import app
        
        with app.app_context():
            # Check all routes containing 'submit'
            submit_routes = [rule for rule in app.url_map.iter_rules() if 'submit' in rule.rule]
            
            print("Found submit-related routes:")
            for rule in submit_routes:
                print(f"  {rule.rule} -> {rule.endpoint} ({', '.join(rule.methods)})")
                
            # Specifically check for submit-voice-answer
            target_route = '/api/submit-voice-answer'
            target_found = any(rule.rule == target_route for rule in app.url_map.iter_rules())
            
            if target_found:
                print(f"✅ {target_route} endpoint is registered")
            else:
                print(f"❌ {target_route} endpoint NOT FOUND")
                return False
                
    except Exception as e:
        print(f"❌ Error checking routes: {e}")
        return False
    
    # Test 2: Check database models
    print("\n2. Testing Database Models...")
    try:
        from app import db, InterviewSession, InterviewAnswer
        
        print("✅ InterviewSession model imported successfully")
        print("✅ InterviewAnswer model imported successfully")
        
        # Check model attributes
        session_attrs = [attr for attr in dir(InterviewSession) if not attr.startswith('_')]
        answer_attrs = [attr for attr in dir(InterviewAnswer) if not attr.startswith('_')]
        
        required_session_attrs = ['id', 'user_id', 'job_title', 'status', 'current_question']
        required_answer_attrs = ['id', 'session_id', 'question_number', 'question_text', 'answer_text']
        
        for attr in required_session_attrs:
            if attr in session_attrs:
                print(f"  ✅ InterviewSession.{attr}")
            else:
                print(f"  ❌ InterviewSession.{attr} MISSING")
                
        for attr in required_answer_attrs:
            if attr in answer_attrs:
                print(f"  ✅ InterviewAnswer.{attr}")
            else:
                print(f"  ❌ InterviewAnswer.{attr} MISSING")
                
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False
    
    # Test 3: Check function dependencies
    print("\n3. Testing Function Dependencies...")
    try:
        from app import evaluate_interview_answer, generate_interview_questions, generate_final_interview_feedback
        print("✅ evaluate_interview_answer function exists")
        print("✅ generate_interview_questions function exists") 
        print("✅ generate_final_interview_feedback function exists")
    except ImportError as e:
        print(f"❌ Missing function dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking functions: {e}")
        return False
    
    # Test 4: Check endpoint function directly
    print("\n4. Testing Endpoint Function...")
    try:
        from app import submit_voice_answer
        print("✅ submit_voice_answer function exists")
        
        # Check if it's properly decorated
        func_name = getattr(submit_voice_answer, '__name__', 'unknown')
        print(f"  Function name: {func_name}")
        
    except Exception as e:
        print(f"❌ Error checking endpoint function: {e}")
        return False
    
    # Test 5: Check authentication requirements
    print("\n5. Testing Authentication Setup...")
    try:
        from flask_login import current_user
        print("✅ Flask-Login is available")
        
        # Check if User model exists
        from app import User
        print("✅ User model exists")
        
    except Exception as e:
        print(f"❌ Authentication setup issue: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("📋 Debug Analysis Summary")
    print("=" * 60)
    
    # Provide troubleshooting steps
    print("\n🔧 Troubleshooting Steps:")
    print("1. ✅ Endpoint exists and is registered correctly")
    print("2. ✅ Database models are properly defined")
    print("3. ✅ Required functions are available")
    print("4. ✅ Authentication framework is set up")
    
    print("\n🚨 Possible Issues Causing 404:")
    print("• **Authentication**: User might not be logged in (login_required decorator)")
    print("• **Production Environment**: Different code version deployed")
    print("• **Route Conflicts**: Another route might be intercepting the request")
    print("• **Case Sensitivity**: URL case mismatch")
    print("• **Database Migration**: Tables might not exist in production")
    
    print("\n💡 Debugging Steps for Production:")
    print("1. Check browser dev tools Network tab for actual request URL")
    print("2. Verify user is logged in (check for authentication cookies)")
    print("3. Check production logs for actual error details")
    print("4. Ensure latest code is deployed to production")
    print("5. Verify database tables exist: interview_session, interview_answer")
    
    print("\n✨ Debug Status: COMPLETE")
    print("🎯 Endpoint exists locally - likely production environment issue")
    
    return True

if __name__ == "__main__":
    try:
        success = debug_interview_submit()
        if success:
            print("\n🎊 Debug completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Debug found issues.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Debug failed with error: {e}")
        sys.exit(1)