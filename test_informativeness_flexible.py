#!/usr/bin/env python3
"""
Test script to verify the more flexible informativeness detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.deepseek_service import DeepSeekService

def test_informativeness():
    """Test the updated informativeness detection with various response types"""
    
    service = DeepSeekService()
    
    # Test cases with different response types
    test_cases = [
        {
            "question": "What is your favorite color?",
            "response": "Blue",
            "expected": "informative (single word)"
        },
        {
            "question": "How do you handle stress?",
            "response": "Exercise",
            "expected": "informative (single word)"
        },
        {
            "question": "What motivates you at work?",
            "response": "Money",
            "expected": "informative (single word)"
        },
        {
            "question": "Describe your leadership style",
            "response": "Democratic",
            "expected": "informative (single word)"
        },
        {
            "question": "What's your biggest strength?",
            "response": "Communication",
            "expected": "informative (single word)"
        },
        {
            "question": "How do you solve problems?",
            "response": "I don't know",
            "expected": "non-informative"
        },
        {
            "question": "What's your experience with teamwork?",
            "response": "n/a",
            "expected": "non-informative"
        },
        {
            "question": "Tell me about your goals",
            "response": "skip",
            "expected": "non-informative"
        },
        {
            "question": "What's your preferred work environment?",
            "response": "Quiet office",
            "expected": "informative (short phrase)"
        },
        {
            "question": "How do you learn new skills?",
            "response": "Online courses",
            "expected": "informative (short phrase)"
        }
    ]
    
    print("🧪 TESTING FLEXIBLE INFORMATIVENESS DETECTION")
    print("=" * 60)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['expected']}")
        print(f"Q: {test_case['question']}")
        print(f"A: {test_case['response']}")
        
        try:
            is_informative = service.detect_informativeness(
                test_case['question'], 
                test_case['response'], 
                "English"
            )
            
            status = "✅ INFORMATIVE" if is_informative else "❌ NON-INFORMATIVE"
            expected_status = "informative" if "informative" in test_case['expected'] else "non-informative"
            
            if (is_informative and "informative" in test_case['expected']) or \
               (not is_informative and "non-informative" in test_case['expected']):
                result = "✅ PASS"
            else:
                result = "❌ FAIL"
            
            print(f"Result: {status} | {result}")
            results.append(result)
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append("❌ ERROR")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}")
    
    passed = results.count("✅ PASS")
    failed = results.count("❌ FAIL")
    errors = results.count("❌ ERROR")
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Errors: {errors}")
    print(f"📊 Success Rate: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Informativeness detection is working flexibly.")
    else:
        print(f"\n⚠️  {failed + errors} tests failed. Check the implementation.")

if __name__ == "__main__":
    test_informativeness() 