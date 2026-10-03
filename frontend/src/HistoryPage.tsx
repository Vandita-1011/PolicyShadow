import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getRuns, type RunListItem } from "./api";

export function HistoryPage() {
  const [runs, setRuns] = useState<RunListItem[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getRuns().then(setRuns).catch((e) => setError(String(e)));
  }, []);

  const filtered = runs.filter((r) => {
    const q = search.toLowerCase();
    return (
      r.policy_names.join(" ").toLowerCase().includes(q) ||
      r.run_id.toLowerCase().includes(q) ||
      r.status.toLowerCase().includes(q)
    );
  });

  return (
    <div>
      <h1 className="page-title">History</h1>
      <p className="page-subtitle">All past analysis runs</p>

      <input
        className="search-input"
        placeholder="Search runs or policies..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {error && <p style={{ color: "var(--risk-high)" }}>{error}</p>}

      <div className="card" style={{ padding: 0 }}>
        {filtered.length === 0 ? (
          <div className="empty-state-compact"><p>No matching runs.</p></div>
        ) : (
          filtered.map((r) => (
            <div key={r.run_id} className="run-row" style={{ padding: "1rem 1.25rem" }}>
              <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr", gap: "1rem", flex: 1, alignItems: "center" }}>
                <div>
                  <strong>{r.policy_names.join(" + ")}</strong>
                  <div style={{ color: "var(--color-text-muted)", fontSize: "0.8rem" }}>
                    {new Date(r.created_at).toLocaleString()}
                  </div>
                </div>
                <span className={`status-pill status-${r.status}`}>{r.status}</span>
                <span>{r.violation_count} violations / {r.cluster_count} clusters</span>
                <span>{r.total_records} records</span>
                <span>{r.decision_summary}</span>
              </div>
              <Link to={`/runs/${r.run_id}`}><button className="btn-secondary">View Details</button></Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
