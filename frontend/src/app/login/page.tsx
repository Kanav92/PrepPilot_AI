"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Terminal } from "lucide-react";
import api, { AuthResponse } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post<AuthResponse>("/auth/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user_name", res.data.name);
      localStorage.setItem("user_id", String(res.data.user_id));
      router.push("/resume");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-base)] text-[var(--text-primary)] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <Terminal size={20} className="text-[var(--accent-amber)]" />
          <span className="font-mono-display font-semibold">PrepPilot AI</span>
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-8">
          <h1 className="font-mono-display text-lg font-medium mb-1">Welcome back</h1>
          <p className="text-sm text-[var(--text-muted)] mb-6">Log in to continue your prep.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs text-[var(--text-muted)] mb-1.5">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[var(--bg-base)] border border-[var(--border-subtle)] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[var(--accent-amber)] transition-colors"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="block text-xs text-[var(--text-muted)] mb-1.5">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[var(--bg-base)] border border-[var(--border-subtle)] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[var(--accent-amber)] transition-colors"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="text-sm text-[var(--accent-weak)] bg-[var(--accent-weak)]/10 border border-[var(--accent-weak)]/30 rounded-md px-3 py-2">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[var(--accent-amber)] text-[var(--bg-base)] py-2.5 rounded-md font-medium text-sm hover:bg-[var(--accent-amber-dim)] transition-colors disabled:opacity-50"
            >
              {loading ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className="text-sm text-[var(--text-muted)] text-center mt-6">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-[var(--accent-amber)] hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
