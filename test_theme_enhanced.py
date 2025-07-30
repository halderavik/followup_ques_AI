#!/usr/bin/env python3
"""
Comprehensive test script for the theme-enhanced API endpoint.
Tests various scenarios including theme detection, missing themes, and standard workflow.
"""

import json
import urllib.request
import urllib.parse
import urllib.error

def test_api_endpoint(url, data):
    """Test the API endpoint and return the response."""
    try:
        # Convert data to JSON
        json_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data), response.getcode()
            
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        return json.loads(error_data), e.code
    except Exception as e:
        return {"error": str(e)}, 500

def print_test_result(test_name, data, response, status_code):
    """Print formatted test result."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Request Data:")
    print(json.dumps(data, indent=2))
    print(f"\nStatus Code: {status_code}")
    print(f"Response:")
    print(json.dumps(response, indent=2))
    print(f"{'='*60}")

def main():
    """Run comprehensive tests for the theme-enhanced API."""
    base_url = "http://localhost:5000"
    
    print("🧪 THEME-ENHANCED API COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    # Test 1: Theme = "No" (Standard workflow)
    print("\n1️⃣ Testing Theme = 'No' (Standard workflow)")
    test_data_1 = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with time management and communication.",
        "type": "reason",
        "language": "English",
        "theme": "No"
    }
    
    response_1, status_1 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_1)
    print_test_result("Theme = 'No' (Standard)", test_data_1, response_1, status_1)
    
    # Test 2: Theme = "Yes", Theme Found (Communication)
    print("\n2️⃣ Testing Theme = 'Yes', Theme Found")
    test_data_2 = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with time management and communication issues.",
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
    
    response_2, status_2 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_2)
    print_test_result("Theme = 'Yes', Theme Found", test_data_2, response_2, status_2)
    
    # Test 3: Theme = "Yes", No Theme Found
    print("\n3️⃣ Testing Theme = 'Yes', No Theme Found")
    test_data_3 = {
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
    
    response_3, status_3 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_3)
    print_test_result("Theme = 'Yes', No Theme Found", test_data_3, response_3, status_3)
    
    # Test 4: Non-informative response
    print("\n4️⃣ Testing Non-informative Response")
    test_data_4 = {
        "question": "What challenges do you face at work?",
        "response": "I don't know",
        "type": "reason",
        "language": "English",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "leadership", "importance": 80},
                {"name": "communication", "importance": 60}
            ]
        }
    }
    
    response_4, status_4 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_4)
    print_test_result("Non-informative Response", test_data_4, response_4, status_4)
    
    # Test 5: Multiple themes found (should pick highest importance)
    print("\n5️⃣ Testing Multiple Themes Found")
    test_data_5 = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with leadership responsibilities and communication issues.",
        "type": "elaboration",
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
    
    response_5, status_5 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_5)
    print_test_result("Multiple Themes Found", test_data_5, response_5, status_5)
    
    # Test 6: Chinese language test
    print("\n6️⃣ Testing Chinese Language")
    test_data_6 = {
        "question": "你在工作中面临什么挑战？",
        "response": "我在沟通方面有困难。",
        "type": "reason",
        "language": "Chinese",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "leadership", "importance": 80},
                {"name": "communication", "importance": 60}
            ]
        }
    }
    
    response_6, status_6 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_6)
    print_test_result("Chinese Language", test_data_6, response_6, status_6)
    
    # Test 7: Invalid request (missing theme_parameters when theme="Yes")
    print("\n7️⃣ Testing Invalid Request")
    test_data_7 = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with time management.",
        "type": "reason",
        "language": "English",
        "theme": "Yes"
        # Missing theme_parameters
    }
    
    response_7, status_7 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_7)
    print_test_result("Invalid Request", test_data_7, response_7, status_7)
    
    print(f"\n{'='*60}")
    print("🎯 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Test 1 (Theme=No): {'PASS' if status_1 == 200 else 'FAIL'}")
    print(f"✅ Test 2 (Theme Found): {'PASS' if status_2 == 200 else 'FAIL'}")
    print(f"✅ Test 3 (No Theme): {'PASS' if status_3 == 200 else 'FAIL'}")
    print(f"✅ Test 4 (Non-informative): {'PASS' if status_4 == 200 else 'FAIL'}")
    print(f"✅ Test 5 (Multiple Themes): {'PASS' if status_5 == 200 else 'FAIL'}")
    print(f"✅ Test 6 (Chinese): {'PASS' if status_6 == 200 else 'FAIL'}")
    print(f"✅ Test 7 (Invalid): {'PASS' if status_7 == 422 else 'FAIL'}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 