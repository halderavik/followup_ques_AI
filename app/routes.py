from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from .models import GenerateFollowupRequest, GenerateFollowupResponse, FollowupQuestion
from .question_types import QuestionType
from .error_models import ErrorResponse, ValidationErrorResponse
from .deepseek_service import DeepSeekService, DeepSeekAPIError
# Authentication removed - no import needed

bp = Blueprint('api', __name__)

@bp.route('/', methods=['GET'])
def root():
    """
    Root endpoint with API information.

    Returns:
        JSON: API information and available endpoints.
    """
    return jsonify({
        "name": "Survey Intelligence API",
        "description": "Generate intelligent follow-up questions for survey responses using DeepSeek AI",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "question_types": "/question-types",
            "generate_followup": "/generate-followup"
        },
        "usage": {
            "health": "GET /health - Check API status",
            "question_types": "GET /question-types - Get available question types",
            "generate_followup": "POST /generate-followup - Generate follow-up questions"
        }
    }), 200

@bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Returns:
        JSON: Status message.
    """
    return jsonify({"status": "ok"}), 200

@bp.route('/question-types', methods=['GET'])
def question_types():
    """
    List supported follow-up question types.

    Returns:
        JSON: List of question types.
    """
    return jsonify({"question_types": [qt.value for qt in QuestionType]}), 200

@bp.route('/generate-followup', methods=['POST'])
def generate_followup():
    """
    Generate follow-up questions for a survey response.

    Returns:
        JSON: Generated follow-up questions or error.
    """
    try:
        data = request.get_json()
        req = GenerateFollowupRequest(**data)
    except ValidationError as ve:
        return jsonify(ValidationErrorResponse(
            detail="Invalid request data.",
            code="validation_error",
            errors=ve.errors()
        ).dict()), 422
    except Exception as exc:
        return jsonify(ErrorResponse(
            detail=f"Malformed request: {exc}",
            code="bad_request"
        ).dict()), 400

    service = DeepSeekService()
    prompt = service.build_prompt(req.question, req.response, [t.value for t in req.allowed_types] if req.allowed_types else None)
    try:
        api_response = service.generate_questions(prompt)
        followups = service.parse_response(api_response)
        response = GenerateFollowupResponse(
            followups=[FollowupQuestion(type=QuestionType(f["type"]), text=f["text"]) for f in followups]
        )
        return jsonify(response.dict()), 200
    except DeepSeekAPIError as dse:
        return jsonify(ErrorResponse(
            detail=str(dse),
            code="deepseek_error"
        ).dict()), 502
    except Exception as exc:
        return jsonify(ErrorResponse(
            detail=f"Internal server error: {exc}",
            code="internal_error"
        ).dict()), 500 