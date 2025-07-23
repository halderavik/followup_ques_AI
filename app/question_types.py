from enum import Enum

class QuestionType(str, Enum):
    """
    Enum for supported follow-up question types.
    """
    REASON = "reason"           # Why did you choose this answer?
    CLARIFICATION = "clarification" # Can you explain what you mean by...?
    ELABORATION = "elaboration"     # Can you provide more details about...?
    EXAMPLE = "example"             # Can you give an example of...?
    IMPACT = "impact"               # How does this affect...?
    COMPARISON = "comparison"       # How does this compare to...? 