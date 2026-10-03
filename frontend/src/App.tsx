import { BrowserRouter, Routes, Route, useNavigate, useParams } from "react-router-dom";
import "./theme.css";
import { NavBar } from "./NavBar";
import { DashboardPage } from "./DashboardPage";
import { HistoryPage } from "./HistoryPage";
import { RunList } from "./RunList";
import { RunDetailView } from "./RunDetailView";

function RunDetailRoute() {
  const { runId } = useParams();
  const navigate = useNavigate();
  if (!runId) return <p>Run not found.</p>;
  return <RunDetailView runId={runId} onBack={() => navigate("/history")} />;
}

function LegacyRunsRoute() {
  const navigate = useNavigate();
  return <RunList onSelect={(id) => navigate(`/runs/${id}`)} />;
}

export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <div className="shell-content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/policies" element={<LegacyRunsRoute />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/runs/:runId" element={<RunDetailRoute />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
