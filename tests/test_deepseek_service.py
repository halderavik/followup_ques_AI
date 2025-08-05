import pytest
from app.deepseek_service import OpenAIService, OpenAIAPIError
import requests
from unittest.mock import patch

def test_build_prompt_basic():
    """Test prompt building with required fields only."""
    prompt = OpenAIService.build_prompt("Q?", "A.")
    assert "Q: Q?" in prompt
    assert "A: A." in prompt

def test_build_prompt_with_types():
    """Test prompt building with allowed types."""
    prompt = OpenAIService.build_prompt("Q?", "A.", ["reason", "example"])
    assert "reason" in prompt
    assert "example" in prompt

@patch('app.deepseek_service.requests.post')
@patch.dict('os.environ', {'OPENAI_API_KEY': 'test'})
def test_generate_questions_success(mock_post):
    """Test successful OpenAI API call."""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": '{"followups": [{"type": "reason", "text": "Why?"}]}'}}]
    }
    svc = OpenAIService()
    resp = svc.generate_questions("prompt")
    assert "choices" in resp

@patch('app.deepseek_service.requests.post')
@patch.dict('os.environ', {'OPENAI_API_KEY': 'test'})
def test_generate_questions_api_error(mock_post):
    """Test OpenAI API error response."""
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"
    svc = OpenAIService()
    with pytest.raises(OpenAIAPIError):
        svc.generate_questions("prompt")

@patch('app.deepseek_service.requests.post', side_effect=requests.Timeout)
@patch.dict('os.environ', {'OPENAI_API_KEY': 'test'})
def test_generate_questions_timeout(mock_post):
    """Test OpenAI API timeout and retry logic."""
    svc = OpenAIService()
    with pytest.raises(OpenAIAPIError):
        svc.generate_questions("prompt")


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test'})
def test_parse_response_valid():
    """Test parsing a valid OpenAI API response."""
    svc = OpenAIService()
    api_response = {
        "choices": [{"message": {"content": '{"followups": [{"type": "reason", "text": "Why?"}]}'}}]
    }
    out = svc.parse_response(api_response)
    assert isinstance(out, list)
    assert out[0]["type"] == "reason"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test'})
def test_parse_response_invalid():
    """Test parsing an invalid OpenAI API response."""
    svc = OpenAIService()
    with pytest.raises(OpenAIAPIError):
        svc.parse_response({"not_choices": []}) 