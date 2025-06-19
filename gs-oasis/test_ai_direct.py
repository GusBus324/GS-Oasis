#!/usr/bin/env python3
"""
Simple test to verify the AI module functionality in GS-Oasis without requiring the web app
"""

from query_gpt import get_open_ai_repsonse

def test_ai_directly():
    """Test the AI module directly without using the web interface"""
    print("Testing OpenAI integration directly...")
    
    test_message = "Is this email a scam: 'Dear customer, your account has been locked. Click here to verify your identity.'"
    
    try:
        response = get_open_ai_repsonse(test_message)
        
        if response:
            print("\nAI response received successfully!")
            print(f"Response length: {len(response)} characters")
            
            # Check for important indicators in the response
            for indicator in ["SCAM DETECTED", "SUSPICIOUS CONTENT", "NO SCAM DETECTED", "Analysis", "Red Flags"]:
                if indicator in response:
                    print(f"- Found indicator: {indicator}")
            
            # Save the response to a file for inspection
            with open("direct_ai_test_response.html", "w") as f:
                f.write(response)
            print("\nResponse saved to direct_ai_test_response.html for inspection")
            
            return True
        else:
            print("ERROR: Received empty response from AI")
            return False
            
    except Exception as e:
        print(f"ERROR: Exception occurred during test: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_directly()
    
    if success:
        print("\nAI is AVAILABLE and functioning properly.")
    else:
        print("\nAI is NOT AVAILABLE or not functioning properly.")
