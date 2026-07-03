from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, resume_routes, interview_routes

app = FastAPI(title="InterviewForge AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://preppilot-ai.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(resume_routes.router)
app.include_router(interview_routes.router)

@app.get("/")
def root():
    return {"message": "PrepPilot AI backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
