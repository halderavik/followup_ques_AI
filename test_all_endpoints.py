#!/usr/bin/env python3
"""
Comprehensive test script for all Survey Intelligence API endpoints.
Tests functionality and reliability after 502 error fixes.
"""

import requests
import time
import json

# API endpoints
BASE_URL = "https://follow-up-question-f00b29aae45c.herokuapp.com"

def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Test a single endpoint and return results."""
    print(f"\n🔍 Testing: {name}")
    print(f"Endpoint: {method} {endpoint}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        else:
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=30
            )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == expected_status:
            print(f"✅ SUCCESS: {response.status_code} - {response_time:.2f}s")
            
            # Try to parse JSON response
            try:
                result = response.json()
                if isinstance(result, dict):
                    # Show key fields for different response types
                    if 'followups' in result:
                        print(f"   📝 Generated {len(result['followups'])} follow-up questions")
                        for i, followup in enumerate(result['followups'], 1):
                            print(f"   {i}. [{followup.get('type', 'N/A')}] {followup.get('text', 'N/A')}")
                    elif 'question' in result:
                        print(f"   📝 Generated question: {result['question']}")
                    elif 'question_types' in result:
                        print(f"   📝 Available types: {', '.join(result['question_types'])}")
                    elif 'status' in result:
                        print(f"   📝 Status: {result['status']}")
                    else:
                        print(f"   📝 Response: {json.dumps(result, indent=2)[:200]}...")
                else:
                    print(f"   📝 Response: {result}")
            except:
                print(f"   📝 Response: {response.text[:200]}...")
            
            return True, response_time
        else:
            print(f"❌ FAILED: {response.status_code} - {response_time:.2f}s")
            print(f"   Error: {response.text[:200]}...")
            return False, response_time
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False, 0

def test_all_endpoints():
    """Test all API endpoints comprehensively."""
    
    print("🚀 Comprehensive API Testing - Survey Intelligence API")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Health Check",
            "method": "GET",
            "endpoint": "/health",
            "data": None
        },
        {
            "name": "Question Types",
            "method": "GET", 
            "endpoint": "/question-types",
            "data": None
        },
        {
            "name": "Generate Followup (English)",
            "method": "POST",
            "endpoint": "/generate-followup",
            "data": {
                "question": "What challenges do you face at work?",
                "response": "I struggle with time management and communication."
            }
        },
        {
            "name": "Generate Reason (English)",
            "method": "POST",
            "endpoint": "/generate-reason",
            "data": {
                "question": "What challenges do you face at work?",
                "response": "I struggle with time management and communication."
            }
        },
        {
            "name": "Generate Multilingual (Chinese - Reason)",
            "method": "POST",
            "endpoint": "/generate-multilingual",
            "data": {
                "question": "你在工作中面临什么挑战？",
                "response": "我在时间管理和沟通方面有困难。",
                "type": "reason",
                "language": "Chinese"
            }
        },
        {
            "name": "Generate Multilingual (Japanese - Impact)",
            "method": "POST",
            "endpoint": "/generate-multilingual",
            "data": {
                "question": "仕事でどのような課題に直面していますか？",
                "response": "時間管理とコミュニケーションに苦労しています。",
                "type": "impact",
                "language": "Japanese"
            }
        },
        {
            "name": "Generate Multilingual (Spanish - Elaboration)",
            "method": "POST",
            "endpoint": "/generate-multilingual",
            "data": {
                "question": "¿Qué desafíos enfrentas en el trabajo?",
                "response": "Tengo dificultades con la gestión del tiempo y la comunicación.",
                "type": "elaboration",
                "language": "Spanish"
            }
        }
    ]
    
    results = []
    total_tests = len(test_cases)
    successful_tests = 0
    total_response_time = 0
    
    for test_case in test_cases:
        success, response_time = test_endpoint(
            test_case["name"],
            test_case["method"],
            test_case["endpoint"],
            test_case["data"]
        )
        
        results.append({
            "name": test_case["name"],
            "success": success,
            "response_time": response_time
        })
        
        if success:
            successful_tests += 1
            total_response_time += response_time
        
        print("-" * 50)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
    
    if successful_tests > 0:
        avg_response_time = total_response_time / successful_tests
        print(f"Average Response Time: {avg_response_time:.2f}s")
    
    print(f"\n🎯 ENDPOINT STATUS:")
    for result in results:
        status = "✅ WORKING" if result["success"] else "❌ FAILED"
        time_str = f" ({result['response_time']:.2f}s)" if result["response_time"] > 0 else ""
        print(f"  {result['name']}: {status}{time_str}")
    
    # Overall assessment
    if successful_tests == total_tests:
        print(f"\n🎉 ALL ENDPOINTS WORKING PERFECTLY!")
    elif successful_tests >= total_tests * 0.8:
        print(f"\n✅ MOST ENDPOINTS WORKING WELL!")
    else:
        print(f"\n⚠️  SOME ENDPOINTS NEED ATTENTION!")

if __name__ == "__main__":
    test_all_endpoints()