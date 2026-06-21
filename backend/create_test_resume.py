from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("test_resume.pdf", pagesize=letter)
c.setFont("Helvetica", 11)

lines = [
    "Kanav Goyal",
    "B.Tech Computer Science, Punjab Engineering College (2023-2027)",
    "",
    "SKILLS",
    "Python, C++, JavaScript, PostgreSQL, Redis, React, FastAPI, Next.js, LangChain",
    "",
    "PROJECTS",
    "LinkForge - URL Shortener and Analytics Platform",
    "Built a full-stack URL shortener using Next.js and Express.js with PostgreSQL",
    "for storage and Redis for caching and rate limiting. Implemented JWT auth",
    "and click analytics dashboard.",
    "",
    "InterviewForge AI - Multi-Agent Interview Prep Platform",
    "Building a multi-agent system using LangGraph and FastAPI that conducts",
    "adaptive mock interviews, evaluates answers using LLMs, and generates",
    "personalized study plans based on performance.",
    "",
    "EXPERIENCE",
    "Competitive programmer on Codeforces, solved 300+ problems.",
]

y = 750
for line in lines:
    c.drawString(50, y, line)
    y -= 18

c.save()
print("test_resume.pdf created")
