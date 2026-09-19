import { useState } from "react";
import type { AnalysisResult, Lesion } from "../api/types";

export const PATTERN_COLOR: Record<Lesion["pattern"], string> = {
  ms_typical: "#f97316", // orange-500
  atypical: "#38bdf8", // sky-400
};

interface Props {
  result: AnalysisResult;
  selected?: number | null;
  onSelect?: (id: number | null) => void;
}

/** Image + SVG overlay. Boxes scale with the image because the SVG viewBox is the image's pixel size. */
export default function ScanViewer({ result, selected, onSelect }: Props) {
  const [hover, setHover] = useState<number | null>(null);
  const { width, height } = result.image;
  const active = hover ?? selected ?? null;
  const activeLesion = result.lesions.find((l) => l.id === active);

  return (
    <div className="relative w-full">
      <img src={result.image.data_url} alt="FLAIR slice" className="w-full rounded" />
      <svg viewBox={`0 0 ${width} ${height}`} className="absolute inset-0 w-full h-full">
        {result.lesions.map((l) => {
          const [x, y, w, h] = l.bbox;
          const isActive = active === l.id;
          const color = PATTERN_COLOR[l.pattern];
          return (
            <g
              key={l.id}
              onMouseEnter={() => setHover(l.id)}
              onMouseLeave={() => setHover(null)}
              onClick={() => onSelect?.(l.id)}
              className="cursor-pointer"
            >
              <rect
                x={x}
                y={y}
                width={w}
                height={h}
                fill={isActive ? color + "33" : "transparent"}
                stroke={color}
                strokeWidth={isActive ? 3 : 1.5}
              />
              <text x={x} y={y - 3} fill={color} fontSize={12} fontFamily="monospace">
                {l.id}
              </text>
            </g>
          );
        })}
      </svg>
      {activeLesion && <Tooltip lesion={activeLesion} />}
    </div>
  );
}

function Tooltip({ lesion }: { lesion: Lesion }) {
  const label = lesion.pattern === "ms_typical" ? "MS-typical" : "Atypical / nonspecific";
  return (
    <div className="absolute bottom-2 left-2 rounded bg-slate-900/90 p-3 text-xs max-w-xs border border-slate-700">
      <div className="font-semibold" style={{ color: PATTERN_COLOR[lesion.pattern] }}>
        #{lesion.id} - {label} - {(lesion.confidence * 100).toFixed(0)}%
      </div>
      <div className="text-slate-300 mt-1">
        {lesion.features.location.replace("_", " ")} - elongation {lesion.features.elongation.toFixed(1)} - ovoid{" "}
        {lesion.features.ovoid_score.toFixed(2)}
      </div>
      <ul className="mt-1 text-slate-400 list-disc pl-4">
        {lesion.reasons.map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
    </div>
  );
}
