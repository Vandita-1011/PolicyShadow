import { Link, NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/policies", label: "Policies", end: false },
  { to: "/history", label: "History", end: false },
];

export function NavBar() {
  return (
    <div className="shell-nav">
      <div className="shell-nav-inner">
        <Link to="/" className="brand">
          <span className="brand-mark" />
          <span className="brand-name">PolicyShadow</span>
        </Link>
        <div className="nav-links">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) => `nav-link ${isActive ? "nav-link-active" : ""}`}
            >
              {l.label}
            </NavLink>
          ))}
        </div>
      </div>
    </div>
  );
}
