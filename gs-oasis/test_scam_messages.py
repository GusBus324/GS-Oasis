#!/usr/bin/env python3
# Test the updated scam detection messaging

from query_gpt import format_response_as_html

def test_scam_detection_messages():
    print("Testing updated scam detection messages...\n")
    
    # Test case 1: Definite scam
    test_data1 = {
        "finalDecision": "Yes",
        "rationale": "This message contains multiple red flags indicating it's a scam.",
        "educationalContent": "Always be cautious of messages that create a sense of urgency or ask for personal information.",
        "redFlags": ["Urgent action required", "Threats of account suspension", "Grammatical errors"]
    }
    
    # Test case 2: Suspicious content
    test_data2 = {
        "finalDecision": "Maybe",
        "rationale": "This message has some concerning elements but isn't definitively a scam.",
        "educationalContent": "When in doubt, verify the sender through official channels before taking any action.",
        "redFlags": ["Requesting personal information", "Unusual sender address"]
    }
    
    # Test case 3: No scam detected
    test_data3 = {
        "finalDecision": "No",
        "rationale": "This appears to be a legitimate message from a verified source.",
        "educationalContent": "Even legitimate messages should be approached with caution if they ask for sensitive information.",
        "redFlags": ["None detected in this message"]
    }
    
    # Format and check the responses
    print("Test case 1 (Scam):")
    html1 = format_response_as_html(test_data1)
    print("Contains 'SCAM DETECTED':", "SCAM DETECTED" in html1)
    print()
    
    print("Test case 2 (Suspicious):")
    html2 = format_response_as_html(test_data2)
    print("Contains 'SUSPICIOUS CONTENT':", "SUSPICIOUS CONTENT" in html2)
    print()
    
    print("Test case 3 (Safe):")
    html3 = format_response_as_html(test_data3)
    print("Contains 'NO SCAM DETECTED':", "NO SCAM DETECTED" in html3)

if __name__ == "__main__":
    test_scam_detection_messages()
