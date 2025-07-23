import os
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel
from requests.exceptions import RequestException, Timeout
import logging

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
    TIMEOUT = 10  # seconds
    RETRIES = 2

    def __init__(self):
        """
        Initialize the DeepSeekService.
        Uses the DeepSeek API key from environment variables.
        """
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided in environment variables.")
        self.logger = logging.getLogger("DeepSeekService")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

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
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at generating intelligent follow-up questions for survey responses. Generate 2-3 relevant follow-up questions based on the user's response. Return your response as a JSON object with a 'followups' array containing objects with 'type' and 'text' fields. The 'type' should be one of: reason, clarification, elaboration, example, impact, comparison."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        last_exc = None
        for attempt in range(self.RETRIES + 1):
            try:
                response = requests.post(
                    self.API_URL,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=self.TIMEOUT
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.error(f"DeepSeek API error: {response.status_code} {response.text}")
                    raise DeepSeekAPIError(f"API error: {response.status_code} {response.text}")
            except (RequestException, Timeout) as exc:
                self.logger.warning(f"DeepSeek API request failed (attempt {attempt+1}): {exc}")
                last_exc = exc
        raise DeepSeekAPIError(f"Failed after {self.RETRIES+1} attempts: {last_exc}")

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
        # Reason: Prompt template is simple for MVP, can be extended for more control.
        types_str = f"Allowed types: {', '.join(allowed_types)}." if allowed_types else ""
        return (
            f"Survey Question: {question}\n"
            f"User Response: {response}\n"
            f"{types_str}\n"
            "Generate 2-3 relevant follow-up questions using the allowed types."
        ) 