import type { ReactNode } from "react";

// Axial display, radiological convention (patient's right on the viewer's left).
// Verify against the preprocessing orientation check in data/scripts/load_nifti.py before judging.
export const ORIENTATION = { top: "A", bottom: "P", left: "R", right: "L" };

/** The square plate frame: rule-strong border, plate ground, capped so the whole plate fits the first viewport. */
export const FRAME_CLASS =
  "relative aspect-square w-full mx-auto lg:mx-0 border bg-plate lg:max-w-[calc(100vh-12rem)] transition-colors duration-200 ease-out";

/** The plate's 1.5fr figure / minmax(21rem, 1fr) margin grid, shared by every plate stanza. */
export const PLATE_GRID = "grid grid-cols-1 gap-y-8 lg:gap-x-16 lg:grid-cols-[minmax(0,1.5fr)_minmax(21rem,1fr)]";

interface FurnitureProps {
  /** `active` brightens the ticks and letters to bone: the drag-over and focus gesture on the intake frame. */
  tone?: "rest" | "active";
}

/** Corner ticks and orientation letters in the frame margin: the plate reads as a plate even before the slice lands. */
export function FrameFurniture({ tone = "rest" }: FurnitureProps) {
  const active = tone === "active";
  const tick = `absolute w-4 h-4 transition-colors duration-200 ease-out ${active ? "border-bone" : "border-rule-strong"}`;
  const letter = `absolute wdth-narrow tnum text-[0.72rem] leading-none tracking-label select-none transition-colors duration-200 ease-out ${
    active ? "text-bone" : "text-bone-dim"
  }`;
  return (
    <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
      <span className={`${tick} left-3 top-3 border-l border-t`} />
      <span className={`${tick} right-3 top-3 border-r border-t`} />
      <span className={`${tick} left-3 bottom-3 border-l border-b`} />
      <span className={`${tick} right-3 bottom-3 border-r border-b`} />
      <span className={`${letter} top-3 left-1/2 -translate-x-1/2`}>{ORIENTATION.top}</span>
      <span className={`${letter} bottom-3 left-1/2 -translate-x-1/2`}>{ORIENTATION.bottom}</span>
      <span className={`${letter} left-3 top-1/2 -translate-y-1/2`}>{ORIENTATION.left}</span>
      <span className={`${letter} right-3 top-1/2 -translate-y-1/2`}>{ORIENTATION.right}</span>
    </div>
  );
}

interface CaptionProps {
  /** The plate number, e.g. "Plate 1"; an em dash while the plate has no figure yet. */
  plate: string;
  children: ReactNode;
}

/** The figure caption row: plate number in label type, then whatever the plate needs to say about itself. */
export function PlateCaption({ plate, children }: CaptionProps) {
  return (
    <figcaption className="mt-4 flex flex-wrap items-baseline gap-x-4 gap-y-1 text-[0.85rem] leading-snug text-bone-dim">
      <span className="wdth-narrow uppercase tracking-label text-bone">{plate}</span>
      {children}
    </figcaption>
  );
}
