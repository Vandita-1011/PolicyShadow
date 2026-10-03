import { useState, type ReactNode } from "react";

export function Accordion({ title, children, defaultOpen = false }: { title: string; children: ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="accordion-item">
      <div className="accordion-header" onClick={() => setOpen(!open)}>
        <span>{title}</span>
        <span className={`accordion-chevron ${open ? "open" : ""}`}>›</span>
      </div>
      {open && <div className="accordion-body">{children}</div>}
    </div>
  );
}
