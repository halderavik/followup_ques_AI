#!/usr/bin/env python3
"""
Final test to verify the leading quote fix is working on the live API.
"""

import requests
import json

def test_final_fix():
    """Test the live API to verify leading quote fix."""
    
    url = "https://follow-up-question-f00b29aae45c.herokuapp.com/generate-followup"
    
    data = {
        "question": "What do you think about basketball?",
        "response": "I think the NBA is often associated with more than just the sport of basketball."
    }
    
    print("🧪 Testing Final Fix - Leading Quote Removal")
    print("=" * 50)
    print(f"Testing: {url}")
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {response.status_code}")
            
            # Check if questions are clean
            if 'followups' in result:
                print(f"\n📝 Generated {len(result['followups'])} questions:")
                for i, followup in enumerate(result['followups'], 1):
                    question_text = followup.get('text', '')
                    question_type = followup.get('type', '')
                    
                    # Check for leading quotes
                    if question_text.startswith('"'):
                        print(f"  {i}. ❌ STILL HAS LEADING QUOTE: {question_text}")
                    else:
                        print(f"  {i}. ✅ CLEAN: [{question_type}] {question_text}")
                        
                    # Check for trailing quotes
                    if question_text.endswith('"'):
                        print(f"     ⚠️  Has trailing quote")
            else:
                print("❌ No followups in response")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_final_fix()