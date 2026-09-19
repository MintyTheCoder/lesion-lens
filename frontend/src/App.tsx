import { Link, Route, Routes } from "react-router-dom";
import Analyze from "./pages/Analyze";
import History from "./pages/History";

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">MS Lesion Specificity</h1>
          <p className="text-xs text-slate-400">Decision support for clinician review — not a diagnosis</p>
        </div>
        <nav className="flex gap-4 text-sm">
          <Link to="/" className="hover:underline">Analyze</Link>
          <Link to="/history" className="hover:underline">History</Link>
        </nav>
      </header>
      <main className="p-6 max-w-7xl mx-auto">
        <Routes>
          <Route path="/" element={<Analyze />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  );
}
