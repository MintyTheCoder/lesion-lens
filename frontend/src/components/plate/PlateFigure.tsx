import { useCallback, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { AnalysisResult, Lesion } from "../../api/types";
import { LOCATION_LABEL, PATTERN_LABEL } from "../../brand";
import { FRAME_CLASS, FrameFurniture, PlateCaption } from "./PlateFrame";

export const PATTERN_HEX: Record<Lesion["pattern"], string> = {
  ms_typical: "#ff7a1a",
  atypical: "#4fc3f7",
};

interface Props {
  result: AnalysisResult;
  /** Public path of the slice. When it fails to load, a labeled slot is rendered in its place. */
  imageSrc: string;
  /** Title block rendered at the head of the margin, above the legend. */
  aside: ReactNode;
  /** The plate's single action, rendered directly beneath the legend. */
  action: ReactNode;
  /** Figure caption source note, e.g. "mock detections". */
  sourceNote?: string;
  /** Plate number in the caption. */
  plate?: string;
  /** Extra caption spans after the counts (model line, timing, timestamp). */
  caption?: ReactNode;
  /** Show location and area under each legend entry: the clinician's read, not the landing's summary. */
  legendDetail?: boolean;
  /** Rendered in the legend when the result has no lesions: a finding, not an error. */
  emptyLegend?: ReactNode;
}

interface Leader {
  id: number;
  d: string;
  /** Box-end terminal, in plate coordinates. */
  tx: number;
  ty: number;
}

const LG = "(min-width: 1024px)";
/** Rendered pixel size of the numeral on each box, held constant across frame sizes. */
const NUMERAL_PX = 18;
/** Above this many lesions the leaders would cross; the numerals on the boxes carry the link instead. */
const MAX_LEADERS = 12;

/**
 * An atlas plate: the slice is the figure, each lesion a numbered callout, and a hairline
 * leader runs from every box to its legend entry in the margin. Leaders are measured from
 * the DOM so they stay attached at any width; below `lg` the legend stacks and the numerals
 * on the boxes carry the link instead.
 */
export default function PlateFigure({
  result,
  imageSrc,
  aside,
  action,
  sourceNote,
  plate = "Plate 1",
  caption,
  legendDetail = false,
  emptyLegend,
}: Props) {
  const { width, height } = result.image;
  const ordered = useMemo(
    () => [...result.lesions].sort((a, b) => a.bbox[1] - b.bbox[1] || a.bbox[0] - b.bbox[0]),
    [result.lesions],
  );
  const numeral = useMemo(() => new Map(ordered.map((l, i) => [l.id, i + 1])), [ordered]);

  const [hover, setHover] = useState<number | null>(null);
  const [pinned, setPinned] = useState<number | null>(null);
  const active = hover ?? pinned;

  const [imgOk, setImgOk] = useState<boolean | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<HTMLDivElement>(null);
  const rowRefs = useRef(new Map<number, HTMLElement>());
  const [leaders, setLeaders] = useState<Leader[]>([]);
  const [box, setBox] = useState({ w: 0, h: 0 });
  /** Frame pixels per image pixel; keeps numerals and strokes viewport-stable. */
  const [scale, setScale] = useState(1);

  const setRow = useCallback((id: number) => (el: HTMLElement | null) => {
    if (el) rowRefs.current.set(id, el);
    else rowRefs.current.delete(id);
  }, []);

  useLayoutEffect(() => {
    const measure = () => {
      const c = containerRef.current;
      const f = frameRef.current;
      if (!c || !f) return;
      const cr = c.getBoundingClientRect();
      const fr = f.getBoundingClientRect();
      // The image is object-fit: contain inside a square frame; find the rendered content rect.
      const s = Math.min(fr.width / width, fr.height / height);
      setScale(s || 1);

      if (!window.matchMedia(LG).matches || ordered.length > MAX_LEADERS) {
        setLeaders([]);
        return;
      }
      const cw = width * s;
      const ch = height * s;
      const ox = fr.left - cr.left + (fr.width - cw) / 2;
      const oy = fr.top - cr.top + (fr.height - ch) / 2;
      const gutter = fr.right - cr.left + 22;
      const n = ordered.length;

      const next: Leader[] = [];
      ordered.forEach((l, i) => {
        const row = rowRefs.current.get(l.id);
        if (!row) return;
        const rr = row.getBoundingClientRect();
        const [x, y, w, h] = l.bbox;
        const bx = ox + (x + w) * s + 3;
        const by = oy + (y + h / 2) * s;
        // Upper rows take the outer trunk so arms never cross a neighbour's trunk.
        const gx = gutter + (n - 1 - i) * 7;
        const rx = rr.left - cr.left - 10;
        const ry = rr.top - cr.top + rr.height / 2;
        next.push({
          id: l.id,
          d: `M${bx.toFixed(1)} ${by.toFixed(1)} H${gx} V${ry.toFixed(1)} H${rx.toFixed(1)}`,
          tx: bx,
          ty: by,
        });
      });
      setLeaders(next);
      setBox({ w: cr.width, h: cr.height });
    };

    measure();
    const ro = new ResizeObserver(measure);
    if (containerRef.current) ro.observe(containerRef.current);
    if (frameRef.current) ro.observe(frameRef.current);
    const mq = window.matchMedia(LG);
    mq.addEventListener("change", measure);
    window.addEventListener("resize", measure);
    document.fonts?.ready.then(measure);
    return () => {
      ro.disconnect();
      mq.removeEventListener("change", measure);
      window.removeEventListener("resize", measure);
    };
  }, [ordered, width, height, imgOk]);

  const b = result.burden;
  const dimOthers = active !== null;
  // SVG user units are image pixels; divide by scale to hold a rendered size constant.
  const u = (px: number) => px / scale;

  return (
    <div
      ref={containerRef}
      className="relative grid grid-cols-1 gap-y-8 lg:gap-x-16 lg:grid-cols-[minmax(0,1.5fr)_minmax(21rem,1fr)] lg:grid-rows-[auto_auto_1fr]"
    >
      {/* Margin: title */}
      <div className="lg:col-start-2 lg:row-start-1 order-1">{aside}</div>

      {/* Figure */}
      <figure
        className={`lg:col-start-1 lg:row-start-1 lg:row-span-3 order-2 min-w-0 ${
          ordered.length > MAX_LEADERS ? "lg:sticky lg:top-6 lg:self-start" : ""
        }`}
      >
        <div ref={frameRef} className={`${FRAME_CLASS} border-rule-strong`}>
          {imgOk !== false ? (
            <img
              src={imageSrc}
              alt="Axial FLAIR MRI slice with detected white-matter lesions boxed"
              className={`absolute inset-0 w-full h-full object-contain select-none ${imgOk ? "" : "opacity-0"}`}
              draggable={false}
              onLoad={() => setImgOk(true)}
              onError={() => setImgOk(false)}
            />
          ) : (
            <SliceSlot />
          )}

          <FrameFurniture />

          {/* Lesion boxes in image pixel coordinates */}
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="absolute inset-0 w-full h-full"
            role="img"
            aria-label={`${b.lesion_count} lesions boxed: ${b.ms_typical_count} MS-typical, ${b.atypical_count} atypical or nonspecific`}
          >
            {ordered.map((l) => {
              const [x, y, w, h] = l.bbox;
              const color = PATTERN_HEX[l.pattern];
              const isActive = active === l.id;
              const faded = dimOthers && !isActive;
              const pad = u(3);
              const cy = y + h / 2;
              return (
                <g
                  key={l.id}
                  className="cursor-pointer transition-opacity duration-300 ease-out"
                  style={{ opacity: faded ? 0.3 : 1 }}
                  onMouseEnter={() => setHover(l.id)}
                  onMouseLeave={() => setHover(null)}
                  onClick={() => setPinned((p) => (p === l.id ? null : l.id))}
                >
                  <rect
                    x={x - pad}
                    y={y - pad}
                    width={w + pad * 2}
                    height={h + pad * 2}
                    fill={isActive ? color : "transparent"}
                    fillOpacity={isActive ? 0.18 : 0}
                    stroke={color}
                    strokeWidth={isActive ? 2 : 1.25}
                    vectorEffect="non-scaling-stroke"
                  />
                  {/* numeral, left of the box on its centreline, joined by a short tick */}
                  <line
                    x1={x - pad}
                    y1={cy}
                    x2={x - pad - u(8)}
                    y2={cy}
                    stroke={color}
                    strokeWidth={1}
                    vectorEffect="non-scaling-stroke"
                  />
                  <text
                    x={x - pad - u(12)}
                    y={cy}
                    textAnchor="end"
                    dominantBaseline="central"
                    fill={isActive ? "#ece9e2" : color}
                    fontSize={u(NUMERAL_PX)}
                    fontWeight={600}
                    fontFamily="Archivo, system-ui, sans-serif"
                    style={{ fontVariantNumeric: "tabular-nums" }}
                  >
                    {numeral.get(l.id)}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        <PlateCaption plate={plate}>
          <span>FLAIR, axial</span>
          <span className="tnum">
            {b.lesion_count} lesions detected — {b.ms_typical_count} MS-typical, {b.atypical_count} atypical or
            nonspecific
          </span>
          <span className="tnum">burden {b.total_area_pct}% of slice</span>
          {caption}
          {sourceNote && <span>{sourceNote}</span>}
          {imgOk === false && <span>sample slice pending</span>}
        </PlateCaption>
      </figure>

      {/* Margin: legend */}
      <ol
        className="lg:col-start-2 lg:row-start-2 order-3 self-start border-t border-rule"
        aria-label="Lesion legend"
        onMouseLeave={() => setHover(null)}
      >
        {ordered.length === 0 && emptyLegend && (
          <li className="border-b border-rule py-5 text-[0.95rem] leading-relaxed text-bone-dim text-pretty">{emptyLegend}</li>
        )}
        {ordered.map((l) => {
          const isActive = active === l.id;
          const faded = dimOthers && !isActive;
          const color = PATTERN_HEX[l.pattern];
          return (
            <li key={l.id} ref={setRow(l.id)} className="border-b border-rule">
              <button
                type="button"
                aria-pressed={pinned === l.id}
                onMouseEnter={() => setHover(l.id)}
                onFocus={() => setHover(l.id)}
                onBlur={() => setHover(null)}
                onClick={() => setPinned((p) => (p === l.id ? null : l.id))}
                className="w-full text-left grid grid-cols-[2.5rem_minmax(0,1fr)_auto] gap-x-3 py-3.5 transition-opacity duration-300 ease-out"
                style={{ opacity: faded ? 0.38 : 1 }}
              >
                <span className="tnum text-[1.5rem] leading-none font-medium">{numeral.get(l.id)}</span>
                <span className="min-w-0">
                  <span className="block text-[1.1rem] leading-tight font-medium" style={{ color }}>
                    {PATTERN_LABEL[l.pattern]}
                  </span>
                  {legendDetail && (
                    <span className="block mt-1.5 tnum text-[0.85rem] leading-snug text-bone">
                      {LOCATION_LABEL[l.features.location]} · {l.area_px.toLocaleString()} px
                    </span>
                  )}
                  <span className="block mt-1.5 text-[0.95rem] leading-snug text-bone-dim text-pretty">
                    {l.reasons.join(" · ")}
                  </span>
                </span>
                <span className="tnum text-[0.85rem] leading-none text-bone-dim pt-[5px]">
                  {l.confidence.toFixed(2)}
                </span>
              </button>
            </li>
          );
        })}
      </ol>

      {/* Margin: action, directly beneath the legend */}
      <div className="lg:col-start-2 lg:row-start-3 order-4 self-start mt-2">{action}</div>

      {/* Leaders, drawn over the whole plate on lg+ */}
      {leaders.length > 0 && box.w > 0 && (
        <svg
          className="pointer-events-none absolute inset-0 hidden lg:block"
          width={box.w}
          height={box.h}
          viewBox={`0 0 ${box.w} ${box.h}`}
          aria-hidden="true"
        >
          {leaders.map((ld, i) => {
            const isActive = active === ld.id;
            const faded = dimOthers && !isActive;
            const stroke = isActive ? "#ece9e2" : "rgba(236,233,226,0.7)";
            return (
              <g
                key={ld.id}
                className="transition-opacity duration-300 ease-out"
                style={{ opacity: faded ? 0.25 : 1 }}
              >
                <path
                  d={ld.d}
                  pathLength={1}
                  className="leader"
                  fill="none"
                  stroke={stroke}
                  strokeWidth={isActive ? 1.25 : 1}
                  style={{ animationDelay: `${i * 60}ms` }}
                />
                {/* terminal at the box end */}
                <circle cx={ld.tx} cy={ld.ty} r={2} fill={stroke} />
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
}

/** Rendered in the figure frame when no sample slice has been placed at the image path yet. */
function SliceSlot() {
  return (
    <div className="absolute inset-x-0 bottom-9 text-center px-8" aria-hidden="true">
      <p className="wdth-narrow uppercase tracking-label text-[0.85rem] text-bone-dim">FLAIR slice · sample pending</p>
      <p className="mt-1.5 hidden lg:block text-[0.85rem] text-bone-dim tnum">frontend/public/plate/hero-slice.png</p>
    </div>
  );
}
