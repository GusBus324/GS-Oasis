#!/usr/bin/env python3
# Test the full OpenAI integration with updated scam detection terminology

from query_gpt import get_open_ai_repsonse

def test_api_integration():
    print("Testing OpenAI integration with updated scam detection terminology...\n")
    
    # Test with a clearly suspicious message
    test_message = "URGENT: Your account has been suspended! You must verify your account now by clicking this link: bit.ly/verify123 or your account will be permanently deleted!"
    
    try:
        # Make the API call
        print("Making API call with suspicious message...")
        response = get_open_ai_repsonse(test_message)
        
        # Check for the updated terminology
        if "SCAM DETECTED" in response:
            print("✅ Success: Response includes 'SCAM DETECTED'")
        elif "SUSPICIOUS CONTENT" in response:
            print("✅ Success: Response includes 'SUSPICIOUS CONTENT'")
        elif "NO SCAM DETECTED" in response:
            print("❓ Unexpected: Response includes 'NO SCAM DETECTED' for a suspicious message")
        else:
            print("❌ Failed: Response doesn't include any expected status message")
        
        # Print part of the response for manual inspection
        print("\nPartial API response:")
        print(response[:500] + "...\n" if len(response) > 500 else response)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_api_integration()
