import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { AnalysisResult } from "../../api/types";
import PlateFigure from "../plate/PlateFigure";
import BurdenKey from "./BurdenKey";
import FindingsNote from "./FindingsNote";
import ValidationTable from "./ValidationTable";

interface Props {
  result: AnalysisResult;
  /** The plate's single action, beneath the legend (Analyze another slice, or back to the case list). */
  action: ReactNode;
  /** Extra caption spans: how long the read took, and so on. */
  caption?: ReactNode;
}

/**
 * A finished plate: the landing's Plate 1 composition with the clinician's own slice, the
 * burden as the plate's key, the note as the hand-off, and the cross-dataset check last.
 * Shared by the Analyze result and a reopened case so the two never drift.
 */
export default function CaseView({ result, action, caption }: Props) {
  const [atypicalOnly, setAtypicalOnly] = useState(false);
  const stamp = new Date(result.created_at);

  const hasTypical = result.lesions.some((l) => l.pattern === "ms_typical");
  const hasAtypical = result.lesions.some((l) => l.pattern === "atypical");
  const showToggle = hasTypical && hasAtypical;

  // Filters what's drawn only. BurdenKey always shows the true, unfiltered totals — the toggle
  // is a display aid, never a reason for the counted burden to look different than it is.
  const displayed = useMemo(() => {
    if (!atypicalOnly) return result;
    const filtered = result.lesions.filter((l) => l.pattern === "atypical");
    const totalPx = result.image.width * result.image.height;
    const shownPx = filtered.reduce((sum, l) => sum + l.area_px, 0);
    return {
      ...result,
      lesions: filtered,
      burden: {
        ...result.burden,
        lesion_count: filtered.length,
        ms_typical_count: 0,
        atypical_count: filtered.length,
        total_area_pct: Math.round((shownPx / totalPx) * 10000) / 100,
      },
    };
  }, [result, atypicalOnly]);

  return (
    <>
      <section className="border-t border-rule px-4 sm:px-8 pt-10 lg:pt-12 pb-16">
        <PlateFigure
          result={displayed}
          imageSrc={result.image.data_url}
          aside={
            <div>
              <BurdenKey burden={result.burden} />
              {showToggle && (
                <label className="mt-6 flex items-center gap-3 cursor-pointer select-none w-fit">
                  <span className="wdth-narrow uppercase tracking-label text-[0.72rem] text-bone-dim">
                    Atypical only
                  </span>
                  <span className="relative h-5 w-9 shrink-0">
                    <input
                      type="checkbox"
                      checked={atypicalOnly}
                      onChange={(e) => setAtypicalOnly(e.target.checked)}
                      className="peer absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <span className="pointer-events-none absolute inset-0 rounded-full border border-rule-strong transition-colors duration-200 ease-out peer-checked:border-atypical peer-checked:bg-atypical/20" />
                    <span className="pointer-events-none absolute left-0.5 top-0.5 h-3.5 w-3.5 rounded-full bg-bone-dim transition-transform duration-200 ease-out peer-checked:translate-x-4 peer-checked:bg-atypical" />
                  </span>
                </label>
              )}
            </div>
          }
          action={action}
          legendDetail
          emptyLegend={
            atypicalOnly
              ? "No atypical or nonspecific lesions in this slice."
              : "No white-matter lesions were detected in this slice."
          }
          caption={
            <>
              {caption}
              <span className="tnum">
                {stamp.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}{" "}
                {stamp.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}
              </span>
              <span>
                model {result.model.id} · trained on {result.model.trained_on}
              </span>
              {atypicalOnly && <span>showing atypical only</span>}
            </>
          }
        />
      </section>

      <section className="border-t border-rule px-4 sm:px-8 pt-16 pb-16">
        <FindingsNote summary={result.summary} />
      </section>

      <section className="border-t border-rule px-4 sm:px-8 pt-16 pb-20">
        <ValidationTable />
      </section>
    </>
  );
}