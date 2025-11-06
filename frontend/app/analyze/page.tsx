"use client";
import { useState } from "react";
import { analyzeText, analyzeUpload } from "@/lib/api";

export default function AnalyzePage() {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState("en");
  const [numQuestions, setNumQuestions] = useState(5);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setError(null);
    setLoading(true);
    try {
      const data = file
        ? await analyzeUpload(file, language, numQuestions)
        : await analyzeText({ text, language, num_questions: numQuestions } as any);
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Analyze Educational Text</h2>
      <textarea
        className="w-full h-48 p-2 border rounded"
        placeholder="Paste your text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="flex items-center gap-4">
        <input type="file" accept=".pdf,.txt" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <select className="border p-2 rounded" value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="hi">Hindi</option>
          <option value="mr">Marathi</option>
        </select>
        <input
          type="number"
          min={1}
          max={15}
          className="w-24 border p-2 rounded"
          value={numQuestions}
          onChange={(e) => setNumQuestions(parseInt(e.target.value || "5", 10))}
        />
        <button className="px-4 py-2 bg-black text-white rounded" onClick={run} disabled={loading}>
          {loading ? "Processing..." : "Run Analysis"}
        </button>
      </div>
      {error && <div className="text-red-600">{error}</div>}
      {result && (
        <div className="grid md:grid-cols-2 gap-6">
          <section className="space-y-2">
            <h3 className="font-semibold">Readability Metrics</h3>
            <pre className="bg-white p-3 border rounded overflow-auto text-sm">{JSON.stringify(result.readability, null, 2)}</pre>
          </section>
          <section className="space-y-2">
            <h3 className="font-semibold">Glossary</h3>
            <div className="bg-white p-3 border rounded text-sm space-y-1">
              {Object.entries(result.glossary).map(([w, v]: any) => (
                <div key={w}>
                  <span className="font-medium">{w}</span> → {v.definition} — {v.translation}
                </div>
              ))}
            </div>
          </section>
          <section className="space-y-2 md:col-span-2">
            <h3 className="font-semibold">Generated Quiz Questions</n3>
            <div className="bg-white p-3 border rounded text-sm space-y-2">
              {result.quizzes.map((q: any, i: number) => (
                <div key={i}>
                  <div className="font-medium">Q{i + 1}. {q.question}</div>
                  {q.choices && (
                    <ul className="list-disc list-inside ml-4">
                      {q.choices.map((c: string, idx: number) => (
                        <li key={idx}>{c}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}


