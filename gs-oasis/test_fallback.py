#!/usr/bin/env python3
"""
Test script to verify that the fallback mechanism works when OpenAI API fails
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fallback_test.log"),
        logging.StreamHandler()
    ]
)

def test_fallback():
    """Test the fallback mechanism by directly activating it"""
    logging.info("Testing rule-based fallback mechanism...")
    
    try:
        # Import the function with the new testing parameter
        from query_gpt import get_open_ai_repsonse
        
        test_message = "URGENT: Your account has been locked! Click here immediately to verify your account: www.bank-secure-verify.com"
        
        # Call the function with test_force_fallback=True to bypass all API calls
        response = get_open_ai_repsonse(test_message, test_force_fallback=True)
        
        # Check if we got a valid fallback response
        if response and len(response) > 100:
            print(f"\nResponse fragment: {response[:200]}...\n")
            
            # Check for indicators that it's the rule-based fallback
            if "Fallback Analysis" in response and "SCAM DETECTED" in response:
                logging.info("✅ SUCCESS: Rule-based fallback mechanism worked correctly")
                print("\nRule-based fallback response received successfully!")
                print(f"Response length: {len(response)} characters")
                
                # Save the response to a file for inspection
                with open("fallback_response.html", "w") as f:
                    f.write(response)
                print("\nResponse saved to fallback_response.html for inspection")
                
                return True
            else:
                logging.warning("⚠️ Response received but not the expected rule-based fallback")
                return False
        else:
            logging.error("❌ No valid response received")
            return False
    
    except Exception as e:
        logging.error(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    print("TESTING FALLBACK MECHANISM")
    print("==========================")
    
    success = test_fallback()
    
    if success:
        print("\n✅ SUCCESS: Fallback mechanism is working correctly!")
    else:
        print("\n❌ FAILURE: Fallback mechanism is not working correctly!")
