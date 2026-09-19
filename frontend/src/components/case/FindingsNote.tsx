import { useEffect, useState } from "react";
import { NOT_A_DIAGNOSIS } from "../../brand";
import PlateAction from "../plate/PlateAction";

/**
 * The hand-off artifact: 3–5 sentences a radiologist can paste into a referral note or
 * chart. Copy is the one thing the clinician does with it, so it is the one action here.
 */
export default function FindingsNote({ summary }: { summary: string }) {
  const [copied, setCopied] = useState(false);
  useEffect(() => {
    if (!copied) return;
    const t = window.setTimeout(() => setCopied(false), 1800);
    return () => window.clearTimeout(t);
  }, [copied]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
    } catch {
      // Clipboard blocked (insecure context): select the note so the clinician can copy by hand.
      const el = document.getElementById("findings-note");
      if (el) window.getSelection()?.selectAllChildren(el);
    }
  };

  return (
    <div className="grid grid-cols-1 gap-y-8 lg:grid-cols-[minmax(0,1.5fr)_minmax(21rem,1fr)] lg:gap-x-16">
      <div>
        <h2 className="wdth-wide text-balance font-medium tracking-plate leading-[1.08] text-[clamp(1.6rem,2.4vw,2.25rem)] max-w-[24ch]">
          Findings note
        </h2>
        <p id="findings-note" className="mt-8 text-pretty text-[1.1rem] leading-relaxed max-w-[62ch]">
          {summary}
        </p>
      </div>
      <aside className="lg:self-end">
        <p className="text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch]">{NOT_A_DIAGNOSIS}</p>
        <div className="mt-6" aria-live="polite">
          <PlateAction size="quiet" onClick={copy}>
            {copied ? "Copied to clipboard" : "Copy note"}
          </PlateAction>
        </div>
      </aside>
    </div>
  );
}
