import { Link, NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Overview", end: true },
  { to: "/policies", label: "Policies", end: false },
  { to: "/history", label: "History", end: false },
];

export function Sidebar() {
  return (
    <div className="sidebar">
      <Link to="/" className="sidebar-brand">
        <span className="sidebar-brand-mark" />
        <span className="sidebar-brand-name">PolicyShadow</span>
      </Link>
      <div className="sidebar-section-label">Analysis</div>
      {links.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          end={l.end}
          className={({ isActive }) => `sidebar-link ${isActive ? "sidebar-link-active" : ""}`}
        >
          {l.label}
        </NavLink>
      ))}
    </div>
  );
}
