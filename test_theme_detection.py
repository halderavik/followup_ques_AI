#!/usr/bin/env python3
"""
Test script for theme detection functionality.
"""

import json
import urllib.request
import urllib.parse
import urllib.error

def test_theme_detection():
    """Test theme detection with a response that contains a theme."""
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
        
        print(f"Testing Theme Detection")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            print(f"Status Code: {response.getcode()}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check if theme was detected
            if result.get("detected_theme") == "communication":
                print("✅ SUCCESS: Communication theme detected correctly!")
            else:
                print(f"❌ FAILED: Expected 'communication' theme, got '{result.get('detected_theme')}'")
            
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

def test_no_theme_found():
    """Test when no theme is found in the response."""
    url = "http://localhost:5000/generate-theme-enhanced"
    
    # Test data with no matching themes
    data = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with time management and organization.",
        "type": "reason",
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
        
        print(f"\nTesting No Theme Found")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            print(f"Status Code: {response.getcode()}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check if highest importance theme is returned
            if result.get("highest_importance_theme") == "leadership":
                print("✅ SUCCESS: Highest importance theme (leadership) returned correctly!")
            else:
                print(f"❌ FAILED: Expected 'leadership' theme, got '{result.get('highest_importance_theme')}'")
            
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
    print("🧪 Theme Detection Test")
    print("=" * 40)
    
    success1 = test_theme_detection()
    success2 = test_no_theme_found()
    
    print(f"\n{'='*40}")
    print(f"Test 1 (Theme Detection): {'PASS' if success1 else 'FAIL'}")
    print(f"Test 2 (No Theme): {'PASS' if success2 else 'FAIL'}")
    print(f"{'='*40}") 