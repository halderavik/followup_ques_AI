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
import concurrent.futures

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
    TIMEOUT = 15  # Reduced timeout for faster response
    RETRIES = 1   # Keep retries for reliability
    MAX_TOKENS = 150  # Optimized for faster generation

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
        
        # Configure retry strategy for reliability with faster backoff
        retry_strategy = Retry(
            total=self.RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            backoff_factor=0.1  # Faster backoff for speed
        )
        
        # Configure adapter with optimized connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,  # Optimized for typical load
            pool_maxsize=50,      # Optimized for typical load
            pool_block=False      # Don't block on connection pool exhaustion
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Pre-warm connection pool for faster initial requests
        try:
            self.session.get("https://api.deepseek.com", timeout=1)
        except:
            pass  # Ignore pre-warm failures
        
        # Optimized in-memory cache for performance
        self.cache = {}
        self.cache_ttl = 600  # 10 minutes for better caching
        self.cache_max_size = 1000  # Larger cache for better hit rates

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
        """Cache the response with timestamp and size management."""
        # Clean up cache if it's getting too large
        if len(self.cache) >= self.cache_max_size:
            self.cleanup_cache()
        
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
                    "content": "Generate follow-up questions based on the user's request. Return ONLY valid JSON: {\"followups\": [{\"type\": \"reason|clarification|elaboration|example|impact|comparison\", \"text\": \"question\"}]}"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.05,  # Even lower temperature for fastest responses
            "max_tokens": self.MAX_TOKENS,
            "top_p": 0.5,        # Lower for faster generation
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

    def parse_response(self, api_response: dict, allowed_types: Optional[list] = None) -> list:
        """
        Parse the DeepSeek API response to extract follow-up questions.

        Args:
            api_response (dict): The raw API response from DeepSeek.
            allowed_types (Optional[list]): List of allowed question types to determine expected count.

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
            
            # Determine expected count based on allowed_types
            if allowed_types:
                expected_count = len(allowed_types)
            else:
                expected_count = 6  # Default to all 6 types
            
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
                        
                        # Ensure we have exactly the expected number of questions with the required types
                        return self._ensure_questions(questions, expected_count, allowed_types)
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
                            
                            # Ensure we have exactly the expected number of questions with the required types
                            return self._ensure_questions(questions, expected_count, allowed_types)
                    except json.JSONDecodeError:
                        pass
                
                # If JSON parsing fails, try to extract questions from plain text
                self.logger.warning("JSON parsing failed, attempting to extract questions from plain text")
                questions = self._extract_questions_from_text(content)
                if questions:
                    return self._ensure_questions(questions, expected_count, allowed_types)
                
                raise DeepSeekAPIError("Could not extract questions from response content.")
                
            except Exception as exc:
                self.logger.error(f"Failed to parse DeepSeek response: {exc}")
                raise DeepSeekAPIError(f"Failed to parse DeepSeek response: {exc}")
                
        except Exception as exc:
            self.logger.error(f"Failed to parse DeepSeek response: {exc}")
            raise DeepSeekAPIError(f"Failed to parse DeepSeek response: {exc}")

    def _ensure_questions(self, questions: list, expected_count: int = 6, allowed_types: Optional[list] = None) -> list:
        """
        Ensure exactly the expected number of questions with the required types.
        
        Args:
            questions (list): List of question dictionaries.
            expected_count (int): Expected number of questions (default 6 for all types).
            allowed_types (Optional[list]): List of allowed question types to determine the order.
            
        Returns:
            list: Exactly expected_count questions with the required types.
        """
        self.logger.info(f"Ensuring {expected_count} questions from {len(questions)} input questions")
        
        # Determine the required types based on allowed_types or default to all 6
        if allowed_types:
            required_types = allowed_types
        else:
            all_types = ['reason', 'clarification', 'elaboration', 'example', 'impact', 'comparison']
            required_types = all_types[:expected_count]
        
        result = []
        
        # Type mapping for similar types
        type_mapping = {
            'why': 'reason',
            'clarify': 'clarification',
            'explain': 'clarification',
            'elaborate': 'elaboration',
            'details': 'elaboration',
            'examples': 'example',
            'instance': 'example',
            'case': 'example',
            'effects': 'impact',
            'consequences': 'impact',
            'results': 'impact',
            'outcomes': 'impact',
            'compare': 'comparison',
            'versus': 'comparison',
            'difference': 'comparison'
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
                default_texts = {
                    'reason': f"Why do you think this is the case?",
                    'clarification': f"Can you clarify what you mean by this?",
                    'elaboration': f"Can you provide more details about this?",
                    'example': f"Can you give an example of this?",
                    'impact': f"How does this affect you or others?",
                    'comparison': f"How does this compare to other options?"
                }
                result.append({
                    'type': req_type,
                    'text': default_texts.get(req_type, f"Please provide more details about {req_type}.")
                })
                self.logger.info(f"Created default question for {req_type}")
        
        # Ensure we have exactly the expected number of questions
        final_result = result[:expected_count]
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
        # If allowed_types is provided, use those; otherwise use all 6 types
        if allowed_types:
            types_to_generate = allowed_types
        else:
            types_to_generate = ['reason', 'clarification', 'elaboration', 'example', 'impact', 'comparison']
        
        # Build the prompt with the specified types - optimized for speed
        type_mapping = {
            'reason': 'ask why',
            'clarification': 'ask for clarification', 
            'elaboration': 'ask for more details',
            'example': 'ask for examples',
            'impact': 'ask about effects',
            'comparison': 'ask for comparison'
        }
        
        types_text = ", ".join([f"'{t}' ({type_mapping.get(t, t)})" for t in types_to_generate])
        return f"Q: {question} A: {response}. Generate {len(types_to_generate)} questions: {types_text}. Return JSON: {{\"followups\": [{{\"type\": \"type\", \"text\": \"question\"}}]}}"

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
            "temperature": 0.05,  # Very low temperature for fastest responses
            "max_tokens": 50,     # Further reduced for faster generation
            "top_p": 0.7,        # Lower for faster generation
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
            "temperature": 0.0,  # Zero temperature for fastest, most consistent classification
            "max_tokens": 5,     # Minimal tokens needed for 1/0 response
            "top_p": 0.8,
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

    def detect_themes_in_response(self, response: str, themes: list) -> Optional[dict]:
        """
        Detect which themes from the provided list are present in the response.

        Args:
            response (str): The user's response to analyze.
            themes (list): List of theme dictionaries with 'name' and 'importance' keys.

        Returns:
            Optional[dict]: Dictionary with detected theme info or None if no themes found.
        """
        cache_key = self._get_cache_key(f"theme_detection:{response}:{str(themes)}")
        cached_result = self._get_cached_response(cache_key)
        if cached_result:
            return cached_result

        try:
            prompt = self._build_theme_detection_prompt(response, themes)
            
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
                "temperature": 0.0,  # Zero temperature for fastest, most consistent theme detection
                "max_tokens": 30,    # Reduced for faster JSON response
                "top_p": 0.8,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stream": False
            }

            response_data = self.session.post(
                self.API_URL,
                headers=self._get_headers(),
                json=payload,
                timeout=self.TIMEOUT
            )
            response_data.raise_for_status()
            
            result = response_data.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Parse the JSON response
            import json
            import re
            
            # Clean the content - remove any extra text before or after JSON
            content_clean = content.strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content_clean)
            if json_match:
                content_clean = json_match.group(0)
            
            try:
                theme_result = json.loads(content_clean)
                if theme_result.get("theme_name") == "none":
                    result_data = None
                else:
                    result_data = {
                        "theme_name": theme_result.get("theme_name"),
                        "importance": theme_result.get("importance")
                    }
            except json.JSONDecodeError:
                self.logger.warning(f"Failed to parse theme detection response as JSON: {content}")
                # Fallback: try simple string matching
                result_data = None
                for theme in themes:
                    if theme["name"].lower() in response.lower():
                        result_data = {
                            "theme_name": theme["name"],
                            "importance": theme["importance"]
                        }
                        break
            
            self._cache_response(cache_key, result_data)
            return result_data
            
        except Exception as e:
            self.logger.error(f"Theme detection failed: {e}")
            return None

    @staticmethod
    def _build_theme_detection_prompt(response: str, themes: list) -> str:
        """
        Build prompt for theme detection.

        Args:
            response (str): The user's response to analyze.
            themes (list): List of theme dictionaries.

        Returns:
            str: The formatted prompt for theme detection.
        """
        themes_str = ", ".join([f"'{t['name']}' (importance: {t['importance']}%)" for t in themes])
        
        return f"""Analyze this response for theme matches:

