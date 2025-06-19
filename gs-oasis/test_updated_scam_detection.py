#!/usr/bin/env python3
# Test the updated scam detection response formatting

from query_gpt import format_response_as_html, get_open_ai_repsonse
import json

def test_response_formatting():
    print("Testing response formatting with different scenarios...")
    
    # Test case 1: Definite scam
    scam_data = {
        "finalDecision": "Yes",
        "rationale": "This is clearly a scam with 95% confidence because it exhibits multiple red flags: urgency, requests for personal information, bad grammar, and suspicious links.",
        "educationalContent": "Be cautious of messages that create a false sense of urgency and ask for personal information.",
        "redFlags": [
            "Creates false urgency",
            "Requests sensitive information",
            "Contains suspicious links",
            "Has poor grammar and spelling"
        ]
    }
    
    # Test case 2: No scam
    safe_data = {
        "finalDecision": "No",
        "rationale": "This appears to be a legitimate message with 98% confidence as it comes from a verified sender, contains no suspicious requests, and matches the expected format of communications from this organization.",
        "educationalContent": "Legitimate messages typically don't pressure you to act quickly and don't ask for sensitive information.",
        "redFlags": [
            "No red flags detected in this message",
            "However, always verify the sender before taking action"
        ]
    }
    
    # Test case 3: Suspicious content
    suspicious_data = {
        "finalDecision": "Maybe",
        "rationale": "This message contains some suspicious elements with 50% confidence. While it doesn't explicitly ask for personal information, it uses unusual language and contains links that should be verified.",
        "educationalContent": "When in doubt, contact the supposed sender directly using their official contact methods, not those provided in the message.",
        "redFlags": [
            "Unusual language or formatting",
            "Links that need verification",
            "Subtle pressure tactics"
        ]
    }
    
    # Format and print the HTML responses
    print("\n===== SCAM DETECTED FORMATTING =====")
    scam_html = format_response_as_html(scam_data)
    print(scam_html[:500] + "..." if len(scam_html) > 500 else scam_html)
    
    print("\n===== NO SCAM DETECTED FORMATTING =====")
    safe_html = format_response_as_html(safe_data)
    print(safe_html[:500] + "..." if len(safe_html) > 500 else safe_html)
    
    print("\n===== SUSPICIOUS CONTENT FORMATTING =====")
    suspicious_html = format_response_as_html(suspicious_data)
    print(suspicious_html[:500] + "..." if len(suspicious_html) > 500 else suspicious_html)
    
    print("\nDone testing response formatting")

if __name__ == "__main__":
    test_response_formatting()
