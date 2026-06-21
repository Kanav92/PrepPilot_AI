from fastapi import Header, HTTPException
from app.auth import decode_access_token

def get_current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_access_token(token)
        return {"user_id": int(payload["sub"]), "email": payload["email"]}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
