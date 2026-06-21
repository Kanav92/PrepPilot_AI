"use client";

import Link from "next/link";
import { ArrowRight, Terminal, Brain, TrendingUp } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--bg-base)] text-[var(--text-primary)]">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-6 border-b border-[var(--border-subtle)]">
        <div className="flex items-center gap-2">
          <Terminal size={20} className="text-[var(--accent-amber)]" />
          <span className="font-mono-display font-semibold tracking-tight">PrepPilot AI</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
            Log in
          </Link>
          <Link
            href="/signup"
            className="text-sm bg-[var(--accent-amber)] text-[var(--bg-base)] px-4 py-2 rounded-md font-medium hover:bg-[var(--accent-amber-dim)] transition-colors"
          >
            Get started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="px-8 pt-24 pb-20 max-w-5xl mx-auto">
        <div className="font-mono-display text-xs text-[var(--accent-amber)] tracking-widest uppercase mb-6">
          $ initializing interview session...
        </div>
        <h1 className="font-mono-display text-5xl md:text-6xl font-semibold tracking-tight leading-[1.1] mb-6">
          Four AI agents.<br />
          One adaptive interview.
        </h1>
        <p className="text-lg text-[var(--text-muted)] max-w-2xl mb-10 leading-relaxed">
          PrepPilot reads your resume, runs a live adaptive mock interview across DSA, DBMS, OS, CN, and your actual projects —
          then builds a study plan from what it learns about you, every single session.
        </p>
        <div className="flex items-center gap-4">
          <Link
            href="/signup"
            className="group flex items-center gap-2 bg-[var(--accent-amber)] text-[var(--bg-base)] px-6 py-3 rounded-md font-medium hover:bg-[var(--accent-amber-dim)] transition-colors"
          >
            Start a mock interview
            <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
          </Link>
          <Link
            href="/login"
            className="text-[var(--text-muted)] hover:text-[var(--text-primary)] px-6 py-3 transition-colors"
          >
            I already have an account
          </Link>
        </div>
      </section>

      {/* Agent trace preview — signature element teaser */}
      <section className="px-8 pb-24 max-w-5xl mx-auto">
        <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-6 font-mono-display text-sm">
          <div className="flex items-center gap-2 mb-4 text-[var(--text-muted)] text-xs uppercase tracking-widest">
            <span className="w-2 h-2 rounded-full bg-[var(--accent-strong)] animate-pulse" />
            Live agent trace
          </div>
          <div className="space-y-2 text-[var(--text-muted)]">
            <div><span className="text-[var(--accent-amber)]">resume_analyzer</span> → extracted 9 skills, 2 projects</div>
            <div><span className="text-[var(--accent-amber)]">interview_agent</span> → fetch_question_from_bank(topic=&quot;DSA&quot;, difficulty=&quot;medium&quot;)</div>
            <div><span className="text-[var(--accent-amber)]">evaluation_agent</span> → score: 80/100, missing: collision resolution</div>
            <div><span className="text-[var(--accent-amber)]">planner_agent</span> → fetch_long_term_performance(user_id) → 3 weak topics found</div>
          </div>
        </div>
      </section>

      {/* Feature grid */}
      <section className="px-8 pb-24 max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="border border-[var(--border-subtle)] rounded-lg p-6">
          <Brain size={20} className="text-[var(--accent-amber)] mb-4" />
          <h3 className="font-mono-display font-medium mb-2">Adaptive by design</h3>
          <p className="text-sm text-[var(--text-muted)] leading-relaxed">
            Difficulty shifts in real time based on how you answer. Weak on a topic? You get a followup, not a new question.
          </p>
        </div>
        <div className="border border-[var(--border-subtle)] rounded-lg p-6">
          <Terminal size={20} className="text-[var(--accent-amber)] mb-4" />
          <h3 className="font-mono-display font-medium mb-2">Built on your resume</h3>
          <p className="text-sm text-[var(--text-muted)] leading-relaxed">
            Real questions about your real projects — not generic prompts pulled from a static bank.
          </p>
        </div>
        <div className="border border-[var(--border-subtle)] rounded-lg p-6">
          <TrendingUp size={20} className="text-[var(--accent-amber)] mb-4" />
          <h3 className="font-mono-display font-medium mb-2">Remembers your history</h3>
          <p className="text-sm text-[var(--text-muted)] leading-relaxed">
            Every session updates your long-term topic performance, so your study plan gets sharper over time.
          </p>
        </div>
      </section>
    </div>
  );
}
