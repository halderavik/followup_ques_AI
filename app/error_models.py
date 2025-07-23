from pydantic import BaseModel, Field
from typing import Optional

class ErrorResponse(BaseModel):
    """
    Base error response model.

    Args:
        detail (str): Description of the error.
        code (Optional[str]): Optional error code identifier.
    """
    detail: str = Field(..., description="Description of the error.")
    code: Optional[str] = Field(None, description="Optional error code identifier.")

class ValidationErrorResponse(ErrorResponse):
    """
    Validation error response model.

    Args:
        errors (Optional[list]): List of validation error details.
    """
    errors: Optional[list] = Field(None, description="List of validation error details.") 