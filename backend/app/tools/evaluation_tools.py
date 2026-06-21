import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)

@tool
def retrieve_concept_reference(topic: str, concept_key: str) -> dict:
    """Retrieve the reference explanation for a concept to ground the evaluation.
    Use this before scoring an answer to get the expected correct explanation.
    Topics: DSA, DBMS, OS, CN, OOP, PROJECT
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT topic, concept_key, reference_text
            FROM concept_reference
            WHERE topic = %s AND concept_key ILIKE %s
            LIMIT 1
            """,
            (topic.upper(), f"%{concept_key}%")
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return dict(row)
        return {"reference_text": "No specific reference found. Use general knowledge to evaluate."}
    except Exception as e:
        return {"reference_text": "Reference lookup failed. Use general knowledge to evaluate."}
