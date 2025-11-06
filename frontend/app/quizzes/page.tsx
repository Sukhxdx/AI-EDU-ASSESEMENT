"use client";
import { useEffect, useState } from "react";
import { listSessions, loadSession } from "@/lib/api";

export default function QuizzesPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loaded, setLoaded] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setSessions(await listSessions());
      } catch (e: any) {
        setError(e.message);
      }
    })();
  }, []);

  const load = async (id: number) => {
    setError(null);
    setLoaded(null);
    try {
      setLoaded(await loadSession(id));
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Saved Quiz Sessions</h2>
      {error && <div className="text-red-600">{error}</div>}
      {!sessions.length ? (
        <div>No previous sessions found.</div>
      ) : (
        <div className="space-y-2">
          {sessions.map((s) => (
            <div key={s.id} className="flex items-center justify-between bg-white p-3 border rounded">
              <div>
                <div className="font-medium">Session {s.id}</div>
                <div className="text-xs text-gray-500">{s.created_at}</div>
              </div>
              <button className="px-3 py-1 bg-black text-white rounded" onClick={() => load(s.id)}>Load</button>
            </div>
          ))}
        </div>
      )}
      {loaded && (
        <div className="space-y-2">
          <h3 className="font-semibold">Session {loaded.id}</h3>
          <pre className="bg-white p-3 border rounded overflow-auto text-sm">{JSON.stringify(loaded, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}


