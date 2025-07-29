#!/usr/bin/env python3
"""
Performance test script for the Survey Intelligence API.
Tests all endpoints to measure response times after optimization.
"""

import requests
import time
import statistics

# API endpoints
BASE_URL = "https://follow-up-question-f00b29aae45c.herokuapp.com"

def test_endpoint_performance():
    """Test performance of all API endpoints."""
    
    test_cases = [
        {
            "name": "Generate Followup (English)",
            "endpoint": "/generate-followup",
            "method": "POST",
            "data": {
                "question": "What challenges do you face at work?",
                "response": "I struggle with time management and communication."
            }
        },
        {
            "name": "Generate Reason (English)",
            "endpoint": "/generate-reason", 
            "method": "POST",
            "data": {
                "question": "What challenges do you face at work?",
                "response": "I struggle with time management and communication."
            }
        },
        {
            "name": "Generate Multilingual (Chinese)",
            "endpoint": "/generate-multilingual",
            "method": "POST", 
            "data": {
                "question": "你在工作中面临什么挑战？",
                "response": "我在时间管理和沟通方面有困难。",
                "type": "reason",
                "language": "Chinese"
            }
        },
        {
            "name": "Generate Multilingual (Japanese)",
            "endpoint": "/generate-multilingual",
            "method": "POST",
            "data": {
                "question": "仕事でどのような課題に直面していますか？",
                "response": "時間管理とコミュニケーションに苦労しています。",
                "type": "impact",
                "language": "Japanese"
            }
        }
    ]
    
    print("🚀 Performance Testing - Survey Intelligence API")
    print("=" * 60)
    
    results = {}
    
    for test_case in test_cases:
        print(f"\n📊 Testing: {test_case['name']}")
        print(f"Endpoint: {test_case['endpoint']}")
        
        response_times = []
        success_count = 0
        total_tests = 3  # Test each endpoint 3 times
        
        for i in range(total_tests):
            try:
                start_time = time.time()
                
                if test_case['method'] == 'POST':
                    response = requests.post(
                        f"{BASE_URL}{test_case['endpoint']}",
                        headers={"Content-Type": "application/json"},
                        json=test_case['data'],
                        timeout=15
                    )
                else:
                    response = requests.get(
                        f"{BASE_URL}{test_case['endpoint']}",
                        timeout=15
                    )
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"  Test {i+1}: ✅ {response_time:.2f}s")
                else:
                    print(f"  Test {i+1}: ❌ {response.status_code} - {response_time:.2f}s")
                    
            except Exception as e:
                print(f"  Test {i+1}: ❌ Exception - {str(e)}")
        
        # Calculate statistics
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            results[test_case['name']] = {
                'avg': avg_time,
                'min': min_time,
                'max': max_time,
                'success_rate': success_count / total_tests
            }
            
            print(f"\n📈 Results for {test_case['name']}:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  Min: {min_time:.2f}s")
            print(f"  Max: {max_time:.2f}s")
            print(f"  Success Rate: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
            
            # Performance assessment
            if avg_time <= 3.0:
                print(f"  🎯 Performance: EXCELLENT (≤3s target achieved)")
            elif avg_time <= 5.0:
                print(f"  ⚡ Performance: GOOD (≤5s)")
            else:
                print(f"  ⚠️  Performance: NEEDS IMPROVEMENT (>5s)")
        
        print("-" * 40)
    
    # Summary
    print(f"\n🎯 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    for name, stats in results.items():
        status = "🎯 EXCELLENT" if stats['avg'] <= 3.0 else "⚡ GOOD" if stats['avg'] <= 5.0 else "⚠️  NEEDS WORK"
        print(f"{name}: {stats['avg']:.2f}s avg - {status}")
    
    # Overall assessment
    all_avg_times = [stats['avg'] for stats in results.values()]
    overall_avg = statistics.mean(all_avg_times)
    
    print(f"\n📊 Overall Average Response Time: {overall_avg:.2f}s")
    
    if overall_avg <= 3.0:
        print("🎉 SUCCESS: All endpoints achieving 2-3 second target!")
    elif overall_avg <= 5.0:
        print("✅ GOOD: Most endpoints performing well")
    else:
        print("⚠️  NEEDS OPTIMIZATION: Response times still too high")

if __name__ == "__main__":
    test_endpoint_performance()