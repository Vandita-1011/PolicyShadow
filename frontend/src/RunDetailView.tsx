import { useState } from "react";
import { Link } from "react-router-dom";
import { submitDecision, type Cluster } from "./api";
import { useRunPolling } from "./useRunPolling";
import { Accordion } from "./Accordion";
import { MarkdownContent } from "./MarkdownContent";

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
      <p style={{ margin: "0.6rem 0" }}>
        <strong>{rec.category}</strong>{" "}
        <span className="risk-badge" style={{ background: riskColor(rec.risk_level) }}>{rec.risk_level} risk</span>
      </p>
      <p style={{ color: "var(--color-text-muted)" }}>{rec.rationale}</p>

      <Accordion title="Explanation & remediation" defaultOpen>
        <MarkdownContent text={cluster.explanation} />
      </Accordion>

      <Accordion title={`Evidence (${cluster.evidence.length})`}>
        {cluster.evidence.map((e, i) => (
          <div key={i} className="evidence-item">
            <div className="evidence-source">{e.source}</div>
            <p style={{ fontSize: "0.9rem", margin: "0.3rem 0 0" }}>{e.text}</p>
          </div>
        ))}
      </Accordion>

      {rec.decision ? (
        <div className={`decision-panel ${rec.decision.decision === "approve" ? "approved" : "rejected"}`}>
          <strong style={{ textTransform: "capitalize" }}>{rec.decision.decision}</strong>
          <p style={{ fontSize: "0.85rem", margin: "0.3rem 0" }}>
            {new Date(rec.decision.decided_at).toLocaleString()}
            {rec.decision.note && ` — "${rec.decision.note}"`}
          </p>
          <p style={{ fontSize: "0.85rem", margin: 0 }}>
            {rec.decision.decision === "approve"
              ? "PolicyShadow does not modify your cluster automatically — apply this policy change manually when ready."
              : "No action will be taken on this policy."}
          </p>
        </div>
      ) : (
        <div style={{ marginTop: "1rem" }}>
          <input
            placeholder="Optional note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            style={{ marginRight: "0.5rem", padding: "0.5rem", border: "1px solid var(--color-border)", borderRadius: "3px" }}
          />
          <button className="btn-approve" onClick={() => decide("approve")} disabled={submitting}>Approve</button>{" "}
          <button className="btn-reject" onClick={() => decide("reject")} disabled={submitting}>Reject</button>
        </div>
      )}
    </div>
  );
}

export function RunDetailView({ runId, onBack }: { runId: string; onBack: () => void }) {
  const { run, error } = useRunPolling(runId);

  return (
    <div>
      <button className="btn-secondary" onClick={onBack} style={{ marginBottom: "1.25rem" }}>← Back to history</button>
      {error && <p style={{ color: "var(--risk-high)" }}>{error}</p>}
      {!run && !error && <p className="pulse">Loading...</p>}

      {run && (
        <div className="card">
          <h2 style={{ marginBottom: "0.2rem" }}>Run {run.run_id.slice(0, 8)}</h2>
          <span className={`status-pill status-${run.status}`}>{run.status}</span>
          <div className="summary-row">
            <div className="summary-item"><span className="label">Started</span><div className="value">{new Date(run.created_at).toLocaleString()}</div></div>
            <div className="summary-item"><span className="label">Records analyzed</span><div className="value">{run.total_records}</div></div>
            {run.status === "completed" && (
              <>
                <div className="summary-item"><span className="label">Violations</span><div className="value">{run.violation_count}</div></div>
                <div className="summary-item"><span className="label">Clusters</span><div className="value">{run.clusters.length}</div></div>
              </>
            )}
          </div>
        </div>
      )}

      {run && run.status === "running" && (
        <div className="card"><p className="pulse">Analysis running — this page will update automatically.</p></div>
      )}
      {run && run.status === "failed" && (
        <div className="card" style={{ borderLeft: "4px solid var(--risk-high)" }}>
          <p style={{ color: "var(--risk-high)" }}><strong>Run failed.</strong></p>
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>{run.error}</p>
        </div>
      )}
      {run && run.status === "completed" &&
        run.clusters.map((c) => <ClusterCard key={c.cluster_id} cluster={c} onDecided={() => window.location.reload()} />)}
    </div>
  );
}