Response: "{response}"

Available themes: {themes_str}

Look for exact matches or synonyms of the theme names in the response.

Return ONLY a JSON object like this:
{{"theme_name": "theme_name", "importance": importance_number}}

If no themes are found, return:
{{"theme_name": "none", "importance": 0}}

Examples:
- If response contains "communication" and themes include "communication", return {{"theme_name": "communication", "importance": 60}}
- If response contains "leadership" and themes include "leadership", return {{"theme_name": "leadership", "importance": 80}}
- If no themes match, return {{"theme_name": "none", "importance": 0}}

Choose the theme with the highest importance if multiple themes are found."""

    def generate_theme_enhanced_question(self, question: str, response: str, question_type: str, language: str, 
                                       theme: str, theme_parameters: Optional[dict] = None) -> dict:
        """
        Generate a theme-enhanced multilingual follow-up question with optimized performance.

        Args:
            question (str): The original survey question.
            response (str): The user's response to the question.
            question_type (str): The type of follow-up question to generate.
            language (str): The target language for the response.
            theme (str): "Yes" to enable theme analysis, "No" for standard workflow.
            theme_parameters (Optional[dict]): Theme parameters when theme="Yes".

        Returns:
            dict: Dictionary containing response data with theme information.

        Raises:
            DeepSeekAPIError: If there's an error calling the DeepSeek API.
        """
        # If theme is "No", use standard workflow (fast path)
        if theme.lower() == "no":
            try:
                question_text = self.generate_multilingual_question(question, response, question_type, language)
                return {
                    "informative": 1,
                    "question": question_text,
                    "theme": theme,
                    "detected_theme": None,
                    "theme_importance": None,
                    "highest_importance_theme": None
                }
            except DeepSeekAPIError as e:
                self.logger.error(f"Failed to generate standard question: {e}")
                raise e

        # Theme analysis workflow
        if not theme_parameters or not theme_parameters.get("themes"):
            raise ValueError("Theme parameters required when theme='Yes'")

        themes = [{"name": t["name"], "importance": t["importance"]} for t in theme_parameters["themes"]]
        
        # OPTIMIZATION: Run informativeness detection and theme detection in parallel
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks simultaneously
            informativeness_future = executor.submit(self.detect_informativeness, question, response, language)
            theme_detection_future = executor.submit(self.detect_themes_in_response, response, themes)
            
            # Wait for both results
            is_informative = informativeness_future.result()
            detected_theme = theme_detection_future.result()
        
        # Log performance improvement
        elapsed_time = time.time() - start_time
        self.logger.info(f"Parallel processing completed in {elapsed_time:.2f}s")
        
        # OPTIMIZATION: Early return for non-informative responses
        if not is_informative:
            return {
                "informative": 0, 
                "question": None,
                "theme": theme,
                "detected_theme": None,
                "theme_importance": None,
                "highest_importance_theme": None
            }
        
        if detected_theme:
            # Theme found - generate question based on detected theme and type
            try:
                result = self._generate_theme_based_question(
                    question, response, question_type, language, 
                    detected_theme["theme_name"], detected_theme["importance"]
                )
                return {
                    "informative": 1,
                    "question": result["question"],
                    "explanation": result["explanation"],
                    "theme": theme,
                    "detected_theme": detected_theme["theme_name"],
                    "theme_importance": detected_theme["importance"],
                    "highest_importance_theme": None
                }
            except DeepSeekAPIError as e:
                self.logger.error(f"Failed to generate theme-based question: {e}")
                raise e
        else:
            # No themes found - ask about why important themes weren't mentioned
            try:
                # Find highest importance theme
                highest_theme = max(themes, key=lambda x: x["importance"])
                
                result = self._generate_missing_theme_question(
                    question, response, language, highest_theme["name"], highest_theme["importance"]
                )
                return {
                    "informative": 1,
                    "question": result["question"],
                    "explanation": result["explanation"],
                    "theme": theme,
                    "detected_theme": None,
                    "theme_importance": None,
                    "highest_importance_theme": highest_theme["name"]
                }
            except DeepSeekAPIError as e:
                self.logger.error(f"Failed to generate missing theme question: {e}")
                raise e

    def _generate_theme_based_question(self, question: str, response: str, question_type: str, 
                                     language: str, theme_name: str, theme_importance: int) -> dict:
        """
        Generate a question based on detected theme and question type.

        Args:
            question (str): The original survey question.
            response (str): The user's response.
            question_type (str): The type of follow-up question.
            language (str): The target language.
            theme_name (str): The detected theme name.
            theme_importance (int): The importance percentage of the theme.

        Returns:
            dict: Dictionary containing question and explanation.
        """
        cache_key = self._get_cache_key(f"theme_question:{question}:{response}:{question_type}:{language}:{theme_name}")
        cached_result = self._get_cached_response(cache_key)
        if cached_result:
            return cached_result

        prompt = self._build_theme_question_prompt(question, response, question_type, language, theme_name, theme_importance)
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": f"Generate a follow-up question in {language} that focuses on the detected theme '{theme_name}' and follows the specified question type. Return the question and explanation separately."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False
        }

        response_data = self.session.post(
            self.API_URL,
            headers=self._get_headers(),
            json=payload,
            timeout=self.TIMEOUT
        )
        response_data.raise_for_status()
        
        result = response_data.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        # Parse question and explanation
        question_text, explanation = self._parse_question_and_explanation(content)
        
        # Clean the question text
        question_text = self._clean_question_text(question_text)
        
        result_data = {"question": question_text, "explanation": explanation}
        self._cache_response(cache_key, result_data)
        return result_data

    def _generate_missing_theme_question(self, question: str, response: str, language: str, 
                                       theme_name: str, theme_importance: int) -> dict:
        """
        Generate a question asking why important themes weren't mentioned.

        Args:
            question (str): The original survey question.
            response (str): The user's response.
            language (str): The target language.
            theme_name (str): The highest importance theme.
            theme_importance (int): The importance percentage.

        Returns:
            dict: Dictionary containing question and explanation.
        """
        cache_key = self._get_cache_key(f"missing_theme:{question}:{response}:{language}:{theme_name}")
        cached_result = self._get_cached_response(cache_key)
        if cached_result:
            return cached_result

        prompt = f"""Original Question: {question}
