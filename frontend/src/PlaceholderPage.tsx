export function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="card empty-state">
      <h3>{title}</h3>
      <p>This page is being built in the next step.</p>
    </div>
  );
}
