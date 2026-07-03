# PrepPilot AI

A multi-agent interview preparation platform for campus placements — analyzes your resume, runs an adaptive mock interview across DSA/DBMS/OS/CN/OOP and your real projects, evaluates your answers with LLM-grounded scoring, and builds a personalized study plan that improves with every session.

Built as a portfolio project demonstrating real multi-agent orchestration, stateful LLM workflows, and full-stack engineering — not just an LLM wrapper.

---

## Screenshots

### Resume Upload — skills, projects and experience extracted from your real PDF
![Resume Upload](screenshots/Resume_page.png)



### Interview Screen — live agent trace sidebar updating in real time
![Interview Screen](screenshots/Interview_page.png)


### Results Page — topic breakdown, scores, and planner recommendations
![Results Page](screenshots/Result_page.png)

---

## What it actually does

1. **Upload a resume** → an AI agent extracts your skills, projects, and experience level from the raw PDF
2. **Take a 10-question adaptive interview** → questions span fixed CS fundamentals and your actual resume projects, with difficulty that shifts based on how you're doing in real time
3. **Get scored per answer** → an evaluation agent grades you against grounded reference concepts, not just unconstrained LLM judgment
4. **Receive a personalized study plan** → a planning agent looks at this session *and* your performance history across all past sessions to recommend what to focus on next

---

## Why this is "agentic," not just "an app that calls an LLM"

The core design decision: **deterministic logic decides strategy, the LLM executes it via tool calls.**

A plain Python rule decides what topic, what difficulty, and what *kind* of question comes next (fixed-bank question vs. a fresh question about your project vs. a followup probing a weak answer). The LLM's only job at that point is to call the correct tool with the right arguments. This split exists because letting an LLM freely decide topic sequencing turned out to be unreliable in practice (it would fixate on one topic) — but generating a question about *your specific* deepfake detection project genuinely needs an LLM, since no static question bank could contain that.

Four agents, each a LangGraph node:

| Agent | Responsibility | Tools it calls |
|---|---|---|
| **Resume Analyzer** | Extracts structured data from your resume | PDF text extraction → LLM structuring |
| **Interview Agent** | Selects and generates each question | `fetch_question_from_bank`, `generate_project_question`, `generate_followup_question` |
| **Evaluation Agent** | Scores each typed answer | `retrieve_concept_reference` (grounding), then LLM scoring |
| **Planner Agent** | Builds the study roadmap | `fetch_long_term_performance`, then LLM recommendation generation |

---

## Tech stack

**Frontend** — Next.js (App Router), TypeScript, Tailwind CSS
**Backend** — FastAPI (Python)
**Agent orchestration** — LangGraph, with PostgreSQL-backed checkpointing for stateful sessions
**LLM** — Groq API running Llama 3.3 70B
**Database** — PostgreSQL
**Auth** — JWT (PyJWT) + bcrypt password hashing
**PDF parsing** — PyPDF

---

## Architecture highlights

### Stateful orchestration across stateless HTTP requests

Each question and each answer arrives as a *separate* HTTP request — but a mock interview needs continuous state (which question you're on, your running scores, your difficulty trajectory). This is solved with LangGraph's `PostgresSaver` checkpointer: every graph invocation is keyed by a `thread_id` (the interview session ID), and state automatically persists in Postgres between calls.

The system is split into four smaller graphs — `resume_graph`, `question_graph`, `evaluation_graph`, `planner_graph` — rather than one large graph, because a single graph has one entry point, and every API call (even just submitting an answer) would otherwise re-run the whole pipeline from the start. Splitting by which endpoint triggers it maps cleanly onto natural request boundaries.

### Long-term memory, separate from session memory

Two distinct memory systems exist:
- **Short-term**: the LangGraph checkpoint, scoped to one interview session
- **Long-term**: a `user_topic_performance` table tracking a weighted rolling average score per topic, updated after every completed session:new_average = ((old_average × old_attempt_count) + this_session_score) / (old_attempt_count + 1)
This means a single bad session doesn't overwrite your history — your tracked skill level reflects a pattern across all attempts, and the Planner Agent reads this back in before generating recommendations.

### RAG-grounded evaluation

Before scoring an answer, the Evaluation Agent retrieves a reference explanation from a `concept_reference` table via a real tool call, then includes that as grounding context in the scoring prompt — reducing purely vibes-based LLM grading.

---

## Database schema

8 application tables: `users`, `resumes`, `question_bank`, `concept_reference`, `interview_sessions`, `answers`, `user_topic_performance`, `session_summaries` — plus 4 tables LangGraph's checkpointer manages automatically.

---

## Live Demo

- **Frontend:** https://prep-pilot-ai-xi.vercel.app
- **Backend API:** https://preppilot-backend-5wkw.onrender.com
- **API Docs:** https://preppilot-backend-5wkw.onrender.com/docs

> Note: The backend runs on Render's free tier and may take 30-60 seconds to wake up after inactivity. Open the app a minute before demoing.

---

## Running it locally

**Requirements:** Python 3.11+, Node.js 18+, PostgreSQL, a free Groq API key from [console.groq.com](https://console.groq.com)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or see below for manual install
```

Create a `.env` file in `backend/`:
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/interviewforge

GROQ_API_KEY=your_groq_key_here

JWT_SECRET=generate_a_random_secret
Apply the schema:
```bash
psql -U your_user -d interviewforge -f app/db/schema.sql
```

Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` (or whatever port it prints).

---

## What I'd add next

- Deployment (Vercel + Railway)
- Automated tests around the agent decision logic
- Company-specific interview modes (Amazon SDE, Google SWE, etc. — prompt-template variants)
- Rate limiting on LLM calls
- A semantic (embedding-based) memory layer for recalling specific past question content, not just numeric performance trends

---

## A note on scope

This is a deliberately tight v1: 4 agents, a working adaptive loop, real long-term memory, real auth — built end-to-end and fully tested, rather than a large feature list left half-finished. Several real bugs surfaced and were fixed during development (Postgres `Decimal`/`datetime` JSON serialization, an LLM followup-loop that needed deterministic state tracking instead of an inferred flag, and Groq's strict tool-schema validation rejecting `null` for array parameters) — all documented in commit history.
