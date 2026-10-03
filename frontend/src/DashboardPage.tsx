import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getStats, getRuns, type Stats, type RunListItem } from "./api";

export function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentRuns, setRecentRuns] = useState<RunListItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStats().then(setStats).catch((e) => setError(String(e)));
    getRuns().then((r) => setRecentRuns(r.slice(0, 6))).catch((e) => setError(String(e)));
  }, []);

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">Overview of policy rollout analysis and decisions</p>

      <div className="hero-banner">
        <h2>Safe Kubernetes policy rollout, backed by evidence</h2>
        <p>
          PolicyShadow replays candidate admission policies against historical
          workload data, clusters the resulting violations, and generates
          grounded explanations and rollout guidance — before anything is
          enforced, and always with a human making the final call.
        </p>
        <div style={{ marginTop: "1.1rem" }}>
          <Link to="/policies">
            <button style={{ background: "white", color: "var(--color-accent)" }}>Run Analysis</button>
          </Link>{" "}
          <Link to="/policies">
            <button className="btn-secondary" style={{ borderColor: "white", color: "white" }}>
              View Policies
            </button>
          </Link>
        </div>
      </div>

      {error && <p style={{ color: "var(--risk-high)" }}>{error}</p>}

      {stats && (
        <div className="stat-grid">
          <div className="card" style={{ textAlign: "center" }}>
            <div className="stat-value">{stats.total_runs}</div>
            <div className="label">Total runs</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div className="stat-value">{stats.total_policies}</div>
            <div className="label">Policies</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div className="stat-value">{stats.total_violations_detected}</div>
            <div className="label">Violations detected</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div className="stat-value">{stats.pending_decisions}</div>
            <div className="label">Pending decisions</div>
          </div>
        </div>
      )}

      <div className="two-col">
        <div className="card">
          <span className="label">Recent activity</span>
          {recentRuns.length === 0 ? (
            <div className="empty-state-compact">
              <p>No runs yet.</p>
              <Link to="/policies"><button style={{ marginTop: "0.5rem" }}>Run your first analysis</button></Link>
            </div>
          ) : (
            recentRuns.map((r) => (
              <div key={r.run_id} className="run-row">
                <div>
                  <strong>{r.policy_names.join(" + ")}</strong>
                  <div style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
                    {r.violation_count} violations — {new Date(r.created_at).toLocaleDateString()}
                  </div>
                </div>
                <Link to={`/runs/${r.run_id}`}><button className="btn-secondary">View Details</button></Link>
              </div>
            ))
          )}
        </div>

        <div className="card">
          <span className="label">How it works</span>
          <ol className="how-it-works" style={{ marginTop: "0.75rem" }}>
            <li>Replay historical workloads against a candidate policy</li>
            <li>Cluster the resulting violations by meaning</li>
            <li>Retrieve grounded knowledge and generate an explanation</li>
            <li>Review the rollout recommendation and approve or reject</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
