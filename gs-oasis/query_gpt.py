import openai
import json
import html
import re
import requests
import logging
import ssl
import os
import certifi
import urllib3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("openai_api.log"),
        logging.StreamHandler()
    ]
)

def configure_ssl():
    """Configure SSL for OpenAI API requests to fix SSL issues"""
    logging.info("Configuring SSL for OpenAI API")
    
    # Set certifi's CA bundle as the default for OpenAI
    os.environ['OPENAI_CA_BUNDLE'] = certifi.where()
    
    # Create a custom SSL context
    custom_context = ssl.create_default_context(cafile=certifi.where())
    
    # Configure OpenAI library session
    openai.requestssession = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1)
    openai.requestssession.mount('https://', adapter)
    
    # Set a longer timeout for API calls
    openai.api_requestor.TIMEOUT_SECS = 30
    
    return custom_context

# Call the configure_ssl function immediately to set up SSL configuration
ssl_context = configure_ssl()

def extract_json_from_text(text):
    """
    Try to extract JSON from text that might contain additional content before or after the JSON.
    Returns the parsed JSON if successful, or None if no valid JSON was found.
    """
    # Try to find JSON between backticks or triple backticks, common in AI responses
    json_pattern = r'```(?:json)?\s*([\s\S]*?)```|`([\s\S]*?)`'
    json_matches = re.findall(json_pattern, text)
    
    # Check each potential JSON match
    for match in json_matches:
        for json_str in match:
            if json_str.strip():
                try:
                    return json.loads(json_str.strip())
                except json.JSONDecodeError:
                    continue
    
    # If no JSON found in code blocks, try to find JSON-like structure in the entire text
    try:
        # Find the first { and the last }
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            json_str = text[start_idx:end_idx+1]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    return None

