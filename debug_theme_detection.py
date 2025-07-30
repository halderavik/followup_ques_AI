#!/usr/bin/env python3
"""
Debug script for theme detection.
"""

import os
import requests
import json

def debug_theme_detection():
    """Debug the theme detection logic."""
    
    # Test data
    response = "I struggle with communication issues and team collaboration."
    themes = [
        {"name": "leadership", "importance": 80},
        {"name": "communication", "importance": 60},
        {"name": "technology", "importance": 40}
    ]
    
    # Build the prompt
    themes_str = ", ".join([f"'{t['name']}' (importance: {t['importance']}%)" for t in themes])
    
    prompt = f"""Analyze this response for theme matches:

Response: "{response}"

Available themes: {themes_str}

Return ONLY a JSON object like this:
{{"theme_name": "theme_name", "importance": importance_number}}

If no themes are found, return:
{{"theme_name": "none", "importance": 0}}

Choose the theme with the highest importance if multiple themes are found."""
    
    print("🔍 DEBUGGING THEME DETECTION")
    print("=" * 50)
    print(f"Response: {response}")
    print(f"Themes: {themes}")
    print(f"Prompt: {prompt}")
    
    # Make the API call
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "Analyze the response for theme matches. Return ONLY a JSON object with 'theme_name' and 'importance' or 'none' if no themes found."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 50,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stream": False
    }
    
    try:
        response_data = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        response_data.raise_for_status()
        
        result = response_data.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        print(f"\n🤖 AI Response: {content}")
        
        # Try to parse JSON
        try:
            theme_result = json.loads(content)
            print(f"✅ JSON Parsed Successfully: {theme_result}")
            
            if theme_result.get("theme_name") == "none":
                print("❌ No theme detected")
            else:
                print(f"✅ Theme detected: {theme_result.get('theme_name')} (importance: {theme_result.get('importance')})")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw content: {repr(content)}")
            
    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    debug_theme_detection() 