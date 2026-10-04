import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { validatePolicy, submitPolicy, startAnalysis } from "./api";

export function SubmitPolicyPage() {
  const [name, setName] = useState("");
  const [yaml, setYaml] = useState("");
  const [validation, setValidation] = useState<{ valid: boolean; error: string | null } | null>(null);
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    file.text().then(setYaml);
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
    try {
      const policy = await submitPolicy(name || "untitled-policy", "", yaml);
      const result = await startAnalysis(policy.policy_id);
      navigate(`/runs/${result[0].run_id}`);
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
          onChange={(e) => { setYaml(e.target.value); setValidation(null); }}
          rows={14}
          style={{ width: "100%", fontFamily: "monospace", fontSize: "0.85rem", background: "var(--bg-surface-alt)", color: "var(--text-primary)", border: "1px solid var(--border-color)", borderRadius: "6px", padding: "0.75rem" }}
          placeholder="apiVersion: kyverno.io/v1..."
        />
        <div style={{ marginTop: "1rem" }}>
          <button className="btn-secondary" onClick={onValidate} disabled={busy || !yaml}>Validate</button>{" "}
          <button onClick={onSubmitAndRun} disabled={busy || !yaml || validation?.valid !== true}>
            Submit &amp; Run Analysis
          </button>
        </div>
        {validation && (
          <p style={{ color: validation.valid ? "var(--success)" : "var(--danger)", marginTop: "0.75rem" }}>
            {validation.valid ? "Policy is valid." : validation.error}
          </p>
        )}
      </div>
    </div>
  );
}
