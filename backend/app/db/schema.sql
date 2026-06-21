-- InterviewForge AI — v1 Postgres Schema

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    name            VARCHAR(255),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE resumes (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE 
CASCADE,
    raw_text        TEXT,
    parsed_data     JSONB,
    uploaded_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE question_bank (
    id              SERIAL PRIMARY KEY,
    topic           VARCHAR(50) NOT NULL,
    difficulty      VARCHAR(20) NOT NULL,
    question_text   TEXT NOT NULL,
    expected_concepts TEXT[]
);

CREATE TABLE concept_reference (
    id              SERIAL PRIMARY KEY,
    topic           VARCHAR(50) NOT NULL,
    concept_key     VARCHAR(255) NOT NULL,
    reference_text  TEXT NOT NULL
);

CREATE TABLE interview_sessions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE 
CASCADE,
    resume_id       INTEGER REFERENCES resumes(id),
    status          VARCHAR(20) DEFAULT 'in_progress',
    started_at      TIMESTAMP DEFAULT NOW(),
    completed_at    TIMESTAMP
);

CREATE TABLE answers (
    id                  SERIAL PRIMARY KEY,
    session_id          INTEGER NOT NULL REFERENCES interview_sessions(id) 
ON DELETE CASCADE,
    question_text       TEXT NOT NULL,
    topic                VARCHAR(50),
    difficulty           VARCHAR(20),
    user_answer          TEXT,
    score                INTEGER,
    missing_concepts     TEXT[],
    feedback             TEXT,
    answered_at           TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_topic_performance (
    id                      SERIAL PRIMARY KEY,
    user_id                 INTEGER NOT NULL REFERENCES users(id) ON 
DELETE CASCADE,
    topic                   VARCHAR(50) NOT NULL,
    rolling_average_score   NUMERIC(5,2) DEFAULT 0,
    attempt_count           INTEGER DEFAULT 0,
    last_attempted          TIMESTAMP,
    UNIQUE (user_id, topic)
);

CREATE TABLE session_summaries (
    id                  SERIAL PRIMARY KEY,
    session_id          INTEGER NOT NULL REFERENCES interview_sessions(id) 
ON DELETE CASCADE,
    topic_breakdown      JSONB,
    focus_recommendations TEXT[],
    created_at           TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_sessions_user_id ON interview_sessions(user_id);
CREATE INDEX idx_answers_session_id ON answers(session_id);
CREATE INDEX idx_topic_perf_user_id ON user_topic_performance(user_id);
