export default function SummaryCard({ summary }: { summary: string }) {
  return (
    <div className="rounded-lg border border-slate-800 p-4 space-y-3">
      <h3 className="text-sm font-semibold text-slate-300">Findings summary</h3>
      <p className="text-sm leading-relaxed">{summary}</p>
      <p className="text-xs text-amber-400/90 border-t border-slate-800 pt-2">
        Pattern flags encode established radiological criteria for distinguishing MS-typical from nonspecific
        lesions. This is decision support for clinician review. It is not a diagnosis and is never shown to patients.
      </p>
    </div>
  );
}
