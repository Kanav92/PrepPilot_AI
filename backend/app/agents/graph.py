import json
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.agents.state import InterviewState
from app.agents.resume_analyzer import resume_analyzer_node
from app.agents.interview_agent import interview_node, tools as interview_tools
from app.agents.evaluation_agent import evaluation_node
from app.agents.planner_agent import planner_node

MAX_QUESTIONS = 10
interview_tool_node = ToolNode(interview_tools)

FALLBACK_QUESTIONS = {
    "DSA":  {"question_text": "What is dynamic programming? Give an example.", "topic": "DSA", "difficulty": "medium", "expected_concepts": ["memoization", "overlapping subproblems"]},
    "DBMS": {"question_text": "Explain the ACID properties of a transaction.", "topic": "DBMS", "difficulty": "medium", "expected_concepts": ["atomicity", "consistency", "isolation", "durability"]},
    "OS":   {"question_text": "What is a deadlock and what are the four necessary conditions?", "topic": "OS", "difficulty": "medium", "expected_concepts": ["mutual exclusion", "hold and wait", "no preemption", "circular wait"]},
    "CN":   {"question_text": "What is the difference between TCP and UDP?", "topic": "CN", "difficulty": "medium", "expected_concepts": ["reliability", "connection-oriented", "latency"]},
    "OOP":  {"question_text": "What are the four pillars of OOP?", "topic": "OOP", "difficulty": "medium", "expected_concepts": ["encapsulation", "inheritance", "polymorphism", "abstraction"]},
}
TOPIC_ORDER = ["DSA", "DBMS", "OS", "CN", "OOP"]

def set_question_node(state: InterviewState) -> dict:
    messages = state.get("messages", [])
    questions_asked = state.get("questions", [])
    current_question = {}

    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        if not content:
            continue
        if isinstance(content, str):
            try:
                data = json.loads(content)
                if isinstance(data, dict) and "question_text" in data:
                    current_question = data
                    break
            except:
                pass
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and "question_text" in block:
                    current_question = block
                    break
            if current_question:
                break

    if not current_question:
        print("[SetQuestion] Tool result parse failed — using fallback")
        topics_covered = [q.get("topic", "") for q in questions_asked]
        for t in TOPIC_ORDER:
            if t not in topics_covered:
                current_question = FALLBACK_QUESTIONS[t]
                break
        if not current_question:
            current_question = FALLBACK_QUESTIONS["DSA"]

    print(f"[SetQuestion] Topic: {current_question.get('topic')} | Q: {current_question.get('question_text', '')[:60]}...")

    return {
        "current_question": current_question,
        "questions": [current_question],
        "messages": []
    }


# ============================================================
# GRAPH A — Used to START the interview and GENERATE each question.
# Entry point: resume_analyzer (only matters on the very first call;
# subsequent calls only touch interview->tools->set_question since
# resume_data is already in checkpointed state and Resume Analyzer
# is cheap to skip via the route logic, not the graph itself).
# ============================================================
def build_question_graph(checkpointer=None):
    graph = StateGraph(InterviewState)

    graph.add_node("interview", interview_node)
    graph.add_node("interview_tools", interview_tool_node)
    graph.add_node("set_question", set_question_node)

    graph.set_entry_point("interview")
    graph.add_edge("interview", "interview_tools")
    graph.add_edge("interview_tools", "set_question")
    graph.add_edge("set_question", END)

    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# ============================================================
# GRAPH B — Used once, at the very start, to analyze the resume.
# Separate so it only ever runs exactly once per session.
# ============================================================
def build_resume_graph(checkpointer=None):
    graph = StateGraph(InterviewState)
    graph.add_node("resume_analyzer", resume_analyzer_node)
    graph.set_entry_point("resume_analyzer")
    graph.add_edge("resume_analyzer", END)

    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# ============================================================
# GRAPH C — Used when the user SUBMITS AN ANSWER. Just evaluation.
# ============================================================
def build_evaluation_graph(checkpointer=None):
    graph = StateGraph(InterviewState)
    graph.add_node("evaluation", evaluation_node)
    graph.set_entry_point("evaluation")
    graph.add_edge("evaluation", END)

    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# ============================================================
# GRAPH D — Used once, when MAX_QUESTIONS is reached. Planner only.
# ============================================================
def build_planner_graph(checkpointer=None):
    graph = StateGraph(InterviewState)
    graph.add_node("planner", planner_node)
    graph.set_entry_point("planner")
    graph.add_edge("planner", END)

    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()
