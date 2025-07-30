#!/usr/bin/env python3
"""
Simple test script for the theme-enhanced API endpoint.
"""

import json
import urllib.request
import urllib.parse
import urllib.error

def test_simple():
    """Test the theme-enhanced API with a simple request."""
    url = "http://localhost:5000/generate-theme-enhanced"
    
    # Simple test data
    data = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with time management.",
        "type": "reason",
        "language": "English",
        "theme": "No"
    }
    
    try:
        # Convert data to JSON
        json_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Testing URL: {url}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            print(f"Status Code: {response.getcode()}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        try:
            error_data = e.read().decode('utf-8')
            print(f"Error Response: {error_data}")
        except:
            print("Could not read error response")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Theme-Enhanced API Test")
    print("=" * 40)
    success = test_simple()
    print(f"\nTest {'PASSED' if success else 'FAILED'}") 