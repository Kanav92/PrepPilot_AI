from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.models.schemas import AnswerSubmission
from app.db.database import get_connection
from app.agents.checkpointer import get_checkpointer
from app.agents.graph import (
    build_resume_graph, build_question_graph,
    build_evaluation_graph, build_planner_graph, MAX_QUESTIONS
)
from app.tools.memory_update import update_long_term_performance
import json

router = APIRouter(prefix="/interview", tags=["interview"])


def get_thread_config(session_id: int):
    return {"configurable": {"thread_id": f"session-{session_id}"}}


@router.post("/start")
def start_interview(resume_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    # Verify resume belongs to this user, and fetch its data
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, raw_text, parsed_data FROM resumes WHERE id = %s AND user_id = %s",
        (resume_id, user_id)
    )
    resume = cur.fetchone()
    if not resume:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Resume not found for this user")

    # Create a new interview session row
    cur.execute(
        "INSERT INTO interview_sessions (user_id, resume_id, status) VALUES (%s, %s, 'in_progress') RETURNING id",
        (user_id, resume_id)
    )
    session_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()

    config = get_thread_config(session_id)

    with get_checkpointer() as checkpointer:
        resume_graph = build_resume_graph(checkpointer=checkpointer)
        question_graph = build_question_graph(checkpointer=checkpointer)

        parsed_data = resume["parsed_data"]
        if isinstance(parsed_data, str):
            parsed_data = json.loads(parsed_data)
        parsed_data["raw_text"] = resume["raw_text"]

        initial_state = {
            "user_id": user_id,
            "session_id": session_id,
            "resume_id": resume_id,
            "resume_data": parsed_data,
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

        resume_graph.invoke(initial_state, config)
        result = question_graph.invoke({}, config)

    return {
        "session_id": session_id,
        "question": result["current_question"],
        "question_number": len(result["questions"]),
        "total_questions": MAX_QUESTIONS
    }


@router.post("/answer")
def submit_answer(payload: AnswerSubmission, current_user: dict = Depends(get_current_user)):
    session_id = payload.session_id
    user_id = current_user["user_id"]

    # Verify session belongs to this user
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, status FROM interview_sessions WHERE id = %s AND user_id = %s",
        (session_id, user_id)
    )
    session = cur.fetchone()
    cur.close()
    conn.close()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found for this user")
    if session["status"] == "completed":
        raise HTTPException(status_code=400, detail="This interview session is already completed")

    config = get_thread_config(session_id)

    with get_checkpointer() as checkpointer:
        evaluation_graph = build_evaluation_graph(checkpointer=checkpointer)
        question_graph = build_question_graph(checkpointer=checkpointer)
        planner_graph = build_planner_graph(checkpointer=checkpointer)

        eval_result = evaluation_graph.invoke({"current_answer": payload.answer_text}, config)
        last_score = eval_result["scores"][-1]
        idx = eval_result["current_question_idx"]

        if idx >= MAX_QUESTIONS:
            # Interview done — run planner, save everything
            planner_result = planner_graph.invoke({}, config)
            topic_breakdown = planner_result["topic_breakdown"]
            recommendations = planner_result["focus_recommendations"]

            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE interview_sessions SET status = 'completed', completed_at = NOW() WHERE id = %s",
                (session_id,)
            )
            cur.execute(
                """
                INSERT INTO session_summaries (session_id, topic_breakdown, focus_recommendations)
                VALUES (%s, %s, %s)
                """,
                (session_id, json.dumps(topic_breakdown), recommendations)
            )
            # Save all individual answers too
            for ans, sc in zip(eval_result["answers"], eval_result["scores"]):
                cur.execute(
                    """
                    INSERT INTO answers (session_id, question_text, topic, user_answer, score, missing_concepts, feedback)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (session_id, ans["question"], ans["topic"], ans["answer"], sc["score"], sc["missing_concepts"], sc["feedback"])
                )
            conn.commit()
            cur.close()
            conn.close()

            update_long_term_performance(user_id, topic_breakdown)

            return {
                "interview_complete": True,
                "last_score": last_score,
                "topic_breakdown": topic_breakdown,
                "focus_recommendations": recommendations
            }
        else:
            next_q_result = question_graph.invoke({}, config)
            return {
                "interview_complete": False,
                "last_score": last_score,
                "question": next_q_result["current_question"],
                "question_number": len(next_q_result["questions"]),
                "total_questions": MAX_QUESTIONS
            }


@router.get("/results/{session_id}")
def get_results(session_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, status, started_at, completed_at FROM interview_sessions WHERE id = %s AND user_id = %s",
        (session_id, user_id)
    )
    session = cur.fetchone()
    if not session:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")

    cur.execute(
        "SELECT topic_breakdown, focus_recommendations FROM session_summaries WHERE session_id = %s",
        (session_id,)
    )
    summary = cur.fetchone()

    cur.execute(
        "SELECT question_text, topic, score, missing_concepts, feedback FROM answers WHERE session_id = %s ORDER BY id",
        (session_id,)
    )
    answers = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "session": dict(session),
        "summary": dict(summary) if summary else None,
        "answers": [dict(a) for a in answers]
    }
