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

class ThemeParameter(BaseModel):
    """
    Model for a theme with its importance percentage.

    Args:
        name (str): The name of the theme.
        importance (int): The importance percentage (0-100).
    """
    name: str = Field(..., description="The name of the theme.")
    importance: int = Field(..., ge=0, le=100, description="The importance percentage (0-100).")

class ThemeParameters(BaseModel):
    """
    Model for theme parameters containing a list of themes.

    Args:
        themes (List[ThemeParameter]): List of themes with their importance percentages (1-10 themes allowed).
    """
    themes: List[ThemeParameter] = Field(..., min_items=1, max_items=10, description="List of themes with their importance percentages (1-10 themes allowed).")

class ThemeEnhancedRequest(BaseModel):
    """
    Request model for theme-enhanced multilingual follow-up question generation.

    Args:
        question (str): The original survey question (in the target language).
        response (str): The user's answer to the survey question (in the target language).
        type (str): The type of follow-up question (reason, impact, elaboration, etc.).
        language (str): The target language for the response.
        theme (str): "Yes" to enable theme analysis, "No" for standard workflow.
        theme_parameters (Optional[ThemeParameters]): Theme parameters (required when theme="Yes").
    """
    question: str = Field(..., description="The original survey question (in the target language).")
    response: str = Field(..., description="The user's answer to the survey question (in the target language).")
    type: str = Field(..., description="The type of follow-up question.")
    language: str = Field(..., description="The target language for the response.")
    theme: str = Field(..., description="'Yes' to enable theme analysis, 'No' for standard workflow.")
    theme_parameters: Optional[ThemeParameters] = Field(None, description="Theme parameters (required when theme='Yes').")

class ThemeEnhancedResponse(BaseModel):
    """
    Response model for theme-enhanced multilingual follow-up question.

    Args:
        informative (int): 1 if response is informative, 0 if non-informative.
        question (Optional[str]): The generated follow-up question (only if informative=1).
        explanation (Optional[str]): Explanation of how the question was generated (only if informative=1).
        original_question (str): The original survey question.
        original_response (str): The original user response.
        type (str): The type of follow-up question requested.
        language (str): The language of the generated question.
        theme (str): The theme setting used ("Yes" or "No").
        detected_theme (Optional[str]): The theme detected in the response (if any).
        theme_importance (Optional[int]): The importance percentage of detected theme.
        highest_importance_theme (Optional[str]): The highest importance theme (when no themes found).
    """
    informative: int = Field(..., description="1 if response is informative, 0 if non-informative.")
    question: Optional[str] = Field(None, description="The generated follow-up question (only if informative=1).")
    explanation: Optional[str] = Field(None, description="Explanation of how the question was generated (only if informative=1).")
    original_question: str = Field(..., description="The original survey question.")
    original_response: str = Field(..., description="The original user response.")
    type: str = Field(..., description="The type of follow-up question requested.")
    language: str = Field(..., description="The language of the generated question.")
    theme: str = Field(..., description="The theme setting used ('Yes' or 'No').")
    detected_theme: Optional[str] = Field(None, description="The theme detected in the response (if any).")
    theme_importance: Optional[int] = Field(None, description="The importance percentage of detected theme.")
    highest_importance_theme: Optional[str] = Field(None, description="The highest importance theme (when no themes found).") 