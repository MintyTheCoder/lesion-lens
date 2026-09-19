import type { Burden } from "../../api/types";
import { PATTERN_LABEL } from "../../brand";

/**
 * The plate's key: the four numbers the clinician came for, set at figure scale so the
 * subjective read becomes the quantified one. Pattern counts take their ink but never
 * stand without their label text.
 */
export default function BurdenKey({ burden }: { burden: Burden }) {
  const cells: { figure: string; label: string; color?: string }[] = [
    { figure: String(burden.lesion_count), label: burden.lesion_count === 1 ? "lesion detected" : "lesions detected" },
    { figure: `${burden.total_area_pct}%`, label: "lesion burden of slice" },
    { figure: String(burden.ms_typical_count), label: PATTERN_LABEL.ms_typical, color: "#ff7a1a" },
    { figure: String(burden.atypical_count), label: PATTERN_LABEL.atypical, color: "#4fc3f7" },
  ];
  return (
    <dl className="grid grid-cols-2 border-t border-rule" aria-label="Lesion burden">
      {cells.map((c, i) => (
        <div key={c.label} className={`border-b border-rule py-4 ${i % 2 === 0 ? "pr-4" : "pl-4 border-l"}`}>
          <dd
            className="wdth-wide tnum font-semibold tracking-plate leading-[0.86] text-[clamp(2.4rem,3.6vw,3.25rem)]"
            style={c.color ? { color: c.color } : undefined}
          >
            {c.figure}
          </dd>
          <dt className="mt-3 wdth-narrow uppercase tracking-label text-[0.72rem] leading-[1.3] text-bone-dim">
            {c.label}
          </dt>
        </div>
      ))}
    </dl>
  );
}
