#!/usr/bin/env python3
"""
Comprehensive test script for the generate-theme-enhanced API endpoint.
Tests various scenarios including theme detection, missing themes, and standard workflow.
"""

import requests
import json
import time
from typing import Dict, Any, Tuple

def test_api_endpoint(url: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Test an API endpoint with the given data.
    
    Args:
        url (str): The API endpoint URL.
        data (Dict[str, Any]): The request data.
        
    Returns:
        Tuple[Dict[str, Any], int]: Response data and status code.
    """
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers, timeout=30)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {}, 500
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return {}, 500

def print_test_result(test_name: str, request_data: Dict[str, Any], response_data: Dict[str, Any], status_code: int):
    """
    Print formatted test results.
    
    Args:
        test_name (str): Name of the test.
        request_data (Dict[str, Any]): Request data sent.
        response_data (Dict[str, Any]): Response data received.
        status_code (int): HTTP status code.
    """
    print("=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)
    print("Request Data:")
    print(json.dumps(request_data, indent=2))
    print(f"\nStatus Code: {status_code}")
    print("Response:")
    print(json.dumps(response_data, indent=2))
    print("=" * 60)

def run_comprehensive_tests():
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
        "question": "How do you communicate with your team?",
        "response": "I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
        "type": "elaboration",
        "language": "English",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "communication", "importance": 80},
                {"name": "leadership", "importance": 60},
                {"name": "collaboration", "importance": 70}
            ]
        }
    }
    response_2, status_2 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_2)
    print_test_result("Theme = 'Yes', Theme Found", test_data_2, response_2, status_2)
    
    # Test 3: Theme = "Yes", No Theme Found
    print("\n3️⃣ Testing Theme = 'Yes', No Theme Found")
    test_data_3 = {
        "question": "What's your favorite color?",
        "response": "I like blue because it's calming.",
        "type": "reason",
        "language": "English",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "communication", "importance": 80},
                {"name": "leadership", "importance": 60},
                {"name": "collaboration", "importance": 70}
            ]
        }
    }
    response_3, status_3 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_3)
    print_test_result("Theme = 'Yes', No Theme Found", test_data_3, response_3, status_3)
    
    # Test 4: Non-informative response
    print("\n4️⃣ Testing Non-informative Response")
    test_data_4 = {
        "question": "What do you think about our new policy?",
        "response": "I don't know.",
        "type": "reason",
        "language": "English",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "communication", "importance": 80},
                {"name": "leadership", "importance": 60},
                {"name": "collaboration", "importance": 70}
            ]
        }
    }
    response_4, status_4 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_4)
    print_test_result("Non-informative Response", test_data_4, response_4, status_4)
    
    # Test 5: Multiple themes found (should pick highest importance)
    print("\n5️⃣ Testing Multiple Themes Found")
    test_data_5 = {
        "question": "How do you handle team conflicts?",
        "response": "I try to communicate openly and lead by example to foster collaboration.",
        "type": "impact",
        "language": "English",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "communication", "importance": 80},
                {"name": "leadership", "importance": 90},
                {"name": "collaboration", "importance": 70}
            ]
        }
    }
    response_5, status_5 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_5)
    print_test_result("Multiple Themes Found", test_data_5, response_5, status_5)
    
    # Test 6: Different language (Spanish)
    print("\n6️⃣ Testing Spanish Language")
    test_data_6 = {
        "question": "¿Cuáles son tus desafíos en el trabajo?",
        "response": "Tengo problemas con la gestión del tiempo y la comunicación.",
        "type": "reason",
        "language": "Spanish",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "communication", "importance": 80},
                {"name": "leadership", "importance": 60},
                {"name": "collaboration", "importance": 70}
            ]
        }
    }
    response_6, status_6 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_6)
    print_test_result("Spanish Language", test_data_6, response_6, status_6)
    
    # Test 7: Invalid request (missing theme_parameters when theme="Yes")
    print("\n7️⃣ Testing Invalid Request (Missing Theme Parameters)")
    test_data_7 = {
        "question": "What do you think about teamwork?",
        "response": "Teamwork is important for success.",
        "type": "reason",
        "language": "English",
        "theme": "Yes"
        # Missing theme_parameters
    }
    response_7, status_7 = test_api_endpoint(f"{base_url}/generate-theme-enhanced", test_data_7)
    print_test_result("Invalid Request", test_data_7, response_7, status_7)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Test 1 (Theme=No): {'PASS' if status_1 == 200 else 'FAIL'}")
    print(f"✅ Test 2 (Theme Found): {'PASS' if status_2 == 200 else 'FAIL'}")
    print(f"✅ Test 3 (No Theme): {'PASS' if status_3 == 200 else 'FAIL'}")
    print(f"✅ Test 4 (Non-informative): {'PASS' if status_4 == 200 else 'FAIL'}")
    print(f"✅ Test 5 (Multiple Themes): {'PASS' if status_5 == 200 else 'FAIL'}")
    print(f"✅ Test 6 (Spanish): {'PASS' if status_6 == 200 else 'FAIL'}")
    print(f"✅ Test 7 (Invalid Request): {'PASS' if status_7 == 422 else 'FAIL'}")
    
    # Detailed analysis
    print("\n🔍 DETAILED ANALYSIS")
    print("=" * 60)
    
    # Check theme detection
    if status_2 == 200 and response_2.get("detected_theme") == "communication":
        print("✅ Theme detection working correctly")
    else:
        print("❌ Theme detection not working as expected")
    
    # Check missing theme handling
    if status_3 == 200 and response_3.get("highest_importance_theme"):
        print("✅ Missing theme handling working correctly")
    else:
        print("❌ Missing theme handling not working as expected")
    
    # Check non-informative detection
    if status_4 == 200 and response_4.get("informative") == 0:
        print("✅ Non-informative detection working correctly")
    else:
        print("❌ Non-informative detection not working as expected")
    
    # Check multilingual support
    if status_6 == 200 and response_6.get("language") == "Spanish":
        print("✅ Multilingual support working correctly")
    else:
        print("❌ Multilingual support not working as expected")
    
    # Check validation
    if status_7 == 422:
        print("✅ Input validation working correctly")
    else:
        print("❌ Input validation not working as expected")

if __name__ == "__main__":
    run_comprehensive_tests() 