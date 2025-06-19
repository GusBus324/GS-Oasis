#!/usr/bin/env python3
# Test if the OpenAI API is working correctly

from query_gpt import get_open_ai_repsonse

def test_api():
    print("Testing OpenAI API connection...")
    try:
        response = get_open_ai_repsonse("Is this a test message?")
        if response:
            print("Success! API is working. Response received:")
            print("---")
            print(response[:300] + "..." if len(response) > 300 else response)
            print("---")
            return True
        else:
            print("API call succeeded but returned empty response.")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api()
