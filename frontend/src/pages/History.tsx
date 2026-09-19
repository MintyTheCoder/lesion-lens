import { useEffect, useState } from "react";
import { getCase, getCases } from "../api/client";
import type { AnalysisResult, CaseSummary } from "../api/types";
import BurdenCard from "../components/BurdenCard";
import ScanViewer from "../components/ScanViewer";

/** Cases saved to MongoDB Atlas. Burden over time is the clinical monitoring story. */
export default function History() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [open, setOpen] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    getCases().then(setCases).catch(console.error);
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <ul className="space-y-1 text-sm">
        {cases.length === 0 && <li className="text-slate-500">No saved cases yet.</li>}
        {cases.map((c) => (
          <li key={c.case_id}>
            <button
              onClick={() => getCase(c.case_id).then(setOpen)}
              className="w-full text-left rounded px-3 py-2 hover:bg-slate-900 border border-slate-800"
            >
              <div className="font-mono text-xs text-slate-400">
                {c.case_id.slice(0, 8)} - {new Date(c.created_at).toLocaleString()}
              </div>
              <div>
                {c.lesion_count} lesions - <span className="text-sky-400">{c.atypical_count} atypical</span>
              </div>
            </button>
          </li>
        ))}
      </ul>
      <div className="lg:col-span-2 space-y-4">
        {open && (
          <>
            <BurdenCard burden={open.burden} />
            <ScanViewer result={open} />
          </>
        )}
      </div>
    </div>
  );
}
