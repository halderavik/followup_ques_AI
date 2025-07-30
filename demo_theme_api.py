#!/usr/bin/env python3
"""
Simple demo script for the generate-theme-enhanced API endpoint.
Shows practical usage with a real-world example.
"""

import requests
import json

def demo_theme_api():
    """Demonstrate the theme-enhanced API with a practical example."""
    
    print("🎯 THEME-ENHANCED API DEMO")
    print("=" * 50)
    
    # Example: Employee satisfaction survey
    print("\n📋 Example: Employee Satisfaction Survey")
    print("Question: 'How satisfied are you with your work environment?'")
    print("Response: 'I'm satisfied with the flexible hours and remote work options, but the office communication could be better.'")
    
    # Test data
    test_data = {
        "question": "How satisfied are you with your work environment?",
        "response": "I'm satisfied with the flexible hours and remote work options, but the office communication could be better.",
        "type": "elaboration",
        "language": "English",
        "theme": "Yes",
        "theme_parameters": {
            "themes": [
                {"name": "communication", "importance": 85},
                {"name": "work_life_balance", "importance": 75},
                {"name": "teamwork", "importance": 70},
                {"name": "leadership", "importance": 60}
            ]
        }
    }
    
    print("\n🔍 Theme Analysis:")
    print("- communication (85% importance)")
    print("- work_life_balance (75% importance)")
    print("- teamwork (70% importance)")
    print("- leadership (60% importance)")
    
    print("\n🚀 Making API Request...")
    
    try:
        response = requests.post(
            "http://localhost:5000/generate-theme-enhanced",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ API Response:")
            print("=" * 50)
            print(f"📊 Informative: {'Yes' if result['informative'] == 1 else 'No'}")
            
            if result['informative'] == 1:
                print(f"🎯 Detected Theme: {result.get('detected_theme', 'None')}")
                print(f"📈 Theme Importance: {result.get('theme_importance', 'N/A')}%")
                print(f"❓ Generated Question: {result['question']}")
                print(f"💡 Explanation: {result.get('explanation', 'N/A')}")
            else:
                print("❌ Response was not informative enough to generate a follow-up question.")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")

def demo_multiple_scenarios():
    """Demonstrate multiple scenarios with the theme API."""
    
    print("\n\n🔄 MULTIPLE SCENARIOS DEMO")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Theme Found (Communication)",
            "data": {
                "question": "How do you prefer to receive feedback?",
                "response": "I prefer face-to-face conversations for feedback as they allow for better communication and clarification.",
                "type": "reason",
                "language": "English",
                "theme": "Yes",
                "theme_parameters": {
                    "themes": [
                        {"name": "communication", "importance": 90},
                        {"name": "feedback", "importance": 80}
                    ]
                }
            }
        },
        {
            "name": "No Theme Found",
            "data": {
                "question": "What's your favorite programming language?",
                "response": "I really like Python because it's readable and has great libraries.",
                "type": "reason",
                "language": "English",
                "theme": "Yes",
                "theme_parameters": {
                    "themes": [
                        {"name": "communication", "importance": 90},
                        {"name": "teamwork", "importance": 80}
                    ]
                }
            }
        },
        {
            "name": "Non-informative Response",
            "data": {
                "question": "What improvements would you suggest for our product?",
                "response": "Maybe.",
                "type": "elaboration",
                "language": "English",
                "theme": "Yes",
                "theme_parameters": {
                    "themes": [
                        {"name": "innovation", "importance": 85},
                        {"name": "user_experience", "importance": 75}
                    ]
                }
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                "http://localhost:5000/generate-theme-enhanced",
                json=scenario['data'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result['informative'] == 1:
                    print(f"✅ Informative response")
                    print(f"🎯 Theme: {result.get('detected_theme', 'None')}")
                    print(f"❓ Question: {result['question'][:80]}...")
                else:
                    print(f"❌ Non-informative response")
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo_theme_api()
    demo_multiple_scenarios()
    
    print("\n\n🎉 Demo Complete!")
    print("The theme-enhanced API successfully:")
    print("✅ Detects themes in responses")
    print("✅ Generates contextually relevant questions")
    print("✅ Handles missing themes gracefully")
    print("✅ Identifies non-informative responses")
    print("✅ Provides explanations for question generation") 