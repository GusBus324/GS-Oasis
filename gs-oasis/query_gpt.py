import openai
import json
import html
import re

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

def get_open_ai_repsonse(user_question):
    openai.api_key = "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"

    user_prompt = "Take a look at the following message. Decide whether it is a possible scam threatening the user. Explain why it is if you believe it is."

    modifier = "Provide the response in a JSON format with the following keys: \"finalDecision\", \"rationale\", \"educationalContent\", and \"redFlags\". The finalDecision should be a clear 'Yes' or 'No' whether this is a phishing scam. The rationale should explain your reasoning. The educationalContent should be a short paragraph explaining how to identify phishing scams. The redFlags should be a list of common signs of phishing scams. IMPORTANT: Ensure your response is valid JSON that can be parsed."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": user_prompt + user_question + modifier},
        ]
    )
    
    # Get the raw content from OpenAI
    raw_content = response.choices[0].message['content']
    
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

def format_response_as_html(data):
    """Format the parsed JSON response as professional HTML."""
    
    # Determine the status class based on whether it's a phishing scam
    is_phishing = "Yes" in str(data.get("finalDecision", ""))
    status_class = "alert-danger" if is_phishing else "alert-success"
    status_icon = "⚠️" if is_phishing else "✅"
    status_text = "PHISHING DETECTED" if is_phishing else "NO PHISHING DETECTED"
    
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
        <div class="response-header {status_class}">
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
    


