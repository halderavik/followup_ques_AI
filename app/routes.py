from flask import Blueprint, request, jsonify, current_app, send_from_directory
from pydantic import ValidationError
from .models import GenerateFollowupRequest, GenerateFollowupResponse, FollowupQuestion, SingleReasonRequest, SingleReasonResponse, MultilingualQuestionRequest, MultilingualQuestionResponse
from .question_types import QuestionType
from .error_models import ErrorResponse, ValidationErrorResponse
from .deepseek_service import DeepSeekService, DeepSeekAPIError
# Authentication removed - no import needed

bp = Blueprint('api', __name__)

# Root route to serve the frontend
@bp.route('/', methods=['GET'])
def serve_frontend():
    """
    Serve the performance monitoring frontend.
    """
    return send_from_directory('../static', 'index.html')

@bp.route('/api-info', methods=['GET'])
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
            "generate_followup": "/generate-followup",
            "generate_reason": "/generate-reason",
            "generate_multilingual": "/generate-multilingual",
            "performance": "/performance"
        },
        "usage": {
            "health": "GET /health - Check API status",
            "question_types": "GET /question-types - Get available question types",
            "generate_followup": "POST /generate-followup - Generate follow-up questions",
            "generate_reason": "POST /generate-reason - Generate single reason-based question",
            "generate_multilingual": "POST /generate-multilingual - Generate single multilingual question",
            "performance": "GET /performance - Get performance metrics"
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

@bp.route('/performance', methods=['GET'])
def performance():
    """
    Get API performance metrics.

    Returns:
        JSON: Performance metrics and cache statistics.
    """
    try:
        from .deepseek_service import DeepSeekService
        service = DeepSeekService()
        
        # Clean up cache
        service.cleanup_cache()
        
        return jsonify({
            "cache_size": len(service.cache),
            "cache_ttl": service.cache_ttl,
            "timeout": service.TIMEOUT,
            "max_tokens": service.MAX_TOKENS,
            "retries": service.RETRIES
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to get performance metrics",
            "details": str(e)
        }), 500

@bp.route('/generate-reason', methods=['POST'])
def generate_reason():
    """
    Generate a single reason-based follow-up question for a survey response.

    Returns:
        JSON: Generated reason-based follow-up question or error.
    """
    try:
        data = request.get_json()
        req = SingleReasonRequest(**data)
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
    # Force question type to be REASON only
    prompt = service.build_prompt(req.question, req.response, ["REASON"])
    try:
        api_response = service.generate_questions(prompt)
        followups = service.parse_response(api_response)
        
        # Take only the first question (should be REASON type)
        if followups and len(followups) > 0:
            first_question = followups[0]["text"]
            response = SingleReasonResponse(
                question=first_question,
                original_question=req.question,
                original_response=req.response
            )
            return jsonify(response.dict()), 200
        else:
            return jsonify(ErrorResponse(
                detail="No follow-up question generated",
                code="no_question_generated"
            ).dict()), 500
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

@bp.route('/generate-multilingual', methods=['POST'])
def generate_multilingual():
    """
    Generate a single multilingual follow-up question for a survey response.

    Returns:
        JSON: Generated multilingual follow-up question or error.
    """
    try:
        data = request.get_json()
        req = MultilingualQuestionRequest(**data)
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
    try:
        # Generate multilingual question using the new optimized method
        question_text = service.generate_multilingual_question(
            req.question, 
            req.response, 
            req.type, 
            req.language
        )
        
        response = MultilingualQuestionResponse(
            question=question_text,
            original_question=req.question,
            original_response=req.response,
            type=req.type,
            language=req.language
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