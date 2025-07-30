from pydantic import BaseModel, Field
from typing import List, Optional
from .question_types import QuestionType

class GenerateFollowupRequest(BaseModel):
    """
    Request model for generating follow-up questions.

    Args:
        question (str): The original survey question.
        response (str): The user's answer to the survey question.
        allowed_types (Optional[List[QuestionType]]): Optional list of allowed follow-up question types.
    """
    question: str = Field(..., description="The original survey question.")
    response: str = Field(..., description="The user's answer to the survey question.")
    allowed_types: Optional[List[QuestionType]] = Field(None, description="Optional list of allowed follow-up question types.")

class FollowupQuestion(BaseModel):
    """
    Model for a generated follow-up question.

    Args:
        type (QuestionType): The type of follow-up question.
        text (str): The follow-up question text.
    """
    type: QuestionType
    text: str

class GenerateFollowupResponse(BaseModel):
    """
    Response model for generated follow-up questions.

    Args:
        followups (List[FollowupQuestion]): List of generated follow-up questions.
    """
    followups: List[FollowupQuestion]

class SingleReasonRequest(BaseModel):
    """
    Request model for generating a single reason-based follow-up question.

    Args:
        question (str): The original survey question.
        response (str): The user's answer to the survey question.
    """
    question: str = Field(..., description="The original survey question.")
    response: str = Field(..., description="The user's answer to the survey question.")

class SingleReasonResponse(BaseModel):
    """
    Response model for a single reason-based follow-up question.

    Args:
        question (str): The generated reason-based follow-up question.
        original_question (str): The original survey question.
        original_response (str): The original user response.
    """
    question: str = Field(..., description="The generated reason-based follow-up question.")
    original_question: str = Field(..., description="The original survey question.")
    original_response: str = Field(..., description="The original user response.")

class MultilingualQuestionRequest(BaseModel):
    """
    Request model for generating a single multilingual follow-up question.

    Args:
        question (str): The original survey question (in the target language).
        response (str): The user's answer to the survey question (in the target language).
        type (str): The type of follow-up question (reason, impact, elaboration, etc.).
        language (str): The target language for the response (e.g., "Chinese", "Japanese", "Spanish").
    """
    question: str = Field(..., description="The original survey question (in the target language).")
    response: str = Field(..., description="The user's answer to the survey question (in the target language).")
    type: str = Field(..., description="The type of follow-up question.")
    language: str = Field(..., description="The target language for the response.")

class MultilingualQuestionResponse(BaseModel):
    """
    Response model for a single multilingual follow-up question.

    Args:
        question (str): The generated follow-up question in the target language.
        original_question (str): The original survey question.
        original_response (str): The original user response.
        type (str): The type of follow-up question generated.
        language (str): The language of the generated question.
    """
    question: str = Field(..., description="The generated follow-up question in the target language.")
    original_question: str = Field(..., description="The original survey question.")
    original_response: str = Field(..., description="The original user response.")
    type: str = Field(..., description="The type of follow-up question generated.")
    language: str = Field(..., description="The language of the generated question.")

class EnhancedMultilingualRequest(BaseModel):
    """
    Request model for enhanced multilingual follow-up question generation with informativeness detection.

    Args:
        question (str): The original survey question (in the target language).
        response (str): The user's answer to the survey question (in the target language).
        type (str): The type of follow-up question (reason, impact, elaboration, etc.).
        language (str): The target language for the response (e.g., "Chinese", "Japanese", "Spanish").
    """
    question: str = Field(..., description="The original survey question (in the target language).")
    response: str = Field(..., description="The user's answer to the survey question (in the target language).")
    type: str = Field(..., description="The type of follow-up question.")
    language: str = Field(..., description="The target language for the response.")

class EnhancedMultilingualResponse(BaseModel):
    """
    Response model for enhanced multilingual follow-up question with informativeness detection.

    Args:
        informative (int): 1 if response is informative, 0 if non-informative.
        question (Optional[str]): The generated follow-up question (only if informative=1).
        original_question (str): The original survey question.
        original_response (str): The original user response.
        type (str): The type of follow-up question requested.
        language (str): The language of the generated question.
    """
    informative: int = Field(..., description="1 if response is informative, 0 if non-informative.")
    question: Optional[str] = Field(None, description="The generated follow-up question (only if informative=1).")
    original_question: str = Field(..., description="The original survey question.")
    original_response: str = Field(..., description="The original user response.")
    type: str = Field(..., description="The type of follow-up question requested.")
    language: str = Field(..., description="The language of the generated question.") 