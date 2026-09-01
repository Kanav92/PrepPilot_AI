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
Analyze this resume and return ONLY a JSON object with no explanation, no markdown:
{{
  "skills": ["skill1", "skill2"],
  "projects": [
    {{"name": "project name", "description": "what it does and tech used"}}
  ],
  "experience": [
    {{"company": "company name", "role": "job title", "description": "what you built or did there and tech used"}}
  ],
  "experience_level": "student|junior|mid",
  "gaps": ["gap1", "gap2"]
}}

Rules:
- skills: extract ALL technical skills mentioned anywhere in the resume
- projects: extract all personal/academic projects
- experience: extract all internships and work experience (not projects)
- If no work experience exists, return experience as an empty array []
- experience_level: use "student" if no work experience, "junior" if 1-2 internships, "mid" if 2+ years

Resume:
{raw_text[:4000]}

Return only the raw JSON object, no code fences, no backticks."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
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
        resume_data = json.loads(text)
    except Exception as e:
        print(f"[ResumeAnalyzer] JSON parse failed: {e}")
        resume_data = {
            "skills": [],
            "projects": [],
            "experience": [],
            "experience_level": "student",
            "gaps": []
        }

    resume_data["raw_text"] = raw_text
    print(f"[ResumeAnalyzer] Extracted {len(resume_data.get('skills', []))} skills, "
          f"{len(resume_data.get('projects', []))} projects, "
          f"{len(resume_data.get('experience', []))} work experience entries")
    return {"resume_data": resume_data}
