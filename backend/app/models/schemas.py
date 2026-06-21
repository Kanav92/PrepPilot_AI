from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user_id: int
    email: str
    name: str

class AnswerSubmission(BaseModel):
    session_id: int
    answer_text: str

class SessionStartResponse(BaseModel):
    session_id: int
    question: dict

class NextQuestionResponse(BaseModel):
    session_id: int
    question: Optional[dict]
    interview_complete: bool
    score_summary: Optional[dict] = None
