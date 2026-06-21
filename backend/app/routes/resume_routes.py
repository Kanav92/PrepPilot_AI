from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.dependencies import get_current_user
from app.tools.pdf_tools import extract_text_from_pdf
from app.agents.resume_analyzer import resume_analyzer_node
from app.db.database import get_connection
import json

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()

    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    fake_state = {"resume_data": {"raw_text": raw_text}}
    result = resume_analyzer_node(fake_state)
    resume_data = result["resume_data"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO resumes (user_id, raw_text, parsed_data)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (current_user["user_id"], raw_text, json.dumps(resume_data))
    )
    resume_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()

    return {
        "resume_id": resume_id,
        "parsed_data": resume_data
    }


@router.get("/list")
def list_resumes(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, parsed_data, uploaded_at FROM resumes WHERE user_id = %s ORDER BY uploaded_at DESC",
        (current_user["user_id"],)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"resumes": [dict(r) for r in rows]}
