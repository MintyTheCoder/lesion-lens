import { useEffect, useState } from "react";
import { getValidation } from "../api/client";
import type { ValidationReport } from "../api/types";

/** The "does it hold up on a hospital it never saw?" panel. Reads GET /validation. */
export default function ValidationPanel() {
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    getValidation().then(setReport).catch((e) => setErr(String(e)));
  }, []);

  if (err) return <div className="text-xs text-red-400">Validation unavailable: {err}</div>;
  if (!report) return null;

  return (
    <div className="rounded-lg border border-slate-800 p-4">
      <h3 className="text-sm font-semibold text-slate-300 mb-2">Cross-dataset validation</h3>
      <table className="w-full text-sm">
        <thead className="text-slate-400 text-left">
          <tr>
            <th>Dataset</th>
            <th>Scans</th>
            <th>Precision</th>
            <th>Recall</th>
            <th>FP / scan</th>
            <th>Atypical %</th>
          </tr>
        </thead>
        <tbody>
          {report.datasets.map((d) => (
            <tr key={d.name} className="border-t border-slate-800">
              <td className="py-1">{d.name}</td>
              <td>{d.n_scans}</td>
              <td>{(d.precision * 100).toFixed(1)}%</td>
              <td>{(d.recall * 100).toFixed(1)}%</td>
              <td>{d.fp_per_scan.toFixed(2)}</td>
              <td>{d.atypical_pct.toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
      {report.note && <p className="text-xs text-slate-500 mt-2">{report.note}</p>}
    </div>
  );
}
