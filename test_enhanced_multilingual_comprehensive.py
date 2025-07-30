#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced multilingual API endpoint with informativeness detection.
This script tests various scenarios including informative and non-informative responses in multiple languages.
"""

import urllib.request
import urllib.parse
import json
import time

def test_enhanced_multilingual_api():
    """Test the enhanced multilingual API endpoint comprehensively."""
    
    base_url = "http://localhost:5000"
    
    # Test cases
    test_cases = [
        # English tests
        {
            "name": "English Informative Response",
            "data": {
                "question": "What challenges do you face at work?",
                "response": "I struggle with time management and communication with my team.",
                "type": "reason",
                "language": "English"
            },
            "expected_informative": 1
        },
        {
            "name": "English Non-informative Response",
            "data": {
                "question": "What challenges do you face at work?",
                "response": "I don't know",
                "type": "reason",
                "language": "English"
            },
            "expected_informative": 0
        },
        {
            "name": "English Short Response",
            "data": {
                "question": "What challenges do you face at work?",
                "response": "No",
                "type": "reason",
                "language": "English"
            },
            "expected_informative": 0
        },
        
        # Chinese tests
        {
            "name": "Chinese Informative Response",
            "data": {
                "question": "你在工作中面临什么挑战？",
                "response": "我在时间管理和沟通方面有困难。",
                "type": "reason",
                "language": "Chinese"
            },
            "expected_informative": 1
        },
        {
            "name": "Chinese Non-informative Response",
            "data": {
                "question": "你在工作中面临什么挑战？",
                "response": "我不知道",
                "type": "reason",
                "language": "Chinese"
            },
            "expected_informative": 0
        },
        
        # Spanish tests
        {
            "name": "Spanish Informative Response",
            "data": {
                "question": "¿Qué desafíos enfrentas en el trabajo?",
                "response": "Tengo dificultades con la gestión del tiempo y la comunicación.",
                "type": "impact",
                "language": "Spanish"
            },
            "expected_informative": 1
        },
        {
            "name": "Spanish Non-informative Response",
            "data": {
                "question": "¿Qué desafíos enfrentas en el trabajo?",
                "response": "No sé",
                "type": "impact",
                "language": "Spanish"
            },
            "expected_informative": 0
        },
        
        # French tests
        {
            "name": "French Informative Response",
            "data": {
                "question": "Quels défis rencontrez-vous au travail ?",
                "response": "J'ai des difficultés avec la gestion du temps et la communication.",
                "type": "example",
                "language": "French"
            },
            "expected_informative": 1
        },
        {
            "name": "French Non-informative Response",
            "data": {
                "question": "Quels défis rencontrez-vous au travail ?",
                "response": "Je ne sais pas",
                "type": "example",
                "language": "French"
            },
            "expected_informative": 0
        }
    ]
    
    print("=== Enhanced Multilingual API Comprehensive Test ===\n")
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}/{total_tests}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Make API request
            url = f"{base_url}/generate-enhanced-multilingual"
            json_data = json.dumps(test_case['data']).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
            
            start_time = time.time()
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                elapsed_time = time.time() - start_time
            
            # Validate response structure
            required_fields = ['informative', 'question', 'original_question', 'original_response', 'type', 'language']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"❌ FAILED: Missing required fields: {missing_fields}")
                continue
            
            # Check informativeness
            actual_informative = result['informative']
            expected_informative = test_case['expected_informative']
            
            if actual_informative == expected_informative:
                print(f"✅ PASSED: Informativeness detection correct ({actual_informative})")
                passed_tests += 1
            else:
                print(f"❌ FAILED: Expected informative={expected_informative}, got {actual_informative}")
            
            # Display response details
            print(f"   Response Time: {elapsed_time:.2f}s")
            print(f"   Status Code: {response.status}")
            print(f"   Language: {result['language']}")
            print(f"   Type: {result['type']}")
            print(f"   Question: {result['question'] if result['question'] else 'None'}")
            print()
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            print()
    
    # Summary
    print("=" * 60)
    print(f"Test Summary: {passed_tests}/{total_tests} tests passed")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The enhanced multilingual API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    print("=" * 60)

def test_error_handling():
    """Test error handling scenarios."""
    
    print("\n=== Error Handling Tests ===\n")
    
    base_url = "http://localhost:5000"
    url = f"{base_url}/generate-enhanced-multilingual"
    
    # Test 1: Invalid JSON
    print("Test 1: Invalid JSON")
    try:
        req = urllib.request.Request(url, data=b"invalid json", headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            print(f"❌ FAILED: Should have returned 400 error, got {response.status}")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print(f"✅ PASSED: Correctly returned 400 error for invalid JSON")
        else:
            print(f"❌ FAILED: Expected 400 error, got {e.code}")
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
    
    # Test 2: Missing required fields
    print("\nTest 2: Missing required fields")
    try:
        data = {"question": "Test question"}  # Missing response, type, language
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            print(f"❌ FAILED: Should have returned 422 error, got {response.status}")
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print(f"✅ PASSED: Correctly returned 422 error for missing fields")
        else:
            print(f"❌ FAILED: Expected 422 error, got {e.code}")
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")

if __name__ == "__main__":
    test_enhanced_multilingual_api()
    test_error_handling() 