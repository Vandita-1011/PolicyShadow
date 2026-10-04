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

export interface ValidationResult { valid: boolean; error: string | null; }

export const validatePolicy = (policy_yaml: string): Promise<ValidationResult> =>
  fetch(`${BASE_URL}/policies/validate`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ policy_yaml }),
  }).then(handle);

export const submitPolicy = (name: string, description: string, policy_yaml: string): Promise<Policy> =>
  fetch(`${BASE_URL}/policies/submit`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description, policy_yaml }),
  }).then(handle);

export const getRuns = (): Promise<RunListItem[]> =>
  fetch(`${BASE_URL}/runs`).then(handle);

export const getRunDetail = (runId: string): Promise<RunDetail> =>
  fetch(`${BASE_URL}/runs/${runId}`).then(handle);

export const startAnalysis = (policy_id?: string): Promise<{ run_id: string }[]> =>
  fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(policy_id ? { policy_id } : {}),
  }).then(handle);

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

export interface Policy {
  policy_id: string;
  name: string;
  description: string | null;
  category: string | null;
  rule_definition: string | null;
  notes: string | null;
  status: string;
  is_system: boolean;
  created_at: string;
}

export interface Stats {
  total_runs: number;
  total_policies: number;
  total_violations_detected: number;
  pending_decisions: number;
}

export interface RunListItem {
  run_id: string;
  created_at: string;
  status: string;
  total_records: number;
  violation_count: number;
  cluster_count: number;
  policy_names: string[];
  decision_summary: string;
}

export const getStats = (): Promise<Stats> =>
  fetch(`${BASE_URL}/stats`).then(handle);

export const getPolicies = (): Promise<Policy[]> =>
  fetch(`${BASE_URL}/policies`).then(handle);
