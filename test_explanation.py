#!/usr/bin/env python3
"""
Test script to verify the new explanation feature.
"""

import json
import urllib.request
import urllib.parse
import urllib.error

def test_explanation_feature():
    """Test the new explanation feature."""
    url = "http://localhost:5000/generate-theme-enhanced"
    
    # Test data with communication theme
    data = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with communication issues and team collaboration.",
        "type": "impact",
        "language": "English",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "leadership", "importance": 80},
                {"name": "communication", "importance": 60},
                {"name": "technology", "importance": 40}
            ]
        }
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
        
        print("🧪 Testing Explanation Feature")
        print("=" * 40)
        print(f"Request: {json.dumps(data, indent=2)}")
        
        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            print(f"Status Code: {response.getcode()}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check results
            question = result.get("question")
            explanation = result.get("explanation")
            detected_theme = result.get("detected_theme")
            
            print(f"\n📋 ANALYSIS:")
            print(f"Question: {question}")
            print(f"Explanation: {explanation}")
            print(f"Detected Theme: {detected_theme}")
            
            if question and explanation and detected_theme == "communication":
                print("✅ SUCCESS: Explanation feature working correctly!")
                return True
            else:
                print("❌ FAILED: Explanation feature not working as expected")
                return False
            
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
    success = test_explanation_feature()
    print(f"\nTest {'PASSED' if success else 'FAILED'}") 