const BASE_URL = "http://127.0.0.1:8000";

export interface RunSummary {
  run_id: string;
  created_at: string;
  status: string;
  total_records: number;
}

export interface Evidence {
  source: string;
  text: string;
}

export interface Decision {
  decision: string;
  note: string | null;
  decided_at: string;
}

export interface Recommendation {
  recommendation_id: string;
  category: string;
  risk_level: string;
  rationale: string;
  decision: Decision | null;
}

export interface Cluster {
  cluster_id: string;
  label: string;
  rule_name: string;
  violation_count: number;
  violation_ids: string[];
  evidence: Evidence[];
  explanation: string;
  recommendation: Recommendation;
}

export interface RunDetail {
  run_id: string;
  created_at: string;
  status: string;
  total_records: number;
  error: string | null;
  violation_count: number;
  clusters: Cluster[];
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  return res.json();
}

export const getRuns = (): Promise<RunSummary[]> =>
  fetch(`${BASE_URL}/runs`).then(handle);

export const getRunDetail = (runId: string): Promise<RunDetail> =>
  fetch(`${BASE_URL}/runs/${runId}`).then(handle);

export const startAnalysis = (): Promise<{ run_id: string }[]> =>
  fetch(`${BASE_URL}/analyze`, { method: "POST" }).then(handle);

export const submitDecision = (
  recommendationId: string,
  decision: "approve" | "reject",
  note: string
): Promise<Decision> =>
  fetch(`${BASE_URL}/recommendations/${recommendationId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, note: note || null }),
  }).then(handle);
