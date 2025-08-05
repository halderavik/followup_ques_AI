import requests
import time
import json

def test_deployed_api():
    """Test the deployed API with current model"""
    url = "https://followup-ai-questions-e534ed0185cb.herokuapp.com/generate-followup"
    
    payload = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with time management and communication with my team.",
        "allowed_types": ["reason"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing DEPLOYED API (current model)...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        elapsed_time = time.time() - start_time
        
        print(f"✅ Deployed API Response Time: {elapsed_time:.2f}s")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Generated Question: {result['followups'][0]['text']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Deployed API Error: {e}")

def test_local_6_7b():
    """Test local API with 6.7B model"""
    url = "http://localhost:5000/generate-followup"
    
    payload = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with time management and communication with my team.",
        "allowed_types": ["reason"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("\nTesting LOCAL API (optimized parameters)...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        elapsed_time = time.time() - start_time
        
        print(f"✅ Local Optimized API Response Time: {elapsed_time:.2f}s")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Generated Question: {result['followups'][0]['text']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Local API Error: {e}")

if __name__ == "__main__":
    print("🚀 Performance Comparison Test: Deployed vs Local Optimized Model")
    print("=" * 60)
    
    # Test deployed API first
    test_deployed_api()
    
    # Test local 6.7B model
    test_local_6_7b()
    
    print("\n" + "=" * 60)
    print("Test completed! Compare the response times above.") 