#!/usr/bin/env python3
"""
Test script to verify theme detection fix.
"""

import json
import urllib.request
import urllib.parse
import urllib.error

def test_theme_detection():
    """Test theme detection with communication theme."""
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
        
        print("🧪 Testing Theme Detection Fix")
        print("=" * 40)
        print(f"Request: {json.dumps(data, indent=2)}")
        
        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            print(f"Status Code: {response.getcode()}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check results
            detected_theme = result.get("detected_theme")
            theme_importance = result.get("theme_importance")
            
            if detected_theme == "communication":
                print("✅ SUCCESS: Communication theme detected correctly!")
                print(f"   Theme: {detected_theme}")
                print(f"   Importance: {theme_importance}")
            else:
                print(f"❌ FAILED: Expected 'communication' theme, got '{detected_theme}'")
            
            return detected_theme == "communication"
            
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
    success = test_theme_detection()
    print(f"\nTest {'PASSED' if success else 'FAILED'}") 