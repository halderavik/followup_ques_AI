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

    def _clean_question_text(self, text: str) -> str:
        """
        Clean up question text by removing JSON artifacts and formatting.
        
        Args:
            text (str): Raw question text that may contain JSON artifacts.
            
        Returns:
            str: Clean question text.
        """
        if not text:
            return text
            
        # Remove "text": " prefix and trailing quotes
        if text.startswith('"text": "') and text.endswith('"'):
            text = text[8:-1]  # Remove "text": " and trailing "
        elif text.startswith('"text":'):
            text = text[7:].strip().strip('"')
        
        # Remove any remaining JSON artifacts
        text = text.replace('\\"', '"')  # Unescape quotes
        text = text.replace('\\n', ' ')  # Replace newlines with spaces
        
        # Remove any remaining quotes at the beginning or end
        text = text.strip().strip('"').strip("'")
        
        # Remove any leading quotes that might still be there
        while text.startswith('"') or text.startswith("'"):
            text = text[1:]
        
        # Remove any trailing quotes
        while text.endswith('"') or text.endswith("'"):
            text = text[:-1]
        
        return text.strip()

    def parse_response(self, api_response: dict) -> list:
        """
        Parse the DeepSeek API response to extract follow-up questions.

        Args:
            api_response (dict): The raw API response from DeepSeek.

        Returns:
            list: List of question dictionaries with 'type' and 'text' fields.

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
                        # Convert question types to lowercase to match enum and clean text
                        for question in questions:
                            if isinstance(question, dict) and "type" in question:
                                question["type"] = question["type"].lower()
                            if isinstance(question, dict) and "text" in question:
                                question["text"] = self._clean_question_text(question["text"])
                        
                        # Ensure we have exactly 3 questions with the required types
                        return self._ensure_three_questions(questions)
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
                            # Convert question types to lowercase to match enum and clean text
                            for question in questions:
                                if isinstance(question, dict) and "type" in question:
                                    question["type"] = question["type"].lower()
                                if isinstance(question, dict) and "text" in question:
                                    question["text"] = self._clean_question_text(question["text"])
                            
                            # Ensure we have exactly 3 questions with the required types
                            return self._ensure_three_questions(questions)
                    except json.JSONDecodeError:
                        pass
                
                # If JSON parsing fails, try to extract questions from plain text
                self.logger.warning("JSON parsing failed, attempting to extract questions from plain text")
                questions = self._extract_questions_from_text(content)
                if questions:
                    return self._ensure_three_questions(questions)
                
                raise DeepSeekAPIError("Could not extract questions from response content.")
                
            except Exception as exc:
                self.logger.error(f"Failed to parse DeepSeek response: {exc}")
                raise DeepSeekAPIError(f"Failed to parse DeepSeek response: {exc}")
                
        except Exception as exc:
            self.logger.error(f"Failed to parse DeepSeek response: {exc}")
            raise DeepSeekAPIError(f"Failed to parse DeepSeek response: {exc}")

    def _ensure_three_questions(self, questions: list) -> list:
        """
        Ensure exactly 3 questions with the required types: reason, example, impact.
        
        Args:
            questions (list): List of question dictionaries.
            
        Returns:
            list: Exactly 3 questions with the required types.
        """
        self.logger.info(f"Ensuring 3 questions from {len(questions)} input questions")
        
        required_types = ['reason', 'example', 'impact']
        result = []
        
        # Type mapping for similar types
        type_mapping = {
            'elaboration': 'reason',
            'clarification': 'reason',
            'why': 'reason',
            'examples': 'example',
            'instance': 'example',
            'case': 'example',
            'effects': 'impact',
            'consequences': 'impact',
            'results': 'impact',
            'outcomes': 'impact'
        }
        
        # First, try to find questions with the exact required types
        for req_type in required_types:
            found = False
            for question in questions:
                if isinstance(question, dict) and question.get('type', '').lower() == req_type:
                    result.append(question)
                    found = True
                    self.logger.info(f"Found exact match for {req_type}")
                    break
            
            # If not found, try to map similar types
            if not found:
                for question in questions:
                    question_type = question.get('type', '').lower()
                    if question_type in type_mapping and type_mapping[question_type] == req_type:
                        # Update the type to the required type
                        question['type'] = req_type
                        result.append(question)
                        found = True
                        self.logger.info(f"Mapped {question_type} to {req_type}")
                        break
            
            # If we still didn't find a question with this type, create a default one
            if not found:
                result.append({
                    'type': req_type,
                    'text': f"Please provide more details about {req_type}."
                })
                self.logger.info(f"Created default question for {req_type}")
        
        # Ensure we have exactly 3 questions
        final_result = result[:3]
        self.logger.info(f"Final result: {[q.get('type', 'unknown') for q in final_result]}")
        return final_result

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
                
                # Clean up the line using the cleaning function
                line = self._clean_question_text(line)
                
                # Determine question type based on content
                question_type = 'reason'  # default
                for qtype in question_types:
                    if qtype in line.lower():
                        question_type = qtype
                        break
                
                # Check if it looks like a question
                if any(word in line.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who', '?']):
                    questions.append({
                        'type': question_type,  # Keep lowercase to match enum
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
        # For the main follow-up API, always generate exactly 3 questions with specific types
        return f"Q: {question} A: {response}. Generate exactly 3 follow-up questions with these EXACT types: 1) type: 'reason' - ask why, 2) type: 'example' - ask for examples, 3) type: 'impact' - ask about effects. Return ONLY valid JSON with 'followups' array containing 3 objects with 'type' and 'text' fields."

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

    def detect_informativeness(self, question: str, response: str, language: str = "English") -> bool:
        """
        Detect if a response is informative enough to warrant follow-up questions.

        Args:
            question (str): The original survey question.
            response (str): The user's answer.
            language (str): The language of the question and response.

        Returns:
            bool: True if response is informative, False if non-informative.

        Raises:
            DeepSeekAPIError: If the API call fails.
        """
        # Create cache key for informativeness detection
        cache_key = self._get_cache_key(f"informativeness:{question}:{response}:{language}")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        # Track performance
        start_time = time.time()
        
        # Build prompt for informativeness detection
        prompt = self._build_informativeness_prompt(question, response, language)
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": f"Analyze if the response is informative. Return ONLY '1' for informative or '0' for non-informative."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Very low temperature for consistent classification
            "max_tokens": 10,    # Very short response needed
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False
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
                
                # Extract the classification result
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    raise DeepSeekAPIError("No content in informativeness response.")
                
                # Parse the result (should be "1" or "0")
                result = content.strip()
                is_informative = result == "1"
                
                # Cache the result
                self._cache_response(cache_key, is_informative)
                
                # Log performance metrics
                elapsed_time = time.time() - start_time
                self.logger.info(f"Informativeness detection completed in {elapsed_time:.2f}s")
                
                return is_informative
            else:
                self.logger.error(f"DeepSeek API error: {response.status_code} {response.text}")
                raise DeepSeekAPIError(f"API error: {response.status_code} {response.text}")
        except (RequestException, Timeout) as exc:
            self.logger.error(f"Informativeness detection request failed: {exc}")
            raise DeepSeekAPIError(f"Request failed: {exc}")

    @staticmethod
    def _build_informativeness_prompt(question: str, response: str, language: str) -> str:
        """
        Build prompt for informativeness detection.

        Args:
            question (str): The original survey question.
            response (str): The user's answer.
            language (str): The language of the question and response.

        Returns:
            str: The formatted informativeness detection prompt.
        """
        # Define non-informative patterns in multiple languages
        non_informative_patterns = {
            "English": ["i don't know", "i don't know", "no", "yes", "maybe", "not sure", "unsure", "idk", "dunno", "n/a", "none", "nothing"],
            "Chinese": ["我不知道", "不知道", "不", "是", "也许", "不确定", "不清楚", "没有", "无", "不晓得"],
            "Japanese": ["わかりません", "知りません", "いいえ", "はい", "たぶん", "わからない", "不明", "なし", "無し"],
            "Spanish": ["no sé", "no lo sé", "no", "sí", "tal vez", "no estoy seguro", "no estoy segura", "ninguno", "nada"],
            "French": ["je ne sais pas", "je ne sais pas", "non", "oui", "peut-être", "pas sûr", "pas sûre", "aucun", "rien"],
            "German": ["ich weiß nicht", "weiß nicht", "nein", "ja", "vielleicht", "nicht sicher", "keiner", "nichts"],
            "Korean": ["모르겠어요", "모름", "아니요", "네", "아마", "불확실", "없음", "아무것도"]
        }
        
        # Get patterns for the specific language, default to English
        patterns = non_informative_patterns.get(language, non_informative_patterns["English"])
        patterns_str = ", ".join(patterns)
        
        return f"Question: {question}\nResponse: {response}\n\nIs this response informative enough to ask follow-up questions? Non-informative responses include: {patterns_str}. Return '1' for informative or '0' for non-informative."

    def generate_enhanced_multilingual_question(self, question: str, response: str, question_type: str, language: str) -> dict:
        """
        Generate an enhanced multilingual follow-up question with informativeness detection.

        Args:
            question (str): The original survey question (in the target language).
            response (str): The user's answer (in the target language).
            question_type (str): The type of follow-up question.
            language (str): The target language.

        Returns:
            dict: Dictionary with 'informative' flag and optional 'question' field.

        Raises:
            DeepSeekAPIError: If the API call fails.
        """
        # First, detect if the response is informative
        is_informative = self.detect_informativeness(question, response, language)
        
        if not is_informative:
            # Return response indicating non-informative response
            return {
                "informative": 0,
                "question": None
            }
        
        # If informative, generate the follow-up question
        try:
            question_text = self.generate_multilingual_question(question, response, question_type, language)
            return {
                "informative": 1,
                "question": question_text
            }
        except DeepSeekAPIError as e:
            # If question generation fails, still return informative=1 but with error
            self.logger.error(f"Failed to generate question for informative response: {e}")
            raise e 