User Response: {response}

The user didn't mention '{theme_name}' (importance: {theme_importance}%) in their response.

Generate a follow-up question in {language} asking why they didn't mention this important theme or what they think about it.

Return in this format:
Question: [Your question here]

Explanation: [Explain how this question addresses the missing theme]"""

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": f"Generate a follow-up question in {language} about missing important themes."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False
        }

        response_data = self.session.post(
            self.API_URL,
            headers=self._get_headers(),
            json=payload,
            timeout=self.TIMEOUT
        )
        response_data.raise_for_status()
        
        result = response_data.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        # Parse question and explanation
        question_text, explanation = self._parse_question_and_explanation(content)
        
        # Clean the question text
        question_text = self._clean_question_text(question_text)
        
        result_data = {"question": question_text, "explanation": explanation}
        self._cache_response(cache_key, result_data)
        return result_data

    @staticmethod
    def _build_theme_question_prompt(question: str, response: str, question_type: str, 
                                   language: str, theme_name: str, theme_importance: int) -> str:
        """
        Build prompt for theme-based question generation.

        Args:
            question (str): The original survey question.
            response (str): The user's response.
            question_type (str): The type of follow-up question.
            language (str): The target language.
            theme_name (str): The detected theme name.
            theme_importance (int): The importance percentage.

        Returns:
            str: The formatted prompt for theme-based question generation.
        """
        type_descriptions = {
            "reason": "ask for the reason or cause",
            "impact": "ask about the impact or consequences",
            "elaboration": "ask for more details or examples",
            "clarification": "ask for clarification",
            "comparison": "ask for comparison"
        }
        
        type_desc = type_descriptions.get(question_type.lower(), "ask a relevant follow-up")
        
        return f"""Original Question: {question}
