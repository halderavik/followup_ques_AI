import pytest
from app import create_app
from app.question_types import QuestionType
import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEEPSEEK_API_KEY'] = 'test-key'
    with app.test_client() as client:
        yield client

def test_health(client):
    """Test /health endpoint returns ok."""
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ok'

def test_question_types(client):
    """Test /question-types endpoint returns all types."""
    resp = client.get('/question-types')
    assert resp.status_code == 200
    types = resp.get_json()['question_types']
    assert set(types) == set([qt.value for qt in QuestionType])

def test_generate_followup_no_auth_required(client):
    """Test /generate-followup works without API key (no auth required)."""
    payload = {
        "question": "What did you like?",
        "response": "The service was fast."
    }
    resp = client.post('/generate-followup', json=payload)
    # Should not return 401 - no auth required
    assert resp.status_code != 401


def test_generate_followup_validation_error(client):
    """Test /generate-followup returns 422 for invalid input."""
    resp = client.post('/generate-followup', json={})
    assert resp.status_code == 422
    data = resp.get_json()
    assert data['code'] == 'validation_error'


def test_generate_followup_success(client, monkeypatch):
    """Test /generate-followup returns followups on valid input and mocks DeepSeekService."""
    # Patch DeepSeekService methods
    from app.deepseek_service import DeepSeekService
    monkeypatch.setattr(DeepSeekService, 'generate_questions', lambda self, prompt: {"followups": [{"type": "reason", "text": "Why?"}]} )
    monkeypatch.setattr(DeepSeekService, 'parse_response', lambda self, resp: resp["followups"])
    payload = {
        "question": "What did you like?",
        "response": "The service was fast.",
        "allowed_types": ["reason"]
    }
    resp = client.post('/generate-followup', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'followups' in data
    assert data['followups'][0]['type'] == 'reason' 