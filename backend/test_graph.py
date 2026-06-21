import sys
sys.path.insert(0, ".")
from app.agents.graph import interview_graph

initial_state = {
    "user_id": 1,
    "session_id": 1,
    "resume_id": 1,
    "resume_data": {},
    "questions": [],
    "current_question_idx": 0,
    "current_question": {},
    "difficulty_level": "medium",
    "answers": [],
    "scores": [],
    "topic_breakdown": {},
    "focus_recommendations": [],
    "interview_complete": False,
    "messages": [],
    "tool_types_used": [],
    "current_answer": ""
}

print("Running InterviewForge AI pipeline...\n")
final_state = interview_graph.invoke(initial_state, {"recursion_limit": 60})

print("\n--- Final State ---")
print("Questions asked:", len(final_state.get("questions", [])))
print("Answers recorded:", len(final_state.get("answers", [])))
print("Topic breakdown:", final_state.get("topic_breakdown"))
print("Recommendations:")
for r in final_state.get("focus_recommendations", []):
    print(" -", r)