User Response: {response}

Detected Theme: {theme_name} (importance: {theme_importance}%)

Generate a follow-up question in {language} that:
1. Focuses specifically on the theme '{theme_name}'
2. Uses the question type '{question_type}' ({type_desc})
3. Is relevant to the user's response

Return in this format:
Question: [Your question here]

Explanation: [Explain how this question focuses on the theme and question type]"""

    def _parse_question_and_explanation(self, content: str) -> tuple:
        """
        Parse question and explanation from AI response.

        Args:
            content (str): The AI response content.

        Returns:
            tuple: (question_text, explanation)
        """
        lines = content.split('\n')
        question_text = ""
        explanation = ""
        in_question = False
        in_explanation = False
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('question:'):
                in_question = True
                in_explanation = False
                question_text = line[9:].strip()  # Remove "Question: "
            elif line.lower().startswith('explanation:'):
                in_question = False
                in_explanation = True
                explanation = line[12:].strip()  # Remove "Explanation: "
            elif in_question and line:
                question_text += " " + line
            elif in_explanation and line:
                explanation += " " + line
        
        # Clean up
        question_text = question_text.strip()
        explanation = explanation.strip()
        
        # Fallback if parsing fails
        if not question_text:
            question_text = content.strip()
        if not explanation:
            explanation = "Generated follow-up question based on theme and question type."
        
        return question_text, explanation 