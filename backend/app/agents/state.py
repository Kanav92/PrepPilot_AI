from typing import TypedDict, Annotated
import operator

class InterviewState(TypedDict):
    user_id: int
    session_id: int
    resume_id: int
    resume_data: dict
    questions: Annotated[list, operator.add]
    current_question_idx: int
    current_question: dict
    difficulty_level: str
    answers: Annotated[list, operator.add]
    scores: Annotated[list, operator.add]
    topic_breakdown: dict
    focus_recommendations: list
    interview_complete: bool
    messages: Annotated[list, operator.add]
    tool_types_used: Annotated[list, operator.add]
    current_answer: str
