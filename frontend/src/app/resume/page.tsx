"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Terminal, Upload, FileText, ArrowRight, LogOut, CheckCircle2 } from "lucide-react";
import api, { ResumeData } from "@/lib/api";

export default function ResumePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ResumeData | null>(null);
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
    setUserName(localStorage.getItem("user_name") || "");
  }, [router]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (!selected.name.toLowerCase().endsWith(".pdf")) {
        setError("Only PDF files are supported.");
        return;
      }
      setFile(selected);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post<ResumeData>("/resume/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      localStorage.setItem("resume_id", String(res.data.resume_id));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed. Try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    router.push("/login");
  };

  return (
    <div className="h-screen bg-[var(--bg-base)] bg-grain text-[var(--text-primary)] flex flex-col overflow-hidden">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-[var(--border-subtle)] shrink-0">
        <div className="flex items-center gap-2">
          <Terminal size={20} className="text-[var(--accent-amber)]" />
          <span className="font-mono-display font-semibold tracking-tight">PrepPilot AI</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-[var(--text-muted)]">{userName}</span>
          <button onClick={handleLogout} className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
            <LogOut size={18} />
          </button>
        </div>
      </nav>

      <div className="flex-1 overflow-hidden flex flex-col max-w-2xl mx-auto w-full px-8 py-6">
        <div className="shrink-0">
          <div className="font-mono-display text-xs text-[var(--accent-amber)] tracking-widest uppercase mb-2">
            Step 1 of 2
          </div>
          <h1 className="font-mono-display text-2xl font-semibold mb-1">Upload your resume</h1>
          <p className="text-[var(--text-muted)] text-sm mb-5 leading-relaxed">
            We&apos;ll extract your skills and projects so the interview can ask you about real things you&apos;ve built.
          </p>
        </div>

        {!result ? (
          <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-8 animate-fade-up">
            <label
              htmlFor="resume-upload"
              className="flex flex-col items-center justify-center gap-3 border-2 border-dashed border-[var(--border-subtle)] rounded-lg py-14 cursor-pointer hover:border-[var(--accent-amber)] hover:bg-[var(--accent-amber)]/[0.03] transition-all"
            >
              {file ? (
                <>
                  <FileText size={32} className="text-[var(--accent-amber)]" />
                  <span className="text-sm font-medium">{file.name}</span>
                  <span className="text-xs text-[var(--text-muted)]">Click to change</span>
                </>
              ) : (
                <>
                  <Upload size={32} className="text-[var(--text-muted)]" />
                  <span className="text-sm text-[var(--text-muted)]">Click to choose a PDF</span>
                </>
              )}
              <input id="resume-upload" type="file" accept=".pdf" onChange={handleFileChange} className="hidden" />
            </label>

            {error && (
              <div className="mt-4 text-sm text-[var(--accent-weak)] bg-[var(--accent-weak)]/10 border border-[var(--accent-weak)]/30 rounded-md px-3 py-2">
                {error}
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full mt-6 flex items-center justify-center gap-2 bg-[var(--accent-amber)] text-[var(--bg-base)] py-3 rounded-md font-medium text-sm hover:bg-[var(--accent-amber-dim)] hover:glow-amber transition-all disabled:opacity-40"
            >
              {uploading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-[var(--bg-base)] border-t-transparent rounded-full animate-spin" />
                  Analyzing resume...
                </>
              ) : (
                "Upload & analyze"
              )}
            </button>
          </div>
        ) : (
          <div className="flex-1 overflow-hidden flex flex-col bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg glow-strong animate-fade-up">
            <div className="px-6 pt-6 shrink-0 flex items-center gap-2 text-[var(--accent-strong)] text-sm font-medium">
              <CheckCircle2 size={18} />
              Resume analyzed successfully
            </div>

            {/* Scrollable inner content — page itself never scrolls */}
            <div className="flex-1 overflow-y-auto px-6 py-5">
              <div className="mb-6">
                <div className="text-xs text-[var(--text-muted)] uppercase tracking-widest mb-3 font-medium">
                  Skills detected ({result.parsed_data.skills.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.parsed_data.skills.map((s, i) => (
                    <span
                      key={i}
                      className="text-xs bg-[var(--bg-base)] border border-[var(--border-subtle)] rounded px-2.5 py-1.5"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-xs text-[var(--text-muted)] uppercase tracking-widest mb-3 font-medium">
                  Projects found ({result.parsed_data.projects.length})
                </div>
                <div className="space-y-3">
                  {result.parsed_data.projects.map((p, i) => (
                    <div key={i} className="bg-[var(--bg-base)] border border-[var(--border-subtle)] rounded-md p-3.5">
                      <div className="font-medium text-sm mb-1">{p.name}</div>
                      <div className="text-[var(--text-muted)] text-xs leading-relaxed">{p.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* CTA always inside the card, always visible */}
            <div className="shrink-0 p-6 pt-4 border-t border-[var(--border-subtle)]">
              <button
                onClick={() => router.push("/interview")}
                className="group w-full flex items-center justify-center gap-2 bg-[var(--accent-amber)] text-[var(--bg-base)] py-3 rounded-md font-medium text-sm hover:bg-[var(--accent-amber-dim)] hover:glow-amber transition-all"
              >
                Start the interview
                <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
