import pytest
from app.deepseek_service import DeepSeekService, DeepSeekAPIError
import requests
from unittest.mock import patch

def test_build_prompt_basic():
    """Test prompt building with required fields only."""
    prompt = DeepSeekService.build_prompt("Q?", "A.")
    assert "Survey Question: Q?" in prompt
    assert "User Response: A." in prompt

def test_build_prompt_with_types():
    """Test prompt building with allowed types."""
    prompt = DeepSeekService.build_prompt("Q?", "A.", ["reason", "example"])
    assert "Allowed types: reason, example." in prompt

@patch('app.deepseek_service.requests.post')
@patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test'})
def test_generate_questions_success(mock_post):
    """Test successful DeepSeek API call."""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"followups": [{"type": "reason", "text": "Why?"}]}
    svc = DeepSeekService()
    resp = svc.generate_questions("prompt")
    assert "followups" in resp

@patch('app.deepseek_service.requests.post')
@patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test'})
def test_generate_questions_api_error(mock_post):
    """Test DeepSeek API error response."""
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"
    svc = DeepSeekService()
    with pytest.raises(DeepSeekAPIError):
        svc.generate_questions("prompt")

@patch('app.deepseek_service.requests.post', side_effect=requests.Timeout)
@patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test'})
def test_generate_questions_timeout(mock_post):
    """Test DeepSeek API timeout and retry logic."""
    svc = DeepSeekService()
    with pytest.raises(DeepSeekAPIError):
        svc.generate_questions("prompt")


@patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test'})
def test_parse_response_valid():
    """Test parsing a valid DeepSeek API response."""
    svc = DeepSeekService()
    api_response = {"followups": [{"type": "reason", "text": "Why?"}]}
    out = svc.parse_response(api_response)
    assert isinstance(out, list)
    assert out[0]["type"] == "reason"


@patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test'})
def test_parse_response_invalid():
    """Test parsing an invalid DeepSeek API response."""
    svc = DeepSeekService()
    with pytest.raises(DeepSeekAPIError):
        svc.parse_response({"not_followups": []}) 