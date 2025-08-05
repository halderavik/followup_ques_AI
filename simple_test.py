#!/usr/bin/env python3
"""
Simple test for informativeness detection with complex real-life scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.deepseek_service import OpenAIService

def test_scenario(service, question, response, scenario_name):
    """Test a single scenario and print results"""
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*60}")
    print(f"Question: {question}")
    print(f"Response: {response}")
    
    try:
        is_informative = service.detect_informativeness(question, response, "English")
        print(f"Result: {'✅ Informative' if is_informative else '❌ Non-informative'}")
        return is_informative
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("Testing informativeness detection with complex real-life scenarios...")
    
    service = OpenAIService()
    
    # Define test scenarios
    scenarios = [
        {
            "name": "Business Credit Preference - Short but Informative",
            "question": "What are the main reasons you prefer to use your business credit (e.g. corporate liability) when signing up for or switching to a mobile business service? Please use the box to share those",
            "response": "convenience"
        },
        {
            "name": "Customer Service Experience - Concise Answer",
            "question": "Please describe your recent experience with our customer service team. What went well and what could be improved?",
            "response": "helpful"
        },
        {
            "name": "Product Satisfaction - Brief but Meaningful",
            "question": "How satisfied are you with our product? Please provide specific details about what you like or dislike, and any suggestions for improvement.",
            "response": "excellent"
        },
        {
            "name": "Workplace Culture - Short Response",
            "question": "What aspects of our workplace culture contribute most to your job satisfaction? Please elaborate on specific examples and experiences.",
            "response": "flexibility"
        },
        {
            "name": "Technology Adoption - Single Word Answer",
            "question": "What factors influenced your decision to adopt this new technology platform? Please share your thought process and any concerns you had.",
            "response": "efficiency"
        },
        {
            "name": "Healthcare Provider Choice - Brief but Informative",
            "question": "What were the most important factors you considered when choosing your current healthcare provider? Please explain your decision-making process.",
            "response": "reputation"
        },
        {
            "name": "Educational Program Feedback - Concise",
            "question": "How has this educational program impacted your professional development? Please provide specific examples of skills gained and how you've applied them.",
            "response": "valuable"
        },
        {
            "name": "Travel Booking Experience - Short Answer",
            "question": "What aspects of your recent travel booking experience would you like us to know about? Please share both positive and negative feedback.",
            "response": "smooth"
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        result = test_scenario(
            service, 
            scenario["question"], 
            scenario["response"], 
            scenario["name"]
        )
        results.append((scenario["name"], result))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    informative_count = 0
    total_tests = len(results)
    
    for name, result in results:
        if result is True:
            informative_count += 1
            print(f"✅ {name}: Informative")
        elif result is False:
            print(f"❌ {name}: Non-informative")
        else:
            print(f"⚠️  {name}: Error occurred")
    
    print(f"\nOverall Results: {informative_count}/{total_tests} scenarios classified as informative")
    
    if informative_count == total_tests:
        print("🎉 All tests passed! The system correctly identifies short but informative answers.")
    elif informative_count > total_tests * 0.7:
        print("👍 Most tests passed! The system generally handles complex scenarios well.")
    else:
        print("⚠️  Several tests failed. The system may need adjustment for complex scenarios.")

if __name__ == "__main__":
    main() 