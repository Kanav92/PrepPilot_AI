import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE,
});

// Attach JWT token to every request automatically, if present
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export default api;

// ---- Types matching backend responses ----

export interface Question {
  id?: number;
  question_text: string;
  topic: string;
  difficulty: string;
  expected_concepts?: string[];
}

export interface ScoreResult {
  topic: string;
  score: number;
  missing_concepts: string[];
  feedback: string;
}

export interface AuthResponse {
  access_token: string;
  user_id: number;
  email: string;
  name: string;
}

export interface StartInterviewResponse {
  session_id: number;
  question: Question;
  question_number: number;
  total_questions: number;
}

export interface AnswerResponse {
  interview_complete: boolean;
  last_score: ScoreResult;
  question?: Question;
  question_number?: number;
  total_questions?: number;
  topic_breakdown?: Record<string, number>;
  focus_recommendations?: string[];
}

export interface ResumeData {
  resume_id: number;
  parsed_data: {
    skills: string[];
    projects: { name: string; description: string }[];
    experience_level: string;
    gaps: string[];
  };
}
