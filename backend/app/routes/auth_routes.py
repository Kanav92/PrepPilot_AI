from fastapi import APIRouter, HTTPException
from app.models.schemas import SignupRequest, LoginRequest, AuthResponse
from app.auth import hash_password, verify_password, create_access_token
from app.db.database import get_connection

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = %s", (payload.email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(payload.password)
    cur.execute(
        "INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s) RETURNING id",
        (payload.email, hashed, payload.name)
    )
    user_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()

    token = create_access_token(user_id, payload.email)
    return AuthResponse(access_token=token, user_id=user_id, email=payload.email, name=payload.name)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, email, name, password_hash FROM users WHERE email = %s", (payload.email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user["id"], user["email"])
    return AuthResponse(access_token=token, user_id=user["id"], email=user["email"], name=user["name"])
