import os
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel
from requests.exceptions import RequestException, Timeout
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import time

class DeepSeekAPIError(Exception):
    """
    Custom exception for DeepSeek API errors.
    """
    pass

class DeepSeekService:
    """
    Service class for interacting with the DeepSeek LLM API.
    """
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    TIMEOUT = 15  # Increased timeout for better reliability
    RETRIES = 1   # Reduced retries to improve response time
    MAX_TOKENS = 300  # Reduced from 500 for faster generation

    def __init__(self):
        """
        Initialize the DeepSeekService.
        Uses the DeepSeek API key from environment variables.
        """
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided in environment variables.")
        self.logger = logging.getLogger("DeepSeekService")
        
        # Create a session with connection pooling for better performance
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["POST"],
            backoff_factor=0.5
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Simple in-memory cache for performance
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key for the prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                self.logger.info("Returning cached response")
                return cached_data
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache the response with timestamp."""
        self.cache[cache_key] = (response, time.time())
    
    def generate_questions(self, prompt: str) -> Dict[str, Any]:
        """
        Call DeepSeek API to generate follow-up questions.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            Dict[str, Any]: The API response JSON.

        Raises:
            DeepSeekAPIError: If the API call fails.
        """
        # Check cache first
        cache_key = self._get_cache_key(prompt)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Track performance
        start_time = time.time()
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Generate 2-3 follow-up questions for survey responses. Return JSON: {\"followups\": [{\"type\": \"reason|clarification|elaboration|example|impact|comparison\", \"text\": \"question\"}]}"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.5,  # Reduced for more focused responses
            "max_tokens": self.MAX_TOKENS
        }
        try:
            response = self.session.post(
                self.API_URL,
                headers=self._get_headers(),
                json=payload,
                timeout=self.TIMEOUT
            )
            if response.status_code == 200:
                response_data = response.json()
                # Cache the successful response
                self._cache_response(cache_key, response_data)
                
                # Log performance metrics
                elapsed_time = time.time() - start_time
                self.logger.info(f"DeepSeek API call completed in {elapsed_time:.2f}s")
                
                return response_data
            else:
                self.logger.error(f"DeepSeek API error: {response.status_code} {response.text}")
                raise DeepSeekAPIError(f"API error: {response.status_code} {response.text}")
        except (RequestException, Timeout) as exc:
            self.logger.error(f"DeepSeek API request failed: {exc}")
            raise DeepSeekAPIError(f"Request failed: {exc}")
    
    def cleanup_cache(self):
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def parse_response(self, api_response: dict) -> list:
        """
        Parse the DeepSeek API response to extract follow-up questions.

        Args:
            api_response (dict): The JSON response from DeepSeek API.

        Returns:
            list: List of follow-up question dicts with 'type' and 'text'.

        Raises:
            DeepSeekAPIError: If the response format is invalid or missing data.
        """
        try:
            # Extract the content from the chat completion response
            choices = api_response.get("choices", [])
            if not choices:
                raise DeepSeekAPIError("No choices in DeepSeek API response.")
            
            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise DeepSeekAPIError("No content in DeepSeek API response.")
            
            # Try to parse JSON from the content
            import json
            try:
                # Look for JSON in the response content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx == -1 or end_idx == 0:
                    raise DeepSeekAPIError("No JSON found in response content.")
                
                json_str = content[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                questions = parsed.get("followups", [])
                if not isinstance(questions, list):
                    raise DeepSeekAPIError("Invalid response: 'followups' field missing or not a list.")
                
                for q in questions:
                    if not (isinstance(q, dict) and "type" in q and "text" in q):
                        raise DeepSeekAPIError("Invalid followup question format in response.")
                
                return questions
            except json.JSONDecodeError:
                raise DeepSeekAPIError("Failed to parse JSON from DeepSeek response content.")
                
        except Exception as exc:
            self.logger.error(f"Failed to parse DeepSeek response: {exc}")
            raise DeepSeekAPIError(f"Failed to parse DeepSeek response: {exc}")

    @staticmethod
    def build_prompt(question: str, response: str, allowed_types: Optional[list] = None) -> str:
        """
        Build the prompt for the DeepSeek LLM.

        Args:
            question (str): The original survey question.
            response (str): The user's answer.
            allowed_types (Optional[list]): Allowed follow-up question types.

        Returns:
            str: The formatted prompt.
        """
        # Optimized prompt for faster processing
        types_str = f" Types: {','.join(allowed_types)}" if allowed_types else ""
        return f"Q: {question} A: {response}{types_str}. Generate 2-3 follow-up questions." 