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

      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}

      <div className="card" style={{ padding: 0 }}>
        <div className="history-scroll">
          <div
            className="history-row-grid"
            style={{ padding: "0.75rem 1.25rem", borderBottom: "1px solid var(--border-color)" }}
          >
            <span className="label">Policies</span>
            <span className="label">Status</span>
            <span className="label">Violations / Clusters</span>
            <span className="label">Records</span>
            <span className="label">Decision</span>
            <span className="label">Date</span>
            <span />
          </div>

          {filtered.length === 0 ? (
            <div className="empty-state-compact"><p>No matching runs.</p></div>
          ) : (
            filtered.map((r) => (
              <div
                key={r.run_id}
                className="history-row-grid"
                style={{ padding: "1rem 1.25rem", borderBottom: "1px solid var(--border-color)" }}
              >
                <span className="truncate" title={r.policy_names.join(" + ")}>
                  <strong>{r.policy_names.join(" + ")}</strong>
                </span>
                <span className={`status-pill status-${r.status}`}>{r.status}</span>
                <span>{r.violation_count} / {r.cluster_count}</span>
                <span>{r.total_records}</span>
                <span className="truncate">{r.decision_summary}</span>
                <span className="truncate" style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                  {new Date(r.created_at).toLocaleDateString()}
                </span>
                <Link to={`/runs/${r.run_id}`}><button className="btn-secondary">View</button></Link>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
