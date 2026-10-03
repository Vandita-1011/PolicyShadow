export function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="card" style={{ textAlign: "center", padding: "1.25rem" }}>
      <div style={{ fontSize: "2rem", fontFamily: "var(--font-display)", color: "var(--color-accent)" }}>
        {value}
      </div>
      <div className="label" style={{ marginTop: "0.3rem" }}>{label}</div>
    </div>
  );
}
