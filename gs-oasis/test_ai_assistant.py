#!/usr/bin/env python3
"""
Test script to verify the AI module functionality in GS-Oasis
"""

import requests
import json
import time
import sys

def test_ai_assistant():
    """Test the AI assistant functionality"""
    # Wait for the server to fully start
    print("Waiting for the server to start...")
    time.sleep(3)
    
    try:
        # First, we need to log in
        session = requests.Session()
        
        # Try to access the login page to get any CSRF token
        login_url = "http://localhost:5003/login"
        login_page = session.get(login_url)
        
        if login_page.status_code != 200:
            print(f"ERROR: Could not access login page. Status code: {login_page.status_code}")
            return False
        
        # For this test, we need to register a test user if it doesn't exist
        username = "ai_test_user"
        password = "Test12345!"
        email = "ai_test@example.com"
        
        # Try to register the user
        register_data = {
            "username": username,
            "password": password,
            "email": email
        }
        register_response = session.post("http://localhost:5003/register", data=register_data)
        
        # Log in with the user
        login_data = {
            "username": username,
            "password": password
        }
        login_response = session.post(login_url, data=login_data)
        
        if login_response.status_code != 200 and "dashboard" not in login_response.url:
            print(f"ERROR: Failed to log in. Status code: {login_response.status_code}")
            return False
        
        print("Successfully logged in.")
        
        # Now test the AI assistant
        ai_query = "Is this email a scam: 'Dear customer, your account has been locked. Click here to verify your identity.'"
        ai_data = {
            "question": ai_query
        }
        
        ai_response = session.post("http://localhost:5003/ai_assistant", data=ai_data)
        
        if ai_response.status_code != 200:
            print(f"ERROR: AI assistant request failed. Status code: {ai_response.status_code}")
            return False
        
        print("AI assistant response received successfully.")
        
        # Check if the response contains the user's question
        if ai_query in ai_response.text:
            print("SUCCESS: User question is displayed in the response.")
        else:
            print("WARNING: User question is not displayed in the response.")
        
        # Check for expected response elements
        response_indicators = [
            "SCAM DETECTED", 
            "SUSPICIOUS CONTENT",
            "NO SCAM DETECTED",
            "Analysis",
            "Red Flags"
        ]
        
        found_indicators = []
        for indicator in response_indicators:
            if indicator in ai_response.text:
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"SUCCESS: Found response indicators: {', '.join(found_indicators)}")
        else:
            print("WARNING: No expected response indicators found. AI may not be working properly.")
        
        # Save the response for inspection
        with open("ai_response_test.html", "w") as f:
            f.write(ai_response.text)
            print("Response saved to ai_response_test.html for inspection.")
        
        return True
    
    except Exception as e:
        print(f"ERROR: Exception occurred during test: {e}")
        return False

if __name__ == "__main__":
    print("Testing GS Oasis AI Assistant functionality...")
    success = test_ai_assistant()
    
    if success:
        print("AI Assistant test completed.")
        sys.exit(0)
    else:
        print("AI Assistant test failed.")
        sys.exit(1)
