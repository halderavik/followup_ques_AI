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
    TIMEOUT = 25  # Increased for reliability - prioritize working over speed
    RETRIES = 1   # Add back retries for reliability
    MAX_TOKENS = 80  # Keep optimized tokens

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
        
        # Configure retry strategy for reliability
        retry_strategy = Retry(
            total=self.RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            backoff_factor=0.3  # Balanced backoff for reliability
        )
        
        # Configure adapter with ultra-optimized connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=50,  # Increased from 20
            pool_maxsize=100,     # Increased from 50
            pool_block=False      # Don't block on connection pool exhaustion
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Pre-warm connection pool for faster initial requests
        try:
            self.session.get("https://api.deepseek.com", timeout=1)
        except:
            pass  # Ignore pre-warm failures
        
        # Simple in-memory cache for performance
        self.cache = {}
        self.cache_ttl = 900  # Reduced from 1800 to 15 minutes for faster cache invalidation

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
                    "content": "Generate 2-3 follow-up questions. Return ONLY valid JSON: {\"followups\": [{\"type\": \"reason|clarification|elaboration|example|impact|comparison\", \"text\": \"question\"}]}"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Balanced for reliability and speed
            "max_tokens": self.MAX_TOKENS,
            "top_p": 0.9,        # Back to standard for reliability
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False      # Keep no streaming for faster response
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
                # First, try to parse the entire content as JSON
                try:
                    parsed = json.loads(content.strip())
                    questions = parsed.get("followups", [])
                    if isinstance(questions, list) and questions:
                        return questions
                except json.JSONDecodeError:
                    pass
                
                # If that fails, look for JSON within the content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    try:
                        parsed = json.loads(json_str)
                        questions = parsed.get("followups", [])
                        if isinstance(questions, list) and questions:
                            return questions
                    except json.JSONDecodeError:
                        pass
                
                # If JSON parsing fails, try to extract questions from plain text
                self.logger.warning("JSON parsing failed, attempting to extract questions from plain text")
                questions = self._extract_questions_from_text(content)
                if questions:
                    return questions
                
                raise DeepSeekAPIError("Could not extract questions from response content.")
                
            except Exception as exc:
                self.logger.error(f"Failed to parse DeepSeek response: {exc}")
                raise DeepSeekAPIError(f"Failed to parse DeepSeek response: {exc}")
                
        except Exception as exc:
            self.logger.error(f"Failed to parse DeepSeek response: {exc}")
            raise DeepSeekAPIError(f"Failed to parse DeepSeek response: {exc}")

    def _extract_questions_from_text(self, content: str) -> list:
        """
        Extract questions from plain text when JSON parsing fails.
        
        Args:
            content (str): The response content as plain text.
            
        Returns:
            list: List of question dicts with 'type' and 'text'.
        """
        try:
            # Split content into lines and look for questions
            lines = content.strip().split('\n')
            questions = []
            
            # Common question patterns
            question_types = ['reason', 'clarification', 'elaboration', 'example', 'impact', 'comparison']
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                    
                # Remove numbering and common prefixes
                line = line.lstrip('0123456789.-* ')
                
                # Determine question type based on content
                question_type = 'reason'  # default
                for qtype in question_types:
                    if qtype in line.lower():
                        question_type = qtype
                        break
                
                # Check if it looks like a question
                if any(word in line.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who', '?']):
                    questions.append({
                        'type': question_type.upper(),
                        'text': line
                    })
            
            return questions[:3]  # Return max 3 questions
            
        except Exception as e:
            self.logger.error(f"Failed to extract questions from text: {e}")
            return []

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
        # Ultra-minimal prompt for fastest processing
        types_str = f" Types: {','.join(allowed_types)}" if allowed_types else ""
        return f"Q: {question} A: {response}{types_str}. Generate 2-3 questions."

    def generate_multilingual_question(self, question: str, response: str, question_type: str, language: str) -> str:
        """
        Generate a single multilingual follow-up question.

        Args:
            question (str): The original survey question.
            response (str): The user's answer.
            question_type (str): The type of follow-up question.
            language (str): The target language.

        Returns:
            str: The generated question in the target language.

        Raises:
            DeepSeekAPIError: If the API call fails.
        """
        # Create cache key including language and type for better caching
        cache_key = self._get_cache_key(f"{question}:{response}:{question_type}:{language}")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        # Track performance
        start_time = time.time()
        
        # Build optimized multilingual prompt
        prompt = self._build_multilingual_prompt(question, response, question_type, language)
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": f"Generate 1 question in {language}. Return only the question text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,  # Balanced for reliability and speed
            "max_tokens": 80,     # Keep optimized but reliable
            "top_p": 0.9,        # Back to standard for reliability
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False      # Keep no streaming for faster response
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
                
                # Extract the question text directly
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    raise DeepSeekAPIError("No content in multilingual response.")
                
                # Clean up the response (remove quotes, extra whitespace)
                question_text = content.strip().strip('"').strip("'")
                
                # Cache the response
                self._cache_response(cache_key, question_text)
                
                # Log performance metrics
                elapsed_time = time.time() - start_time
                self.logger.info(f"Multilingual API call completed in {elapsed_time:.2f}s")
                
                return question_text
            else:
                self.logger.error(f"DeepSeek API error: {response.status_code} {response.text}")
                raise DeepSeekAPIError(f"API error: {response.status_code} {response.text}")
        except (RequestException, Timeout) as exc:
            self.logger.error(f"Multilingual API request failed: {exc}")
            raise DeepSeekAPIError(f"Request failed: {exc}")

    @staticmethod
    def _build_multilingual_prompt(question: str, response: str, question_type: str, language: str) -> str:
        """
        Build optimized prompt for multilingual question generation.

        Args:
            question (str): The original survey question (in the target language).
            response (str): The user's answer (in the target language).
            question_type (str): The type of follow-up question.
            language (str): The target language.

        Returns:
            str: The formatted multilingual prompt.
        """
        # Ultra-minimal prompt for fastest multilingual generation
        type_instructions = {
            "reason": "why",
            "impact": "effects", 
            "elaboration": "details",
            "example": "examples",
            "clarification": "clarify",
            "comparison": "compare"
        }
        
        instruction = type_instructions.get(question_type.lower(), "follow-up")
        
        # Since question and response are already in the target language,
        # we just need to ask for a follow-up question in the same language
        return f"Q: {question} A: {response}. Ask {instruction} in {language}." 