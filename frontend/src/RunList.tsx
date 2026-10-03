import { useEffect, useState } from "react";
import { getRuns, startAnalysis, type RunSummary } from "./api";

function statusPillClass(status: string): string {
  if (status === "completed") return "status-pill status-completed";
  if (status === "running") return "status-pill status-running";
  if (status === "failed") return "status-pill status-failed";
  return "status-pill";
}

export function RunList({ onSelect }: { onSelect: (runId: string) => void }) {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => getRuns().then(setRuns).catch((e) => setError(String(e)));

  useEffect(() => {
    refresh();
  }, []);

  const handleRunAnalysis = async () => {
    setStarting(true);
    setError(null);
    try {
      const result = await startAnalysis();
      const runId = result[0]?.run_id;
      await refresh();
      if (runId) onSelect(runId);
    } catch (e) {
      setError(String(e));
    } finally {
      setStarting(false);
    }
  };

  return (
    <div>
      <div className="card">
        <span className="label">Candidate policies</span>
        <h3 style={{ marginTop: "0.4rem" }}>
          restrict-privileged-containers &amp; require-non-root
        </h3>
        <p style={{ color: "var(--color-text-muted)" }}>
          Replays 30 historical workload records against both baseline
          security policies before any enforcement decision is made.
        </p>
        <button onClick={handleRunAnalysis} disabled={starting}>
          {starting ? "Running analysis..." : "Run Analysis"}
        </button>
        {starting && (
          <p className="pulse" style={{ color: "var(--color-text-muted)", marginTop: "0.75rem" }}>
            Replaying history, clustering violations, and generating
            explanations. This takes 1-3 minutes.
          </p>
        )}
        {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
      </div>

      <div className="card">
        <span className="label">Past runs</span>
        {runs.length === 0 ? (
          <div className="empty-state">
            <p>No runs yet. Run your first analysis above.</p>
          </div>
        ) : (
          <div style={{ marginTop: "0.5rem" }}>
            {runs.map((r) => (
              <div key={r.run_id} className="run-row" onClick={() => onSelect(r.run_id)}>
                <span>
                  {r.total_records} records — {new Date(r.created_at).toLocaleString()}
                </span>
                <span className={statusPillClass(r.status)}>{r.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
