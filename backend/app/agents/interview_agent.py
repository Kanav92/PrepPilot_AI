import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.state import InterviewState
from app.tools.question_tools import (
    fetch_question_from_bank,
    generate_project_question,
    generate_followup_question
)

load_dotenv()

TOPICS = ["DSA", "DBMS", "OS", "CN", "OOP"]
MAX_QUESTIONS = 10
MIN_PROJECT_QUESTIONS = 3
tools = [fetch_question_from_bank, generate_project_question, generate_followup_question]

def get_next_topic(topics_covered: list, idx: int) -> str:
    recent = topics_covered[-3:] if len(topics_covered) >= 3 else topics_covered
    available = [t for t in TOPICS if t not in recent]
    if not available:
        available = TOPICS
    return available[idx % len(available)]

def interview_node(state: InterviewState) -> dict:
    idx = state.get("current_question_idx", 0)
    scores = state.get("scores", [])
    resume_data = state.get("resume_data", {})
    projects = resume_data.get("projects", [])
    questions_asked = state.get("questions", [])
    tool_types_used = state.get("tool_types_used", [])

    print(f"[InterviewAgent] Deciding next question (idx: {idx})...")

    if idx >= MAX_QUESTIONS:
        return {"interview_complete": True, "current_question": {}, "messages": []}

    last_score = scores[-1].get("score", 75) if scores else 75
    last_topic = scores[-1].get("topic", "") if scores else ""
    last_question_text = questions_asked[-1].get("question_text", "") if questions_asked else ""
    topics_covered = [q.get("topic", "") for q in questions_asked]

    if last_score < 50:
        difficulty = "easy"
    elif last_score > 80:
        difficulty = "hard"
    else:
        difficulty = "medium"

    project_questions_asked = topics_covered.count("PROJECT")
    last_tool_type = tool_types_used[-1] if tool_types_used else None
    can_do_followup = last_tool_type != "followup"

    questions_remaining = MAX_QUESTIONS - idx
    project_questions_still_needed = max(0, min(MIN_PROJECT_QUESTIONS, len(projects)) - project_questions_asked)
    must_force_project = projects and project_questions_still_needed >= questions_remaining

    asked_bank_ids = [str(q.get("id")) for q in questions_asked if q.get("id") is not None]
    asked_project_questions = [q.get("question_text", "") for q in questions_asked if q.get("topic") == "PROJECT"]

    if last_score < 50 and scores and can_do_followup:
        tool_type = "followup"
        next_topic = last_topic
    elif must_force_project or (
        projects
        and project_questions_asked < min(MIN_PROJECT_QUESTIONS, len(projects))
        and idx > 0
        and idx % 3 == 0
    ):
        tool_type = "project"
        next_topic = "PROJECT"
    else:
        tool_type = "bank"
        next_topic = get_next_topic(topics_covered, idx)

    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile"
    ).bind_tools(tools)

    system_prompt = "You are an interview question selector. Call exactly the tool specified. No text responses."

    if tool_type == "followup":
        user_msg = f"""Call generate_followup_question with:
- previous_question: "{last_question_text}"
- previous_answer: "answer missing core concepts"
- topic: "{next_topic}" """

    elif tool_type == "project":
        project = projects[project_questions_asked % len(projects)]
        exclude_str = " | ".join(asked_project_questions)
        user_msg = f"""Call generate_project_question with:
- project_name: "{project['name']}"
- project_description: "{project['description']}"
- difficulty: "{difficulty}"
- exclude_questions: "{exclude_str}" """

    else:
        exclude_str = ",".join(asked_bank_ids)
        user_msg = f"""Call fetch_question_from_bank with:
- topic: "{next_topic}"
- difficulty: "{difficulty}"
- exclude_ids: "{exclude_str}" """

    print(f"[InterviewAgent] Tool: {tool_type}, Topic: {next_topic}, Difficulty: {difficulty}")

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ])

    return {
        "messages": [response],
        "difficulty_level": difficulty,
        "tool_types_used": [tool_type]
    }
