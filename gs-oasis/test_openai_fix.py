#!/usr/bin/env python3
"""
Test script for the fixed OpenAI API connection
"""

from query_gpt import get_open_ai_repsonse
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("openai_test.log"),
        logging.StreamHandler()
    ]
)

def test_openai_connection():
    """Test the fixed OpenAI API connection"""
    
    logging.info("Testing OpenAI API connection with SSL fix...")
    
    # Define test cases
    test_cases = [
        {
            "name": "Basic test",
            "text": "Hello, this is a test message."
        },
        {
            "name": "Scam test",
            "text": "URGENT: Your account has been locked! Click here immediately to verify your account: www.bank-secure-verify.com"
        }
    ]
    
    success = 0
    
    for test in test_cases:
        logging.info(f"Testing with: {test['name']}")
        try:
            # Add a delay to avoid rate limiting
            time.sleep(1)
            
            # Call the API
            response = get_open_ai_repsonse(test["text"])
            
            if response and len(response) > 100:  # Basic validation that we got a real response
                logging.info(f"✅ Success! Response length: {len(response)} characters")
                
                # Save the response for inspection
                with open(f"openai_response_{test['name'].replace(' ', '_')}.html", "w") as f:
                    f.write(response)
                    
                success += 1
            else:
                logging.error(f"❌ Failed: Response too short or empty")
        except Exception as e:
            logging.error(f"❌ Error: {str(e)}", exc_info=True)
    
    # Report results
    if success == len(test_cases):
        logging.info(f"✅ All {success}/{len(test_cases)} tests passed!")
        return True
    else:
        logging.warning(f"⚠️ {success}/{len(test_cases)} tests passed")
        return False

if __name__ == "__main__":
    print("TESTING FIXED OPENAI API CONNECTION")
    print("===================================")
    
    success = test_openai_connection()
    
    if success:
        print("\n✅ SUCCESS: OpenAI API connection is working!")
    else:
        print("\n⚠️ WARNING: Some tests failed. Check the logs for details.")