def get_open_ai_repsonse(user_question, test_force_fallback=False):
    """
    Get analysis of potential scam from OpenAI with robust fallbacks
    
    Args:
        user_question: The text to analyze for scams
        test_force_fallback: If True, bypass all API calls and use the rule-based fallback (for testing)
    
    Returns:
        HTML formatted response
    """
    openai.api_key = "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"

    user_prompt = "Take a look at the following message. Decide whether it is a possible scam threatening the user. Explain why it is if you believe it is."

    modifier = "Provide the response in a JSON format with the following keys: \"finalDecision\", \"rationale\", \"educationalContent\", and \"redFlags\". The finalDecision should be one of 'Yes' (definitely a scam), 'Maybe' (suspicious content), or 'No' (not a scam). The rationale should explain your reasoning. The educationalContent should be a short paragraph explaining how to identify scams. The redFlags should be a list of common signs of scams. IMPORTANT: Ensure your response is valid JSON that can be parsed."

    # If testing mode is enabled, use the rule-based fallback directly
    if test_force_fallback:
        logging.info("Force fallback mode enabled for testing")
        return generate_fallback_response(user_question)

    # Try primary approach using OpenAI library with SSL configuration
    try:
        logging.info("Attempting OpenAI API call with custom SSL context...")
        
        # SSL configuration is already done by the configure_ssl function called at module level
        
        # Direct API call with proper error handling
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_prompt + user_question + modifier},
            ],
            timeout=30
        )
        
        # Get the raw content from OpenAI
        raw_content = response.choices[0].message['content']
        logging.info("Successfully received OpenAI API response")
        
        try:
            # First try direct JSON parsing
            parsed_response = json.loads(raw_content)
            formatted_html = format_response_as_html(parsed_response)
            return formatted_html
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from text
            parsed_response = extract_json_from_text(raw_content)
            if parsed_response:
                formatted_html = format_response_as_html(parsed_response)
                return formatted_html
            else:
                # Fallback if no JSON can be extracted
                return f"""
                <div class="professional-response">
                    <div class="response-header alert-warning">
                        <h2>⚠️ Analysis Results</h2>
                    </div>
                    <div class="response-section">
                        <h3>Analysis</h3>
                        <p>{html.escape(raw_content)}</p>
                    </div>
                </div>
                """
    except Exception as e:
        # Log the error
        logging.error(f"OpenAI API Error (primary method): {str(e)}")
        
        # Try with direct HTTPS request as backup approach
        try:
            logging.info("Attempting direct API request as fallback...")
            
            # Create a custom session with a custom SSL context
            session = requests.Session()
            custom_context = ssl.create_default_context(cafile=certifi.where())
            custom_context.check_hostname = True
            custom_context.verify_mode = ssl.CERT_REQUIRED
            
            # Create an adapter with the custom context
            adapter = requests.adapters.HTTPAdapter()
            session.mount('https://', adapter)
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai.api_key}"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": user_prompt + user_question + modifier}],
                "max_tokens": 1000
            }
            
            # Make the API call with the custom session
            response = session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30,
                verify=certifi.where()  # Explicitly use certifi's CA bundle
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_content = result['choices'][0]['message']['content']
                logging.info("Successfully received OpenAI API response via fallback method")
                
                # Process the response as before
                try:
                    parsed_response = json.loads(raw_content)
                    formatted_html = format_response_as_html(parsed_response)
                    return formatted_html
                except json.JSONDecodeError:
                    parsed_response = extract_json_from_text(raw_content)
                    if parsed_response:
                        formatted_html = format_response_as_html(parsed_response)
                        return formatted_html
                    else:
                        return f"""
                        <div class="professional-response">
                            <div class="response-header alert-warning">
                                <h2>⚠️ Analysis Results</h2>
                            </div>
                            <div class="response-section">
                                <h3>Analysis</h3>
                                <p>{html.escape(raw_content)}</p>
                            </div>
                        </div>
                        """
            else:
                # API returned an error
                error_message = f"API Error: {response.status_code} - {response.text}"
                logging.error(error_message)
                raise Exception(error_message)
                
        except Exception as fallback_error:
            logging.error(f"Fallback approach also failed: {str(fallback_error)}")
            
            # Try one more approach with a very permissive SSL context
            try:
                logging.info("Attempting final fallback with permissive SSL context...")
                
                # Create a very permissive context as last resort
                permissive_context = ssl.create_default_context()
                permissive_context.check_hostname = False
                permissive_context.verify_mode = ssl.CERT_NONE
                
                # Create an HTTPS adapter with the permissive context
                https = urllib3.PoolManager(
                    cert_reqs='CERT_NONE',
                    ca_certs=None,
                    ssl_context=permissive_context
                )
                
                encoded_data = json.dumps(data).encode('utf-8')
                
                # Make the request with the permissive context
                response = https.request(
                    'POST',
                    'https://api.openai.com/v1/chat/completions',
                    body=encoded_data,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status == 200:
                    result = json.loads(response.data.decode('utf-8'))
                    raw_content = result['choices'][0]['message']['content']
                    logging.info("Successfully received OpenAI API response via permissive fallback")
                    
                    # Process the response as before
                    try:
                        parsed_response = json.loads(raw_content)
                        formatted_html = format_response_as_html(parsed_response)
                        return formatted_html
                    except json.JSONDecodeError:
                        parsed_response = extract_json_from_text(raw_content)
                        if parsed_response:
                            formatted_html = format_response_as_html(parsed_response)
                            return formatted_html
                        else:
                            return generate_fallback_response(user_question)
                else:
                    # API returned an error even with permissive SSL
                    logging.error(f"Final fallback failed with status: {response.status}")
                    return generate_fallback_response(user_question)
                    
            except Exception as final_error:
                logging.error(f"All API approaches failed: {str(final_error)}")
                return generate_fallback_response(user_question)

def generate_fallback_response(user_text):
    """Generate a fallback response when OpenAI API is unavailable"""
    logging.info("Generating fallback response")
    
    # Check for common scam indicators
    scam_indicators = [
        "urgent", "urgently", "immediately", "account locked", "verify account", 
        "verify your account", "banking details", "click here", "login details", 
        "unusual activity", "suspicious activity", "tax refund", "prize", "winner",
        "lottery", "inheritance", "millions", "prince", "nigeria", "confidential",
        "investment opportunity", "bitcoin", "cryptocurrency", "wallet", "deposit",
        "password", "security", "update your information", "gift card", "iTunes",
        "steam", "government", "irs", "hmrc", "tax", "arrested", "lawsuit", "legal",
        "court", "police", "fbi", "claim your", "social security", "social security number",
        "SSN", "login", "log in", "sign in", "signin", "bank", "PayPal", "Apple",
        "Microsoft", "Amazon", "support", "helpdesk", "reset", "recover", "free money"
    ]
    
    # Count how many indicators are present
    indicator_count = sum(1 for indicator in scam_indicators if indicator.lower() in user_text.lower())
    
    # Determine if this is likely a scam based on indicator count
    is_scam = indicator_count >= 3
    is_suspicious = indicator_count >= 1
    
    if is_scam:
        status_class = "alert-danger"
        status_icon = "⚠️"
        status_text = "SCAM DETECTED"
        header_style = "background: #d9534f;"  # Red background
    elif is_suspicious:
        status_class = "alert-warning"
        status_icon = "⚠️"
        status_text = "SUSPICIOUS CONTENT"
        header_style = "background: #f0ad4e;"  # Yellow/amber background
    else:
        status_class = "alert-success"
        status_icon = "✅"
        status_text = "NO SCAM DETECTED"
        header_style = "background: #5cb85c;"  # Green background
    
    # Generate appropriate response based on detection
    if is_scam or is_suspicious:
        rationale = """This message contains several warning signs commonly associated with scams or phishing attempts. 
        These include urgent language, requests for personal information, suspicious links, or financial requests."""
        
        educational_content = """Protect yourself from scams by being cautious of unexpected messages, especially those creating 
        a sense of urgency. Never click on suspicious links or provide personal information unless you're certain of the 
        sender's identity. When in doubt, contact organizations directly through their official channels, not using contact 
        information provided in the suspicious message."""
        
        red_flags_html = """<ul>
            <li>Urgency or pressure tactics</li>
            <li>Poor grammar or spelling errors</li>
            <li>Requests for personal information</li>
            <li>Suspicious links or attachments</li>
            <li>Offers that seem to be too good to be true</li>
            <li>Impersonal greetings or unusual sender addresses</li>
            <li>Threats or intimidation</li>
            <li>Requests for unusual payment methods</li>
        </ul>"""
    else:
        rationale = """This message doesn't contain obvious indicators of scam or phishing attempts. 
        However, always remain vigilant with unexpected communications."""
        
        educational_content = """Even when messages appear legitimate, it's good practice to verify unexpected communications.
        Legitimate organizations won't pressure you for immediate action or personal information via unexpected messages."""
        
        red_flags_html = """<ul>
            <li>Unexpected requests for personal information</li>
            <li>Messages creating a false sense of urgency</li>
            <li>Suspicious links or attachments</li>
            <li>Offers that seem to be too good to be true</li>
            <li>Impersonal greetings or unusual sender addresses</li>
        </ul>"""
    
    # Build the complete HTML response
    html_response = f"""
    <div class="professional-response">
        <div class="response-header" style="{header_style}">
            <h2>{status_icon} {status_text}</h2>
        </div>
        
        <div class="response-section">
            <h3>Fallback Analysis</h3>
            <p>{rationale}</p>
            <p><em>Note: This is a rule-based analysis as our AI service is temporarily unavailable.</em></p>
        </div>
        
        <div class="response-section">
            <h3>Educational Information</h3>
            <p>{educational_content}</p>
        </div>
        
        <div class="response-section">
            <h3>Red Flags to Watch For</h3>
            {red_flags_html}
        </div>
    </div>
    """
    
    return html_response

def format_response_as_html(data):
    """Format the parsed JSON response as professional HTML."""
    
    # Determine the status class based on the detection result
    decision = str(data.get("finalDecision", "")).lower()
    
    if "yes" in decision:
        # Definite scam
        status_class = "alert-danger"
        status_icon = "⚠️"
        status_text = "SCAM DETECTED"
        header_style = "background: #d9534f;"  # Red background
    elif "maybe" in decision or "suspicious" in decision or "possibly" in decision:
        # Suspicious content
        status_class = "alert-warning"
        status_icon = "⚠️"
        status_text = "SUSPICIOUS CONTENT"
        header_style = "background: #f0ad4e;"  # Yellow/amber background
    else:
        # No scam detected
        status_class = "alert-success"
        status_icon = "✅"
        status_text = "NO SCAM DETECTED"
        header_style = "background: #5cb85c;"  # Green background
    
    # Format the red flags as a list
    red_flags_html = ""
    if "redFlags" in data and isinstance(data["redFlags"], list):
        red_flags_html = "<ul>"
        for flag in data["redFlags"]:
            red_flags_html += f"<li>{html.escape(str(flag))}</li>"
        red_flags_html += "</ul>"
    else:
        # Handle case where redFlags is a string or not in expected format
        red_flags = data.get("redFlags", "No specific red flags identified.")
        if isinstance(red_flags, str):
            red_flags_html = f"<p>{html.escape(red_flags)}</p>"
    
    # Build the complete HTML response
    html_response = f"""
    <div class="professional-response">
        <div class="response-header" style="{header_style}">
            <h2>{status_icon} {status_text}</h2>
        </div>
        
        <div class="response-section">
            <h3>Analysis</h3>
            <p>{html.escape(str(data.get("rationale", "No rationale provided.")))}</p>
        </div>
        
        <div class="response-section">
            <h3>Educational Information</h3>
            <p>{html.escape(str(data.get("educationalContent", "No educational content provided.")))}</p>
        </div>
        
        <div class="response-section">
            <h3>Red Flags to Watch For</h3>
            {red_flags_html}
        </div>
    </div>
    """
    
    return html_response



