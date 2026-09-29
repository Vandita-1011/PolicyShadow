const BASE_URL = "http://127.0.0.1:8000";

export interface HealthStatus {
  status: string;
}

export interface RunSummary {
  run_id: string;
  created_at: string;
  status: string;
  total_records: number;
}

export async function getHealth(): Promise<HealthStatus> {
  const res = await fetch(`${BASE_URL}/`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function getRuns(): Promise<RunSummary[]> {
  const res = await fetch(`${BASE_URL}/runs`);
  if (!res.ok) throw new Error(`Failed to fetch runs: ${res.status}`);
  return res.json();
}
