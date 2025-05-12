import re

def check_url_suspiciousness(url):
    """
    Check if a URL appears suspicious.
    Returns a tuple (is_suspicious, reason)
    """
    try:
        # Basic URL validation
        if not url or not isinstance(url, str):
            return False, ""
        
        # Normalize the URL
        url = url.lower().strip()
        
        # Check for common URL patterns that might indicate phishing or scams
        suspicious_patterns = [
            # IP address URLs
            (r'https?://\d+\.\d+\.\d+\.\d+', "Uses IP address instead of domain name"),
            
            # Excessive subdomains
            (r'https?://([a-z0-9-]+\.){5,}[a-z0-9-]+', "Contains excessive subdomains"),
            
            # Misspelled popular domains
            (r'(google|facebook|apple|amazon|microsoft|paypal|netflix|gmail|yahoo|instagram|twitter|linkedin|spotify|youtube)[^a-z0-9.-]', 
             "Contains misspelled popular brand name"),
            
            # URLs with suspicious TLDs
            (r'\.tk$|\.xyz$|\.top$|\.gq$|\.ml$|\.ga$|\.cf$', "Uses a TLD commonly associated with free domains"),
            
            # URLs with suspicious keywords
            (r'login|verify|secure|account|password|credit|bank|verify|wallet|support', 
             "Contains keywords commonly used in phishing"),
            
            # URLs that mix character sets (punycode attacks)
            (r'xn--', "Uses internationalized domain name encoding, potential homograph attack"),
            
            # Shortened URLs
            (r'bit\.ly|tinyurl|goo\.gl|t\.co|is\.gd|buff\.ly|rebrand\.ly', "Uses URL shortener service"),
            
            # Data URLs (can contain executable code)
            (r'data:', "Uses data URL scheme, may contain embedded code")
        ]
        
        for pattern, reason in suspicious_patterns:
            if re.search(pattern, url):
                return True, reason
        
        # Extract domain from URL
        domain_match = re.search(r'https?://([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)
            
            # Check for numeric domains
            if re.match(r'^\d+\.$', domain):
                return True, "Domain name uses only numbers"
            
            # Check for very long domain names
            if len(domain) > 50:
                return True, "Extremely long domain name"
            
            # Check for random-looking domains (random string of characters)
            if re.match(r'^[a-z0-9]{15,}\.', domain) and not any(word in domain for word in ["google", "microsoft", "amazon", "facebook"]):
                return True, "Domain appears to be a random string"
        
        return False, ""
    except Exception:
        return False, ""
