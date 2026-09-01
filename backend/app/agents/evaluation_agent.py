import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.agents.state import InterviewState
from app.tools.evaluation_tools import retrieve_concept_reference

load_dotenv()

def evaluation_node(state: InterviewState) -> dict:
    print("[EvaluationAgent] Evaluating answer...")

    current_question = state.get("current_question", {})
    question_text = current_question.get("question_text", "")
    topic = current_question.get("topic", "DSA")
    idx = state.get("current_question_idx", 0)
    user_answer = state.get("current_answer", "").strip()

    if not user_answer:
        # No answer submitted — score as 0, no API call needed
        score_entry = {
            "topic": topic,
            "score": 0,
            "missing_concepts": ["no answer provided"],
            "feedback": "No answer was submitted for this question."
        }
        answer_entry = {"question": question_text, "answer": "", "topic": topic}
        print(f"[EvaluationAgent] Score: 0/100 for topic {topic} (empty answer)")
        return {
            "answers": [answer_entry],
            "scores": [score_entry],
            "current_question_idx": idx + 1,
            "messages": [],
            "current_answer": ""
        }

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    ref_result = retrieve_concept_reference.invoke({
        "topic": topic,
        "concept_key": question_text[:50]
    })
    reference_text = ref_result.get("reference_text", "Use general technical knowledge to evaluate.")

    prompt = f"""You are a strict but fair technical interview evaluator.

Question: {question_text}
Topic: {topic}
Reference concepts: {reference_text}
Candidate's answer: {user_answer}

Score the answer fairly based on technical correctness and completeness.
Return ONLY this JSON, no markdown, no explanation:
{{
  "score": <integer 0-100>,
  "missing_concepts": ["concept1", "concept2"],
  "feedback": "one specific sentence of constructive feedback"
}}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        result = json.loads(text)
    except Exception as e:
        print(f"[EvaluationAgent] JSON parse failed: {e}")
        result = {"score": 50, "missing_concepts": [], "feedback": "Could not fully parse evaluation, default score given."}

    score_entry = {
        "topic": topic,
        "score": result.get("score", 50),
        "missing_concepts": result.get("missing_concepts", []),
        "feedback": result.get("feedback", "")
    }
    answer_entry = {
        "question": question_text,
        "answer": user_answer,
        "topic": topic
    }

    print(f"[EvaluationAgent] Score: {score_entry['score']}/100 for topic {topic}")

    return {
        "answers": [answer_entry],
        "scores": [score_entry],
        "current_question_idx": idx + 1,
        "messages": [],
        "current_answer": ""  # clear it so it doesn't leak into next question
    }
