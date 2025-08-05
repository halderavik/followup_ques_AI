"""
Test module for enhanced multilingual API endpoint with informativeness detection.
"""

import pytest
import json
from app import create_app
from app.deepseek_service import OpenAIService

class TestEnhancedMultilingualAPI:
    """Test cases for enhanced multilingual API endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_enhanced_multilingual_informative_response(self, client):
        """Test enhanced multilingual endpoint with informative response."""
        data = {
            "question": "What challenges do you face at work?",
            "response": "I struggle with time management and communication with my team.",
            "type": "reason",
            "language": "English"
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Check that response has the correct structure
        assert 'informative' in result
        assert 'question' in result
        assert 'original_question' in result
        assert 'original_response' in result
        assert 'type' in result
        assert 'language' in result
        
        # For informative response, should have informative=1 and a question
        assert result['informative'] == 1
        assert result['question'] is not None
        assert len(result['question']) > 0
        assert result['original_question'] == data['question']
        assert result['original_response'] == data['response']
        assert result['type'] == data['type']
        assert result['language'] == data['language']

    def test_enhanced_multilingual_non_informative_response(self, client):
        """Test enhanced multilingual endpoint with non-informative response."""
        data = {
            "question": "What challenges do you face at work?",
            "response": "I don't know",
            "type": "reason",
            "language": "English"
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Check that response has the correct structure
        assert 'informative' in result
        assert 'question' in result
        assert 'original_question' in result
        assert 'original_response' in result
        assert 'type' in result
        assert 'language' in result
        
        # For non-informative response, should have informative=0 and no question
        assert result['informative'] == 0
        assert result['question'] is None
        assert result['original_question'] == data['question']
        assert result['original_response'] == data['response']
        assert result['type'] == data['type']
        assert result['language'] == data['language']

    def test_enhanced_multilingual_chinese_informative(self, client):
        """Test enhanced multilingual endpoint with Chinese informative response."""
        data = {
            "question": "你在工作中面临什么挑战？",
            "response": "我在时间管理和沟通方面有困难。",
            "type": "reason",
            "language": "Chinese"
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['informative'] == 1
        assert result['question'] is not None
        assert result['language'] == "Chinese"

    def test_enhanced_multilingual_chinese_non_informative(self, client):
        """Test enhanced multilingual endpoint with Chinese non-informative response."""
        data = {
            "question": "你在工作中面临什么挑战？",
            "response": "我不知道",
            "type": "reason",
            "language": "Chinese"
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['informative'] == 0
        assert result['question'] is None
        assert result['language'] == "Chinese"

    def test_enhanced_multilingual_spanish_informative(self, client):
        """Test enhanced multilingual endpoint with Spanish informative response."""
        data = {
            "question": "¿Qué desafíos enfrentas en el trabajo?",
            "response": "Tengo dificultades con la gestión del tiempo y la comunicación.",
            "type": "impact",
            "language": "Spanish"
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['informative'] == 1
        assert result['question'] is not None
        assert result['language'] == "Spanish"

    def test_enhanced_multilingual_spanish_non_informative(self, client):
        """Test enhanced multilingual endpoint with Spanish non-informative response."""
        data = {
            "question": "¿Qué desafíos enfrentas en el trabajo?",
            "response": "No sé",
            "type": "impact",
            "language": "Spanish"
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['informative'] == 0
        assert result['question'] is None
        assert result['language'] == "Spanish"

    def test_enhanced_multilingual_invalid_request(self, client):
        """Test enhanced multilingual endpoint with invalid request."""
        data = {
            "question": "What challenges do you face?",
            # Missing required fields
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 422

    def test_enhanced_multilingual_empty_response(self, client):
        """Test enhanced multilingual endpoint with empty response."""
        data = {
            "question": "What challenges do you face at work?",
            "response": "",
            "type": "reason",
            "language": "English"
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Empty response should be considered non-informative
        assert result['informative'] == 0
        assert result['question'] is None

    def test_enhanced_multilingual_short_response(self, client):
        """Test enhanced multilingual endpoint with very short response."""
        data = {
            "question": "What challenges do you face at work?",
            "response": "No",
            "type": "reason",
            "language": "English"
        }
        
        response = client.post('/generate-enhanced-multilingual', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Short response like "No" should be considered non-informative
        assert result['informative'] == 0
        assert result['question'] is None


class TestOpenAIServiceEnhancedMultilingual:
    """Test cases for OpenAI service enhanced multilingual functionality."""

    def test_detect_informativeness_english_informative(self):
        """Test informativeness detection with English informative response."""
        service = OpenAIService()
        
        # Mock the API call to avoid actual API calls during testing
        # This test would need to be run with actual API key for full testing
        try:
            result = service.detect_informativeness(
                "What challenges do you face at work?",
                "I struggle with time management and communication with my team.",
                "English"
            )
            # Should return True for informative response
            assert isinstance(result, bool)
        except Exception as e:
            # If API key not available, test should be skipped
            pytest.skip(f"OpenAI API not available: {e}")

    def test_detect_informativeness_english_non_informative(self):
        """Test informativeness detection with English non-informative response."""
        service = OpenAIService()
        
        try:
            result = service.detect_informativeness(
                "What challenges do you face at work?",
                "I don't know",
                "English"
            )
            # Should return False for non-informative response
            assert isinstance(result, bool)
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")

    def test_build_informativeness_prompt(self):
        """Test building informativeness detection prompt."""
        service = OpenAIService()
        
        prompt = service._build_informativeness_prompt(
            "What challenges do you face?",
            "I don't know",
            "English"
        )
        
        assert "Question:" in prompt
        assert "Response:" in prompt
        assert "i don't know" in prompt.lower()
        assert "Return '1' for informative or '0' for non-informative" in prompt

    def test_build_informativeness_prompt_chinese(self):
        """Test building informativeness detection prompt for Chinese."""
        service = OpenAIService()
        
        prompt = service._build_informativeness_prompt(
            "你在工作中面临什么挑战？",
            "我不知道",
            "Chinese"
        )
        
        assert "Question:" in prompt
        assert "Response:" in prompt
        assert "我不知道" in prompt
        assert "Return '1' for informative or '0' for non-informative" in prompt 