import { useState } from "react";
import "./theme.css";
import { RunList } from "./RunList";
import { RunDetailView } from "./RunDetailView";

export default function App() {
  const [selectedRun, setSelectedRun] = useState<string | null>(null);

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "2.5rem 1.5rem" }}>
      <div className="app-header">
        <h1>PolicyShadow</h1>
        <p className="app-tagline">
          Decision support for safe Kubernetes admission policy rollout
        </p>
      </div>
      {selectedRun ? (
        <RunDetailView runId={selectedRun} onBack={() => setSelectedRun(null)} />
      ) : (
        <RunList onSelect={setSelectedRun} />
      )}
    </div>
  );
}
