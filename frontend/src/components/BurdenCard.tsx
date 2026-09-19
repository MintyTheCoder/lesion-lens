import type { Burden } from "../api/types";

function Stat({ label, value, className = "" }: { label: string; value: string | number; className?: string }) {
  return (
    <div>
      <div className="text-xs text-slate-400">{label}</div>
      <div className={`text-2xl font-semibold ${className}`}>{value}</div>
    </div>
  );
}

export default function BurdenCard({ burden }: { burden: Burden }) {
  return (
    <div className="rounded-lg border border-slate-800 p-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
      <Stat label="Lesions" value={burden.lesion_count} />
      <Stat label="Burden (% slice)" value={`${burden.total_area_pct}%`} />
      <Stat label="MS-typical" value={burden.ms_typical_count} className="text-orange-400" />
      <Stat label="Atypical" value={burden.atypical_count} className="text-sky-400" />
    </div>
  );
}
