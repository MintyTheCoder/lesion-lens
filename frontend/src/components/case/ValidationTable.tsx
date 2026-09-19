import { useEffect, useState } from "react";
import { getValidation } from "../../api/client";
import type { ValidationReport } from "../../api/types";
import { HONESTY_LINE } from "../../brand";

const pct = (x: number) => `${(x * 100).toFixed(1)}%`;

/**
 * "Does it hold on a hospital it never saw?" — GET /validation. Model-level, not per case.
 * While ml/results/validation.json still holds placeholder zeros the section keeps its
 * place but says so; zeros are never shown as figures.
 */
export default function ValidationTable() {
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getValidation()
      .then(setReport)
      .catch(() => setFailed(true));
  }, []);

  const pending = !report || report.datasets.every((d) => d.n_scans === 0);
  const th = "wdth-narrow uppercase tracking-label text-[0.72rem] font-normal text-bone-dim text-left pb-3";
  const td = "tnum text-[0.95rem] py-3.5";

  return (
    <div>
      <div className="grid grid-cols-1 gap-y-6 lg:grid-cols-[minmax(0,1.5fr)_minmax(21rem,1fr)] lg:gap-x-16">
        <h2 className="wdth-wide text-balance font-medium tracking-plate leading-[1.08] text-[clamp(1.6rem,2.4vw,2.25rem)] max-w-[24ch]">
          Does it hold on a hospital it never saw?
        </h2>
        <p className="text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch] lg:pt-2">
          Trained on MS3SEG; validated on MSLesSeg, 115 multi-hospital scans sealed from training. Reported as
          precision and false positives per scan. {HONESTY_LINE}
        </p>
      </div>

      {failed ? (
        <p className="mt-8 border-t border-b border-rule py-5 text-[0.95rem] text-bone-dim">
          Validation figures are unavailable right now.
        </p>
      ) : pending ? (
        <div className="mt-8 border-t border-b border-rule py-5 grid gap-x-12 gap-y-2 md:grid-cols-[auto_minmax(0,1fr)] items-baseline">
          <span className="wdth-narrow uppercase tracking-label text-[0.85rem] leading-none text-bone">
            Validation run pending
          </span>
          <span className="text-[0.95rem] leading-relaxed text-bone-dim text-pretty max-w-[62ch]">
            Figures arrive from <span className="text-bone">ml/validate</span> over the held-out MS3SEG split and all of
            MSLesSeg. Nothing is shown here until they are real.
          </span>
        </div>
      ) : (
        <div className="mt-8 overflow-x-auto">
          <table className="w-full min-w-[40rem] border-t border-rule">
            <thead>
              <tr className="border-b border-rule">
                <th className={th}>Dataset</th>
                <th className={`${th} text-right`}>Scans</th>
                <th className={`${th} text-right`}>Precision</th>
                <th className={`${th} text-right`}>Recall</th>
                <th className={`${th} text-right`}>FP / scan</th>
                <th className={`${th} text-right`}>Flagged atypical</th>
              </tr>
            </thead>
            <tbody>
              {report!.datasets.map((d) => (
                <tr key={d.name} className="border-b border-rule">
                  <td className={`${td} pr-6`}>{d.name}</td>
                  <td className={`${td} text-right text-bone-dim`}>{d.n_scans}</td>
                  <td className={`${td} text-right`}>{pct(d.precision)}</td>
                  <td className={`${td} text-right`}>{pct(d.recall)}</td>
                  <td className={`${td} text-right`}>{d.fp_per_scan.toFixed(2)}</td>
                  <td className={`${td} text-right text-bone-dim`}>{d.atypical_pct.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-4 text-[0.85rem] leading-snug text-bone-dim max-w-[64ch] text-pretty">
            The atypical share is descriptive: there is no ground truth to score the pattern flag against.
            {report!.note ? ` ${report!.note}` : ""}
          </p>
        </div>
      )}
    </div>
  );
}
