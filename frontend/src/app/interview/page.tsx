"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Terminal, Send } from "lucide-react";
import api, { Question, AnswerResponse, StartInterviewResponse } from "@/lib/api";

interface TraceEntry {
  agent: string;
  detail: string;
}

export default function InterviewPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(10);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [lastScore, setLastScore] = useState<{ score: number; feedback: string } | null>(null);
  const [trace, setTrace] = useState<TraceEntry[]>([]);
  const [error, setError] = useState("");
  const [questionKey, setQuestionKey] = useState(0);
  const [runningAvg, setRunningAvg] = useState<number[]>([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const resumeId = localStorage.getItem("resume_id");
    if (!token) { router.push("/login"); return; }
    if (!resumeId) { router.push("/resume"); return; }
    startInterview(Number(resumeId));
  }, [router]);

  const addTrace = (agent: string, detail: string) => {
    setTrace((prev) => [...prev.slice(-7), { agent, detail }]);
  };

  const startInterview = async (resumeId: number) => {
    setLoading(true);
    addTrace("resume_analyzer", "loading parsed resume data");
    try {
      const res = await api.post<StartInterviewResponse>(`/interview/start?resume_id=${resumeId}`);
      setSessionId(res.data.session_id);
      setQuestion(res.data.question);
      setQuestionNumber(res.data.question_number);
      setTotalQuestions(res.data.total_questions);
      addTrace("interview_agent", `fetch_question_from_bank(${res.data.question.topic}, ${res.data.question.difficulty})`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not start interview.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!answer.trim() || !sessionId) return;
    setSubmitting(true);
    setError("");
    addTrace("evaluation_agent", "retrieve_concept_reference + scoring");

    try {
      const res = await api.post<AnswerResponse>("/interview/answer", {
        session_id: sessionId,
        answer_text: answer,
      });

      setLastScore({ score: res.data.last_score.score, feedback: res.data.last_score.feedback });
      setRunningAvg((prev) => [...prev, res.data.last_score.score]);
      addTrace("evaluation_agent", `score: ${res.data.last_score.score}/100`);

      if (res.data.interview_complete) {
        addTrace("planner_agent", "generating personalized roadmap");
        localStorage.setItem("last_session_id", String(sessionId));
        setTimeout(() => router.push(`/results?session_id=${sessionId}`), 2000);
      } else {
        setTimeout(() => {
          setQuestion(res.data.question!);
          setQuestionNumber(res.data.question_number!);
          setAnswer("");
          setLastScore(null);
          setQuestionKey((k) => k + 1);
          if (res.data.question) {
            addTrace("interview_agent", `next: ${res.data.question.topic} (${res.data.question.difficulty})`);
          }
        }, 2000);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not submit answer.");
    } finally {
      setSubmitting(false);
    }
  };

  const scoreColor = (score: number) =>
    score >= 70 ? "var(--accent-strong)" : score >= 40 ? "var(--accent-amber)" : "var(--accent-weak)";
  const scoreGlow = (score: number) =>
    score >= 70 ? "glow-strong" : score >= 40 ? "glow-amber" : "glow-weak";

  const liveAvg = runningAvg.length ? Math.round(runningAvg.reduce((a, b) => a + b, 0) / runningAvg.length) : null;

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)] bg-grain text-[var(--text-primary)] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-[var(--border-subtle)] border-t-[var(--accent-amber)] rounded-full animate-spin" />
          <div className="font-mono-display text-[var(--accent-amber)] text-sm">Initializing interview session...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--bg-base)] bg-grain text-[var(--text-primary)] flex flex-col">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-[var(--border-subtle)] shrink-0">
        <div className="flex items-center gap-2">
          <Terminal size={18} className="text-[var(--accent-amber)]" />
          <span className="font-mono-display font-semibold tracking-tight text-sm">PrepPilot AI</span>
        </div>
        <div className="flex items-center gap-6">
          {liveAvg !== null && (
            <div className="font-mono-display text-sm flex items-center gap-2">
              <span className="text-[var(--text-muted)]">avg</span>
              <span style={{ color: scoreColor(liveAvg) }} className="font-semibold">{liveAvg}</span>
            </div>
          )}
          <div className="font-mono-display text-sm text-[var(--text-muted)]">
            <span className="text-[var(--accent-amber)]">{questionNumber}</span> / {totalQuestions}
          </div>
        </div>
      </nav>

      <div className="h-[3px] bg-[var(--border-subtle)] w-full shrink-0">
        <div
          className="h-[3px] bg-[var(--accent-amber)] progress-glow transition-all duration-700 ease-out"
          style={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
        />
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_360px] overflow-hidden">
        {/* LEFT: Question + answer */}
        <div className="overflow-y-auto px-10 py-10 lg:px-14">
          {question && (
            <div key={questionKey} className="animate-fade-up max-w-2xl">
              <div className="flex items-center gap-3 mb-5">
                <span className="text-xs font-mono-display font-semibold bg-[var(--accent-amber)]/10 border border-[var(--accent-amber)]/40 rounded px-2.5 py-1 text-[var(--accent-amber)]">
                  {question.topic}
                </span>
                <span className="text-xs font-mono-display text-[var(--text-muted)] uppercase tracking-wider border border-[var(--border-subtle)] rounded px-2.5 py-1">
                  {question.difficulty}
                </span>
              </div>

              <h1 className="text-[28px] font-medium leading-[1.3] mb-8 text-[var(--text-primary)]">
                {question.question_text}
              </h1>

              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                disabled={submitting || !!lastScore}
                placeholder="Type your answer here..."
                rows={9}
                className="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-4 py-3.5 text-sm leading-relaxed focus:outline-none focus:border-[var(--accent-amber)] focus:glow-amber transition-all resize-none disabled:opacity-60"
              />

              {error && (
                <div className="mt-4 text-sm text-[var(--accent-weak)] bg-[var(--accent-weak)]/10 border border-[var(--accent-weak)]/30 rounded-md px-3 py-2">
                  {error}
                </div>
              )}

              {lastScore ? (
                <div className={`mt-6 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-6 animate-score-reveal ${scoreGlow(lastScore.score)}`}>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-[var(--text-muted)] uppercase tracking-widest font-medium">Score</span>
                    <span className="font-mono-display text-4xl font-semibold" style={{ color: scoreColor(lastScore.score) }}>
                      {lastScore.score}<span className="text-lg text-[var(--text-muted)]">/100</span>
                    </span>
                  </div>
                  <p className="text-sm text-[var(--text-muted)] leading-relaxed">{lastScore.feedback}</p>
                </div>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={!answer.trim() || submitting}
                  className="group mt-6 flex items-center gap-2 bg-[var(--accent-amber)] text-[var(--bg-base)] px-6 py-3 rounded-md font-medium text-sm hover:bg-[var(--accent-amber-dim)] hover:glow-amber transition-all disabled:opacity-40 disabled:hover:shadow-none"
                >
                  {submitting ? (
                    <>
                      <span className="w-3.5 h-3.5 border-2 border-[var(--bg-base)] border-t-transparent rounded-full animate-spin" />
                      Evaluating...
                    </>
                  ) : (
                    <>
                      Submit answer
                      <Send size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                    </>
                  )}
                </button>
              )}
            </div>
          )}
        </div>

        {/* RIGHT: Persistent agent trace sidebar */}
        <div className="border-t lg:border-t-0 lg:border-l border-[var(--border-subtle)] bg-[var(--bg-card)] px-6 py-8 overflow-y-auto">
          <div className="flex items-center gap-2 mb-6 text-[var(--text-muted)] uppercase tracking-widest text-xs font-mono-display">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-strong)] animate-pulse" />
            Live agent trace
          </div>
          <div className="space-y-3 font-mono-display text-xs">
            {trace.map((t, i) => (
              <div key={i} className="animate-trace-in border-l-2 border-[var(--border-subtle)] pl-3 py-0.5">
                <div className="text-[var(--accent-amber)] font-medium">{t.agent}</div>
                <div className="text-[var(--text-muted)] mt-0.5 break-words">{t.detail}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
