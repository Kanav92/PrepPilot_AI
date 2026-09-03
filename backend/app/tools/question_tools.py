import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)

@tool
def fetch_question_from_bank(topic: str, difficulty: str, exclude_ids: Optional[str] = "") -> dict:
    """Fetch a question from the question bank for a given topic and difficulty,
    excluding any question IDs already asked this session.
    Topics: DSA, DBMS, OS, CN, OOP
    Difficulty: easy, medium, hard
    exclude_ids: comma-separated string of question IDs to exclude, e.g. "3,7,12". Leave empty if none.
    """
    ids_list = []
    if exclude_ids and exclude_ids.strip():
        try:
            ids_list = [int(x.strip()) for x in exclude_ids.split(",") if x.strip().isdigit()]
        except Exception:
            ids_list = []

    try:
        conn = get_conn()
        cur = conn.cursor()

        if ids_list:
            placeholders = ",".join(["%s"] * len(ids_list))
            cur.execute(
                f"""
                SELECT id, topic, difficulty, question_text, expected_concepts
                FROM question_bank
                WHERE topic = %s AND difficulty = %s AND id NOT IN ({placeholders})
                ORDER BY RANDOM()
                LIMIT 1
                """,
                (topic.upper(), difficulty.lower(), *ids_list)
            )
        else:
            cur.execute(
                """
                SELECT id, topic, difficulty, question_text, expected_concepts
                FROM question_bank
                WHERE topic = %s AND difficulty = %s
                ORDER BY RANDOM()
                LIMIT 1
                """,
                (topic.upper(), difficulty.lower())
            )
        row = cur.fetchone()

        if not row:
            if ids_list:
                placeholders = ",".join(["%s"] * len(ids_list))
                cur.execute(
                    f"""
                    SELECT id, topic, difficulty, question_text, expected_concepts
                    FROM question_bank
                    WHERE topic = %s AND id NOT IN ({placeholders})
                    ORDER BY RANDOM()
                    LIMIT 1
                    """,
                    (topic.upper(), *ids_list)
                )
            else:
                cur.execute(
                    """
                    SELECT id, topic, difficulty, question_text, expected_concepts
                    FROM question_bank
                    WHERE topic = %s
                    ORDER BY RANDOM()
                    LIMIT 1
                    """,
                    (topic.upper(),)
                )
            row = cur.fetchone()

        cur.close()
        conn.close()
        if row:
            return dict(row)
        return {"error": f"No question found for topic={topic}, difficulty={difficulty}"}
    except Exception as e:
        return {"error": str(e)}

@tool
def generate_project_question(project_name: str, project_description: str, difficulty: str, exclude_questions: Optional[str] = "") -> dict:
    """Generate a personalized interview question based on the user's resume project.
    Use this when you want to ask about a specific project from the user's resume.
    exclude_questions: questions already asked about this project, separated by ' | '. Leave empty if none.
    """
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    avoid_text = ""
    if exclude_questions and exclude_questions.strip():
        avoid_list = exclude_questions.split(" | ")
        avoid_str = "\n".join(f"- {q}" for q in avoid_list if q.strip())
        if avoid_str:
            avoid_text = f"\n\nDo NOT repeat or closely rephrase these already-asked questions:\n{avoid_str}\nAsk about a genuinely different aspect of the project."

    prompt = f"""You are a technical interviewer. Generate exactly ONE interview question 
about this project:
Project: {project_name}
Description: {project_description}
Difficulty: {difficulty}{avoid_text}

Return ONLY a JSON object with these exact keys:
{{
  "question_text": "your question here",
  "topic": "PROJECT",
  "difficulty": "{difficulty}",
  "expected_concepts": ["concept1", "concept2"]
}}
Return only the JSON, no explanation."""

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    import json
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        return json.loads(text)
    except:
        return {"question_text": text, "topic": "PROJECT", "difficulty": difficulty, "expected_concepts": []}

@tool
def generate_followup_question(previous_question: str, previous_answer: str, topic: str) -> dict:
    """Generate a followup question when the user's answer was weak or incomplete.
    Use this when score < 50 to probe the same concept deeper.
    """
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"""You are a technical interviewer. The candidate gave a weak answer.
Previous question: {previous_question}
Candidate's answer: {previous_answer}
Topic: {topic}

Generate ONE followup question to probe their understanding deeper.
Return ONLY a JSON object:
{{
  "question_text": "your followup question here",
  "topic": "{topic}",
  "difficulty": "medium",
  "expected_concepts": ["concept1", "concept2"]
}}
Return only the JSON, no explanation."""

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    import json
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        return json.loads(text)
    except:
        return {"question_text": text, "topic": topic, "difficulty": "medium", "expected_concepts": []}
