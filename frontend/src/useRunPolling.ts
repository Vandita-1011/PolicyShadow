import { useEffect, useState } from "react";
import { getRunDetail, type RunDetail } from "./api";

export function useRunPolling(runId: string | null) {
  const [run, setRun] = useState<RunDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;
    setRun(null);
    setError(null);
    let cancelled = false;

    const poll = async () => {
      try {
        const detail = await getRunDetail(runId);
        if (cancelled) return;
        setRun(detail);
        if (detail.status === "running") {
          setTimeout(poll, 3000);
        }
      } catch (e) {
        if (!cancelled) setError(String(e));
      }
    };
    poll();

    return () => {
      cancelled = true;
    };
  }, [runId]);

  return { run, error };
}
