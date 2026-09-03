import os
import json
from decimal import Decimal
from datetime import datetime, date
from groq import Groq
from dotenv import load_dotenv
from app.agents.state import InterviewState
from app.tools.planner_tools import fetch_long_term_performance

load_dotenv()

def json_safe(obj):
    """Recursively convert non-JSON-serializable types (Decimal, datetime) to safe equivalents."""
    if isinstance(obj, list):
        return [json_safe(x) for x in obj]
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj

def planner_node(state: InterviewState) -> dict:
    print("[PlannerAgent] Generating personalized roadmap...")

    user_id = state.get("user_id", 1)
    scores = state.get("scores", [])

    topic_scores = {}
    topic_counts = {}
    for s in scores:
        t = s.get("topic", "UNKNOWN")
        topic_scores[t] = topic_scores.get(t, 0) + s.get("score", 0)
        topic_counts[t] = topic_counts.get(t, 0) + 1

    topic_breakdown = {
        t: round(topic_scores[t] / topic_counts[t])
        for t in topic_scores if topic_counts[t] > 0
    }

    long_term = fetch_long_term_performance.invoke({"user_id": user_id})
    historical = json_safe(long_term.get("performance", []))

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a study planner for software engineering interview preparation.

Current session scores (out of 100):
{json.dumps(topic_breakdown, indent=2)}

Historical performance:
{json.dumps(historical, indent=2) if historical else "First session - no history yet."}

Return ONLY valid JSON, no explanation, no markdown:
{{"focus_recommendations": ["recommendation 1", "recommendation 2", "recommendation 3", "recommendation 4", "recommendation 5"]}}

Make recommendations specific and actionable. Prioritize weakest topics."""

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
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
        recommendations = result.get("focus_recommendations", [])
        if not recommendations:
            raise ValueError("Empty recommendations")
    except Exception as e:
        print(f"[PlannerAgent] JSON parse failed: {e}")
        sorted_topics = sorted(topic_breakdown.items(), key=lambda x: x[1])
        recommendations = [
            f"Priority 1: Focus on {sorted_topics[0][0]} — scored {sorted_topics[0][1]}/100" if len(sorted_topics) > 0 else "Review all topics",
            f"Priority 2: Practice {sorted_topics[1][0]} questions daily" if len(sorted_topics) > 1 else "Practice DSA problems",
            f"Strong area: {sorted_topics[-1][0]} at {sorted_topics[-1][1]}/100 — maintain this" if len(sorted_topics) > 2 else "Keep up the good work",
            "Attempt mock interviews weekly to track progress",
            "Review missing concepts from each question's feedback"
        ]

    print(f"[PlannerAgent] Generated {len(recommendations)} recommendations")

    return {
        "topic_breakdown": topic_breakdown,
        "focus_recommendations": recommendations
    }
