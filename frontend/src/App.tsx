import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import TriggerStatusPage from "./pages/TriggerStatusPage";
import ElementListPage from "./pages/ElementListPage";
import ElementDetailPage from "./pages/ElementDetailPage";
import ArtifactVersionsPage from "./pages/ArtifactVersionsPage";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">Run & Status</Link>
        <Link to="/elements">Elements</Link>
        <Link to="/versions">Versions</Link>
      </nav>
      <Routes>
        <Route path="/" element={<TriggerStatusPage />} />
        <Route path="/elements" element={<ElementListPage />} />
        <Route path="/elements/:elementId" element={<ElementDetailPage />} />
        <Route path="/versions" element={<ArtifactVersionsPage />} />
      </Routes>
    </BrowserRouter>
  );
}
