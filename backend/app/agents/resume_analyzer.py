import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.agents.state import InterviewState

load_dotenv()

def resume_analyzer_node(state: InterviewState) -> dict:
    print("[ResumeAnalyzer] Analyzing resume...")

    raw_text = state.get("resume_data", {}).get("raw_text")

    if not raw_text:
        raw_text = """
        Name: Test User
        Skills: Python, C++, PostgreSQL, Redis, React, FastAPI
        Projects:
        - LinkForge: A URL shortener with analytics, Redis caching, rate limiting, JWT auth
        Experience: B.Tech CSE student
        """

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"""You are a resume analyzer for a technical interview platform.
Analyze this resume and return ONLY a JSON object with no explanation, no markdown formatting:
{{
  "skills": ["skill1", "skill2"],
  "projects": [
    {{"name": "project name", "description": "what it does and tech used"}}
  ],
  "experience_level": "student|junior|mid",
  "gaps": ["gap1", "gap2"]
}}

Resume:
{raw_text[:4000]}

Return only the raw JSON object, no code fences, no backticks."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )

    text = response.choices[0].message.content.strip()

    # Strip markdown code fences if Groq added them
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        # handle trailing fence if split missed it
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        resume_data = json.loads(text)
    except Exception as e:
        print(f"[ResumeAnalyzer] JSON parse failed: {e}, raw text: {text[:150]}")
        resume_data = {
            "skills": [],
            "projects": [],
            "experience_level": "student",
            "gaps": []
        }

    resume_data["raw_text"] = raw_text
    print(f"[ResumeAnalyzer] Extracted {len(resume_data.get('skills', []))} skills, {len(resume_data.get('projects', []))} projects")
    return {"resume_data": resume_data}
