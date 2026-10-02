import { useState } from "react";
import { submitDecision, type Cluster } from "./api";
import { useRunPolling } from "./useRunPolling";

function riskColor(level: string): string {
  if (level === "Low") return "var(--risk-low)";
  if (level === "High") return "var(--risk-high)";
  return "var(--risk-medium)";
}

function ClusterCard({ cluster, onDecided }: { cluster: Cluster; onDecided: () => void }) {
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const rec = cluster.recommendation;

  const decide = async (decision: "approve" | "reject") => {
    setSubmitting(true);
    try {
      await submitDecision(rec.recommendation_id, decision, note);
      onDecided();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={`card cluster-card risk-${rec.risk_level}`}>
      <span className="label">{cluster.rule_name}</span>
      <h3 style={{ marginTop: "0.3rem" }}>{cluster.violation_count} affected workloads</h3>

      <p style={{ margin: "0.75rem 0" }}>
        <strong>{rec.category}</strong>{" "}
        <span className="risk-badge" style={{ background: riskColor(rec.risk_level) }}>
          {rec.risk_level} risk
        </span>
      </p>
      <p style={{ color: "var(--color-text-muted)" }}>{rec.rationale}</p>

      <details>
        <summary>Explanation</summary>
        <p style={{ whiteSpace: "pre-wrap" }}>{cluster.explanation}</p>
      </details>

      <details>
        <summary>Evidence ({cluster.evidence.length})</summary>
        {cluster.evidence.map((e, i) => (
          <div
            key={i}
            style={{
              marginTop: "0.5rem",
              paddingLeft: "0.5rem",
              borderLeft: "2px solid var(--color-border)",
            }}
          >
            <strong style={{ fontSize: "0.85rem" }}>{e.source}</strong>
            <p style={{ fontSize: "0.92rem" }}>{e.text}</p>
          </div>
        ))}
      </details>

      {rec.decision ? (
        <div style={{ marginTop: "1rem" }}>
          <p>
            <span
              className={`status-pill status-${rec.decision.decision === "approve" ? "completed" : "failed"}`}
            >
              {rec.decision.decision}
            </span>{" "}
            <span style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
              {new Date(rec.decision.decided_at).toLocaleString()}
              {rec.decision.note && ` — "${rec.decision.note}"`}
            </span>
          </p>
          <p className="enforcement-note">
            {rec.decision.decision === "approve"
              ? "Approved. PolicyShadow does not modify your cluster automatically — apply this policy change manually when ready."
              : "Rejected. No action will be taken on this policy."}
          </p>
        </div>
      ) : (
        <div style={{ marginTop: "1rem" }}>
          <input
            placeholder="Optional note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            style={{
              marginRight: "0.5rem",
              padding: "0.5rem",
              border: "1px solid var(--color-border)",
              borderRadius: "3px",
            }}
          />
          <button className="btn-approve" onClick={() => decide("approve")} disabled={submitting}>
            Approve
          </button>{" "}
          <button className="btn-reject" onClick={() => decide("reject")} disabled={submitting}>
            Reject
          </button>
        </div>
      )}
    </div>
  );
}

export function RunDetailView({ runId, onBack }: { runId: string; onBack: () => void }) {
  const { run, error } = useRunPolling(runId);

  return (
    <div>
      <button className="btn-secondary" onClick={onBack} style={{ marginBottom: "1.5rem" }}>
        ← Back to runs
      </button>
      {error && <p style={{ color: "var(--risk-high)" }}>{error}</p>}
      {!run && !error && <p className="pulse">Loading...</p>}
      {run && run.status === "running" && (
        <div className="card">
          <p className="pulse">Analysis running — this page will update automatically.</p>
        </div>
      )}
      {run && run.status === "failed" && (
        <div className="card" style={{ borderLeft: "4px solid var(--risk-high)" }}>
          <p style={{ color: "var(--risk-high)" }}>
            <strong>Run failed.</strong>
          </p>
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>{run.error}</p>
        </div>
      )}
      {run && run.status === "completed" && (
        <>
          <p style={{ color: "var(--color-text-muted)" }}>
            {run.violation_count} violations across {run.clusters.length} clusters — out of{" "}
            {run.total_records} historical records
          </p>
          {run.clusters.map((c) => (
            <ClusterCard key={c.cluster_id} cluster={c} onDecided={() => window.location.reload()} />
          ))}
        </>
      )}
    </div>
  );
}
