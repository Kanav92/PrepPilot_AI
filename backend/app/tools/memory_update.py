import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)

def update_long_term_performance(user_id: int, topic_breakdown: dict):
    conn = get_conn()
    cur = conn.cursor()

    updated_topics = []

    for topic, session_score in topic_breakdown.items():
        cur.execute(
            """
            SELECT rolling_average_score, attempt_count
            FROM user_topic_performance
            WHERE user_id = %s AND topic = %s
            """,
            (user_id, topic)
        )
        existing = cur.fetchone()

        if existing:
            old_avg = float(existing["rolling_average_score"])
            old_count = existing["attempt_count"]
            new_count = old_count + 1
            new_avg = ((old_avg * old_count) + session_score) / new_count

            cur.execute(
                """
                UPDATE user_topic_performance
                SET rolling_average_score = %s,
                    attempt_count = %s,
                    last_attempted = NOW()
                WHERE user_id = %s AND topic = %s
                """,
                (round(new_avg, 2), new_count, user_id, topic)
            )
        else:
            cur.execute(
                """
                INSERT INTO user_topic_performance (user_id, topic, rolling_average_score, attempt_count, last_attempted)
                VALUES (%s, %s, %s, 1, NOW())
                """,
                (user_id, topic, session_score)
            )

        updated_topics.append(topic)

    conn.commit()
    cur.close()
    conn.close()
    print(f"[MemoryUpdate] Updated long-term performance for topics: {updated_topics}")
    return updated_topics
