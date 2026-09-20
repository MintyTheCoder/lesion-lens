import { useEffect, useState } from "react";
import { getBurdenTrend, getCase, getCases } from "../api/client";
import type { AnalysisResult, BurdenTrend, CaseSummary } from "../api/types";
import CaseView from "../components/case/CaseView";
import PlateAction from "../components/plate/PlateAction";
import { PLATE_GRID } from "../components/plate/PlateFrame";

const DIRECTION_LABEL: Record<BurdenTrend["direction"], string> = {
  rising: "Rising",
  stable: "Stable",
  falling: "Falling",
  insufficient_data: "Not enough data yet",
};

function Sparkline({ points }: { points: BurdenTrend["points"] }) {
  const w = 220;
  const h = 40;
  const values = points.map((p) => p.total_area_pct);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = points.length > 1 ? w / (points.length - 1) : 0;
  const coords = values.map((v, i) => {
    const x = i * step;
    const y = h - ((v - min) / range) * h;
    return `${x},${y}`;
  });
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="text-bone" aria-hidden="true">
      <polyline
        points={coords.join(" ")}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

/** Cases saved to MongoDB Atlas. Opening one reuses CaseView, the same plate Analyze renders on
 * a finished read, so a case looks identical whether you're seeing it fresh or reopening it. */
export default function History() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [trend, setTrend] = useState<BurdenTrend | null>(null);
  const [open, setOpen] = useState<AnalysisResult | null>(null);
  const [loadingId, setLoadingId] = useState<string | null>(null);

  useEffect(() => {
    getCases().then(setCases).catch(console.error);
    getBurdenTrend().then(setTrend).catch(console.error);
  }, []);

  const openCase = (id: string) => {
    setLoadingId(id);
    getCase(id)
      .then(setOpen)
      .catch(console.error)
      .finally(() => setLoadingId(null));
  };

  if (open) {
    return (
      <article>
        <CaseView
          result={open}
          action={<PlateAction onClick={() => setOpen(null)}>Back to history</PlateAction>}
          caption={
            <span className="tnum">
              {open.case_id.slice(0, 8)} · {new Date(open.created_at).toLocaleString()}
            </span>
          }
        />
      </article>
    );
  }

  return (
    <article>
      <section className="px-4 sm:px-8 pt-12 pb-10 lg:pt-16 lg:pb-12">
        <div className={`${PLATE_GRID} lg:items-start`}>
          <h1 className="wdth-wide font-medium tracking-plate leading-[1.06] text-[clamp(1.6rem,2.4vw,2.25rem)]">
            History
          </h1>
          <p className="text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch] lg:pt-1">
            Every case saved to Mongo. Open one to reread its plate.
          </p>
        </div>
      </section>

      {trend && trend.points.length >= 2 && (
        <section className="border-t border-rule px-4 sm:px-8 pt-10 lg:pt-12 pb-10">
          <div className={`${PLATE_GRID} lg:items-start`}>
            <h2 className="wdth-wide font-medium tracking-plate leading-[1.06] text-[clamp(1.1rem,1.6vw,1.4rem)]">
              Burden over time
            </h2>
            <div className="flex flex-col gap-3 lg:pt-1">
              <p className="text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch]">
                Total lesion area across {trend.points.length} saved cases:{" "}
                <span className={trend.direction === "rising" ? "text-atypical" : "text-bone"}>
                  {DIRECTION_LABEL[trend.direction]}
                </span>
              </p>
              <Sparkline points={trend.points} />
            </div>
          </div>
        </section>
      )}

      <section className="border-t border-rule px-4 sm:px-8 pt-10 lg:pt-12 pb-16">
        {cases.length === 0 ? (
          <p className="text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch]">
            No saved cases yet. Analyze a slice to start building history.
          </p>
        ) : (
          <ol className="border-t border-rule max-w-[64ch]">
            {cases.map((c, i) => (
              <li key={c.case_id} className="border-b border-rule">
                <button
                  type="button"
                  onClick={() => openCase(c.case_id)}
                  disabled={loadingId === c.case_id}
                  className="group w-full text-left grid grid-cols-[2.5rem_minmax(0,1fr)_auto] gap-x-3 py-3.5 items-start"
                >
                  <span className="tnum text-[1.5rem] leading-none font-medium">{i + 1}</span>
                  <span className="min-w-0">
                    <span className="block text-[1.1rem] leading-tight font-medium tnum">
                      {c.lesion_count} lesions
                      {c.atypical_count > 0 && <span className="text-atypical"> · {c.atypical_count} atypical</span>}
                    </span>
                    <span className="block mt-1.5 text-[0.85rem] leading-snug text-bone-dim tnum">
                      {c.case_id.slice(0, 8)} · {new Date(c.created_at).toLocaleString()}
                    </span>
                  </span>
                  <svg
                    width={22}
                    height={12}
                    viewBox="0 0 22 12"
                    fill="none"
                    aria-hidden="true"
                    className="shrink-0 mt-[6px] text-bone-dim transition-[color,transform] duration-300 ease-out group-hover:text-bone group-hover:translate-x-1 group-focus-visible:text-bone"
                  >
                    <path d="M0 6h20M15 1l5 5-5 5" stroke="currentColor" strokeWidth={1.25} strokeLinecap="square" />
                  </svg>
                </button>
              </li>
            ))}
          </ol>
        )}
      </section>
    </article>
  );
}
