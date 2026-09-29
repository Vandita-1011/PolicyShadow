import { useEffect, useState } from "react";
import "./theme.css";
import { getHealth, getRuns, type HealthStatus, type RunSummary } from "./api";

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [runs, setRuns] = useState<RunSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch((e) => setError(String(e)));
    getRuns().then(setRuns).catch((e) => setError(String(e)));
  }, []);

  return (
    <div style={{ maxWidth: 640, margin: "3rem auto", padding: "0 1rem" }}>
      <h1>PolicyShadow</h1>
      <p style={{ color: "var(--color-text-muted)" }}>
        Connectivity check — this is not the real dashboard yet.
      </p>

      <div className="card">
        <h3>Backend health</h3>
        {error && <p style={{ color: "var(--risk-high)" }}>Error: {error}</p>}
        {!error && !health && <p>Loading...</p>}
        {health && <p>Status: {health.status}</p>}
      </div>

      <div className="card">
        <h3>Existing runs (real data from Postgres)</h3>
        {!error && runs === null && <p>Loading...</p>}
        {runs !== null && runs.length === 0 && <p>No runs yet.</p>}
        {runs !== null && runs.length > 0 && (
          <ul>
            {runs.map((r) => (
              <li key={r.run_id}>
                {r.run_id} — {r.status} — {r.total_records} records — {r.created_at}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
