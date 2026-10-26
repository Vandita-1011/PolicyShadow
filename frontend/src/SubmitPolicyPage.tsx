import { useState } from "react";
import { Link } from "react-router-dom";
import { validatePolicy, submitPolicy, startAnalysis, getRuns } from "./api";
import { useRunPolling } from "./useRunPolling";

export function SubmitPolicyPage() {
  const [name, setName] = useState("");
  const [yaml, setYaml] = useState("");
  const [validation, setValidation] = useState<{ valid: boolean; error: string | null } | null>(null);
  const [busy, setBusy] = useState(false);
  const [submittedRunId, setSubmittedRunId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { run, error: pollError } = useRunPolling(submittedRunId);

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    file.text().then((text) => {
      setYaml(text);
      setValidation(null);
      setSubmittedRunId(null);
      setSubmitError(null);
    });
  };

  const onValidate = async () => {
    setBusy(true);
    try {
      setValidation(await validatePolicy(yaml));
    } finally {
      setBusy(false);
    }
  };

  const onSubmitAndRun = async () => {
    setBusy(true);
    setSubmitError(null);
    setSubmittedRunId(null);
    try {
      const policy = await submitPolicy(name || "untitled-policy", "", yaml);

      // Start analysis in background
      const analysisPromise = startAnalysis(policy.policy_id);

      // Concurrently poll getRuns() to detect the newly created run ID immediately
      let detectedRunId: string | null = null;
      for (let attempt = 0; attempt < 15; attempt++) {
        await new Promise((resolve) => setTimeout(resolve, 600));
        try {
          const runs = await getRuns();
          const found = runs.find(
            (r) =>
              (r.status === "running" || r.status === "completed" || r.status === "failed") &&
              (r.policy_names.includes(policy.name) || r.policy_names.length === 0)
          );
          if (found) {
            detectedRunId = found.run_id;
            setSubmittedRunId(found.run_id);
            break;
          }
        } catch {
          // Ignore transient poll error
        }
      }

      // Await final result from startAnalysis
      const result = await analysisPromise;
      if (!detectedRunId) {
        if (result && result.length > 0 && result[0]?.run_id) {
          setSubmittedRunId(result[0].run_id);
        } else {
          const runs = await getRuns();
          if (runs.length > 0) {
            setSubmittedRunId(runs[0].run_id);
          }
        }
      }
    } catch (e) {
      setSubmitError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">Submit a Policy</h1>
      <p className="page-subtitle">Paste or upload a Kyverno ClusterPolicy to analyze it against historical workloads</p>
      <div className="card">
        <input
          placeholder="Policy name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="search-input"
        />
        <input type="file" accept=".yaml,.yml" onChange={onFile} style={{ marginBottom: "1rem" }} />
        <textarea
          value={yaml}
          onChange={(e) => {
            setYaml(e.target.value);
            setValidation(null);
            setSubmittedRunId(null);
            setSubmitError(null);
          }}
          rows={14}
          style={{ width: "100%", fontFamily: "monospace", fontSize: "0.85rem", background: "var(--bg-surface-alt)", color: "var(--text-primary)", border: "1px solid var(--border-color)", borderRadius: "6px", padding: "0.75rem" }}
          placeholder="apiVersion: kyverno.io/v1..."
        />
        <div style={{ marginTop: "1rem" }}>
          <button className="btn-secondary" onClick={onValidate} disabled={busy || !yaml}>Validate</button>{" "}
          <button onClick={onSubmitAndRun} disabled={busy || !yaml || validation?.valid !== true}>
            {busy ? "Running analysis..." : "Submit & Run Analysis"}
          </button>
        </div>
        {validation && (
          <p style={{ color: validation.valid ? "var(--success)" : "var(--danger)", marginTop: "0.75rem" }}>
            {validation.valid ? "Policy is valid." : validation.error}
          </p>
        )}
        {busy && !run && !submitError && (
          <p className="pulse" style={{ color: "var(--color-text-muted)", marginTop: "0.75rem" }}>
            Replaying history, clustering violations, and generating explanations. This takes 1-3 minutes.
          </p>
        )}
        {(submitError || pollError) && (
          <p style={{ color: "var(--danger)", marginTop: "0.75rem" }}>{submitError || pollError}</p>
        )}
      </div>

      {run && (
        <div
          className="card"
          style={{
            marginTop: "1.25rem",
            borderLeft:
              run.status === "completed"
                ? "4px solid var(--success)"
                : run.status === "failed"
                ? "4px solid var(--danger)"
                : "4px solid var(--info)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <h3 style={{ margin: 0, fontSize: "1.05rem" }}>Run {run.run_id.slice(0, 8)}</h3>
            <span className={`status-pill status-${run.status}`}>{run.status}</span>
          </div>

          {run.status === "running" && (
            <>
              <p className="pulse" style={{ margin: "0.5rem 0" }}>
                Analysis running — this page will update automatically.
              </p>
              <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem", margin: 0 }}>
                Replaying history, clustering violations, and generating explanations. This takes 1-3 minutes.
              </p>
            </>
          )}

          {run.status === "completed" && (
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.5rem" }}>
              <div>
                <p style={{ color: "var(--success)", margin: 0, fontWeight: 600 }}>Analysis completed.</p>
                <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem", margin: "0.25rem 0 0" }}>
                  {run.violation_count} violations detected across {run.clusters.length} clusters ({run.total_records} records analyzed).
                </p>
              </div>
              <Link to={`/runs/${run.run_id}`}>
                <button className="btn-secondary">View Results</button>
              </Link>
            </div>
          )}

          {run.status === "failed" && (
            <div style={{ marginTop: "0.5rem" }}>
              <p style={{ color: "var(--danger)", margin: "0 0 0.25rem 0", fontWeight: 600 }}>Run failed.</p>
              <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem", margin: 0 }}>
                {run.error || "An unknown error occurred during analysis."}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
