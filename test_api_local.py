#!/usr/bin/env python3
"""
Simple API test for informativeness detection
"""

import requests
import json
import time

def test_api():
    """Test the local API endpoint"""
    
    url = "http://localhost:5000/generate-enhanced-multilingual"
    
    # Test cases
    test_cases = [
        {
            "name": "Single word response",
            "payload": {
                "question": "What is your favorite color?",
                "response": "Blue",
                "type": "reason",
                "language": "en"
            }
        },
        {
            "name": "Short phrase response", 
            "payload": {
                "question": "How do you handle stress?",
                "response": "Exercise and meditation",
                "type": "reason",
                "language": "en"
            }
        },
        {
            "name": "Non-informative response",
            "payload": {
                "question": "What's your experience?",
                "response": "I don't know",
                "type": "reason",
                "language": "en"
            }
        }
    ]
    
    print("🧪 TESTING LOCAL API - FLEXIBLE INFORMATIVENESS")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Question: {test_case['payload']['question']}")
        print(f"Response: {test_case['payload']['response']}")
        
        try:
            start_time = time.time()
            response = requests.post(url, json=test_case['payload'], timeout=30)
            elapsed_time = time.time() - start_time
            
            print(f"Status: {response.status_code}")
            print(f"Time: {elapsed_time:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                informative = result.get('informative', 'N/A')
                question = result.get('question', 'N/A')
                
                print(f"Informative: {informative}")
                print(f"Generated Question: {question}")
                
                if informative == 1:
                    print("✅ Response correctly marked as informative")
                elif informative == 0:
                    print("✅ Response correctly marked as non-informative")
                else:
                    print("⚠️  Unexpected informative value")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n{'=' * 60}")
    print("Test completed!")

if __name__ == "__main__":
    test_api() 