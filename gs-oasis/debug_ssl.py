#!/usr/bin/env python3
"""
Test script to diagnose and fix SSL errors with OpenAI API
"""

import requests
import json
import os
import ssl
import openai
import certifi

def test_api_connection():
    """Test OpenAI API connection with different configurations"""
    print("Testing OpenAI API connection...")
    
    # Get the API key directly from query_gpt.py
    try:
        # Import and set the API key directly
        api_key = "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"
        openai.api_key = api_key
        print(f"API key found: {api_key[:8]}...{api_key[-4:]}")
    except Exception as e:
        print(f"Error getting API key: {str(e)}")
        return False
    
    # Print SSL and certificate information
    print(f"\nOpenSSL version: {ssl.OPENSSL_VERSION}")
    print(f"Default certificate path: {certifi.where()}")
    
    # Test 1: Try a simple HTTPS request to OpenAI's website
    print("\nTest 1: Basic HTTPS connection to OpenAI...")
    try:
        response = requests.get("https://openai.com", timeout=10)
        print(f"✅ Successfully connected to OpenAI website. Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to OpenAI website: {str(e)}")
    
    # Test 2: Try the API connection with requests directly
    print("\nTest 2: Direct API connection using requests...")
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ API request successful. Response: {response.json()['choices'][0]['message']['content']}")
        else:
            print(f"❌ API request failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error with direct API request: {str(e)}")
    
    # Test 3: Try with openai library but custom configurations
    print("\nTest 3: Using openai library with custom SSL context...")
    try:
        # Create a custom SSL context that's more permissive
        custom_context = ssl.create_default_context(cafile=certifi.where())
        custom_context.check_hostname = False
        custom_context.verify_mode = ssl.CERT_NONE
        
        # Monkey patch the openai library's session to use our context
        import urllib3
        openai.requestssession = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1,
            pool_maxsize=1,
            max_retries=0,
            pool_block=False
        )
        openai.requestssession.mount('https://', adapter)
        
        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Simple test for SSL connection"}],
            max_tokens=10
        )
        print(f"✅ openai library test successful. Response: {response.choices[0].message['content']}")
    except Exception as e:
        print(f"❌ Error with openai library test: {str(e)}")
    
    print("\nTesting complete. Check the results to determine the SSL issue.")

if __name__ == "__main__":
    test_api_connection()
