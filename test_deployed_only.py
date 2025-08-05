import requests
import time

def test_deployed_api():
    """Test the deployed API performance"""
    url = "https://followup-ai-questions-e534ed0185cb.herokuapp.com/generate-followup"
    
    payload = {
        "question": "What challenges do you face at work?",
        "response": "I struggle with time management and communication with my team.",
        "allowed_types": ["reason"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing DEPLOYED API Performance...")
    print("=" * 50)
    
    # Run multiple tests for average
    times = []
    for i in range(3):
        print(f"Test {i+1}/3...")
        start_time = time.time()
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            elapsed_time = time.time() - start_time
            times.append(elapsed_time)
            
            print(f"  Response Time: {elapsed_time:.2f}s")
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Question: {result['followups'][0]['text']}")
            else:
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print("\n" + "=" * 50)
        print(f"📊 Performance Summary:")
        print(f"  Average Time: {avg_time:.2f}s")
        print(f"  Min Time: {min_time:.2f}s")
        print(f"  Max Time: {max_time:.2f}s")
        print(f"  Tests: {len(times)}")

if __name__ == "__main__":
    test_deployed_api() 