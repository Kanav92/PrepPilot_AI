"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Terminal, TrendingUp, TrendingDown, RotateCcw } from "lucide-react";
import api from "@/lib/api";

interface SessionResults {
  session: { id: number; status: string; started_at: string; completed_at: string };
  summary: { topic_breakdown: Record<string, number>; focus_recommendations: string[] } | null;
  answers: { question_text: string; topic: string; score: number; missing_concepts: string[]; feedback: string }[];
}

function ResultsContent() {
  const params = useSearchParams();
  const router = useRouter();
  const sessionId = params.get("session_id") || localStorage.getItem("last_session_id");
  const [results, setResults] = useState<SessionResults | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) {
      router.push("/resume");
      return;
    }
    api
      .get<SessionResults>(`/interview/results/${sessionId}`)
      .then((res) => setResults(res.data))
      .catch(() => router.push("/resume"))
      .finally(() => setLoading(false));
  }, [sessionId, router]);

  if (loading || !results) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)] text-[var(--text-primary)] flex items-center justify-center">
        <div className="font-mono-display text-[var(--accent-amber)] text-sm animate-pulse">Loading results...</div>
      </div>
    );
  }

  const breakdown = results.summary?.topic_breakdown || {};
  const recommendations = results.summary?.focus_recommendations || [];
  const overallAvg = Object.values(breakdown).length
    ? Math.round(Object.values(breakdown).reduce((a, b) => a + b, 0) / Object.values(breakdown).length)
    : 0;

  const scoreColor = (score: number) =>
    score >= 70 ? "var(--accent-strong)" : score >= 40 ? "var(--accent-amber)" : "var(--accent-weak)";

  return (
    <div className="min-h-screen bg-[var(--bg-base)] text-[var(--text-primary)]">
      <nav className="flex items-center justify-between px-8 py-6 border-b border-[var(--border-subtle)]">
        <div className="flex items-center gap-2">
          <Terminal size={20} className="text-[var(--accent-amber)]" />
          <span className="font-mono-display font-semibold tracking-tight">PrepPilot AI</span>
        </div>
        <button
          onClick={() => router.push("/resume")}
          className="flex items-center gap-2 text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
        >
          <RotateCcw size={14} />
          New session
        </button>
      </nav>

      <div className="max-w-4xl mx-auto px-8 py-12">
        <div className="font-mono-display text-xs text-[var(--accent-amber)] tracking-widest uppercase mb-3">
          Session complete
        </div>
        <h1 className="font-mono-display text-3xl font-semibold mb-10">Your results</h1>

        {/* Overall score */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-8 mb-8 flex items-center justify-between">
          <div>
            <div className="text-xs text-[var(--text-muted)] uppercase tracking-widest mb-2">Overall score</div>
            <div className="font-mono-display text-5xl font-semibold" style={{ color: scoreColor(overallAvg) }}>
              {overallAvg}
              <span className="text-xl text-[var(--text-muted)]">/100</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-x-8 gap-y-3">
            {Object.entries(breakdown).map(([topic, score]) => (
              <div key={topic} className="flex items-center gap-2 text-sm">
                {score >= 60 ? (
                  <TrendingUp size={14} style={{ color: "var(--accent-strong)" }} />
                ) : (
                  <TrendingDown size={14} style={{ color: "var(--accent-weak)" }} />
                )}
                <span className="text-[var(--text-muted)] w-16">{topic}</span>
                <span className="font-mono-display font-medium" style={{ color: scoreColor(score) }}>
                  {score}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-8 mb-8">
          <div className="text-xs text-[var(--text-muted)] uppercase tracking-widest mb-4">
            Planner agent recommendations
          </div>
          <ul className="space-y-3">
            {recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-3 text-sm">
                <span className="text-[var(--accent-amber)] font-mono-display mt-0.5">→</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Per-question breakdown */}
        <div className="space-y-4">
          <div className="text-xs text-[var(--text-muted)] uppercase tracking-widest mb-2">Question by question</div>
          {results.answers.map((a, i) => (
            <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono-display bg-[var(--bg-base)] border border-[var(--border-subtle)] rounded px-2 py-1 text-[var(--accent-amber)]">
                  {a.topic}
                </span>
                <span className="font-mono-display font-semibold" style={{ color: scoreColor(a.score) }}>
                  {a.score}/100
                </span>
              </div>
              <p className="text-sm mb-2">{a.question_text}</p>
              <p className="text-xs text-[var(--text-muted)]">{a.feedback}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[var(--bg-base)]" />}>
      <ResultsContent />
    </Suspense>
  );
}
