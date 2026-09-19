import type { AnalysisResult, CaseSummary, ValidationReport } from "./types";

// Vite proxies /api -> http://localhost:8000 (see vite.config.ts).
const BASE = "/api";

const SESSION_ID = localStorage.getItem("session_id") ?? crypto.randomUUID();
localStorage.setItem("session_id", SESSION_ID);

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* not json */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export async function analyze(file: File): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("file", file);
  return handle(
    await fetch(`${BASE}/analyze`, {
      method: "POST",
      headers: { "X-Session-Id": SESSION_ID },
      body: form,
    })
  );
}

export async function getCases(): Promise<CaseSummary[]> {
  return handle(await fetch(`${BASE}/cases`, { headers: { "X-Session-Id": SESSION_ID } }));
}

export async function getCase(caseId: string): Promise<AnalysisResult> {
  return handle(await fetch(`${BASE}/cases/${caseId}`));
}

export async function getValidation(): Promise<ValidationReport> {
  return handle(await fetch(`${BASE}/validation`));
}