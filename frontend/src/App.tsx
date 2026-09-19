import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import Analyze from "./pages/Analyze";
import History from "./pages/History";
import Landing from "./pages/Landing";
import { DESCRIPTOR, PRODUCT_NAME } from "./brand";

const navClass = ({ isActive }: { isActive: boolean }) =>
  [
    "wdth-narrow uppercase tracking-label text-[0.72rem] leading-none py-2 border-b transition-colors duration-200 ease-out",
    isActive ? "text-bone border-bone" : "text-bone-dim border-transparent hover:text-bone hover:border-rule-strong",
  ].join(" ");

export default function App() {
  const { pathname } = useLocation();
  const onPlate = pathname === "/";

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-rule px-4 sm:px-8 h-14 flex items-center justify-between gap-6">
        <Link to="/" className="flex items-baseline gap-3 min-w-0">
          <span className="wdth-wide font-semibold tracking-plate text-[0.95rem] leading-none whitespace-nowrap">
            {PRODUCT_NAME}
          </span>
          <span className="hidden md:inline text-[0.72rem] leading-none text-bone-dim truncate">{DESCRIPTOR}</span>
        </Link>
        <nav className="flex items-center gap-6">
          <NavLink to="/analyze" className={navClass}>
            Analyze
          </NavLink>
          <NavLink to="/history" className={navClass}>
            History
          </NavLink>
        </nav>
      </header>
      <main className={onPlate ? "flex-1" : "flex-1 p-6 max-w-7xl w-full mx-auto"}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  );
}
