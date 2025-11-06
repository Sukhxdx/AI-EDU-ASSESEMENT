const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function analyzeText(payload: { text: string; language: string; num_questions: number }) {
  const res = await fetch(`${BACKEND_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function analyzeUpload(file: File, language: string, numQuestions: number) {
  const form = new FormData();
  form.append("file", file);
  form.append("language", language);
  form.append("num_questions", String(numQuestions));
  const res = await fetch(`${BACKEND_URL}/analyze/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listSessions() {
  const res = await fetch(`${BACKEND_URL}/sessions`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function loadSession(id: number) {
  const res = await fetch(`${BACKEND_URL}/sessions/${id}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}


