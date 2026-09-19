import { useState, type DragEvent } from "react";
import { FRAME_CLASS, FrameFurniture } from "./PlateFrame";

export const ACCEPTED_TYPES = ["image/png", "image/jpeg"];
/** Generous ceiling for a single slice; anything larger is not a FLAIR slice export. */
export const MAX_BYTES = 20 * 1024 * 1024;

interface Props {
  /** A file dropped onto the frame. */
  onFile: (file: File) => void;
  /** Open the page's file chooser (the page owns the input so the margin action can open it too). */
  onChoose: () => void;
  /** Rendered inside the frame while the slice is being read; the frame stays inert. */
  previewSrc?: string | null;
  /** When true the frame no longer accepts drops (a slice is already in it). */
  inert?: boolean;
}

/**
 * The empty plate frame is the drop target: the plate awaiting its figure. Same frame,
 * ticks and orientation letters as the finished plate, so the intake reads as the same
 * object, emptied. Drag-over and focus brighten the hairlines; nothing fills.
 */
export default function PlateIntake({ onFile, onChoose, previewSrc, inert = false }: Props) {
  const [over, setOver] = useState(false);
  const [focus, setFocus] = useState(false);
  const active = !inert && (over || focus);

  const accept = (files: FileList | null) => {
    const f = files?.[0];
    if (f) onFile(f);
  };
  const onDrag = (e: DragEvent, state: boolean) => {
    if (inert) return;
    e.preventDefault();
    setOver(state);
  };

  return (
    <div
      className={`${FRAME_CLASS} ${active ? "border-bone" : "border-rule-strong"}`}
      onDragOver={(e) => onDrag(e, true)}
      onDragEnter={(e) => onDrag(e, true)}
      onDragLeave={(e) => onDrag(e, false)}
      onDrop={(e) => {
        if (inert) return;
        e.preventDefault();
        setOver(false);
        accept(e.dataTransfer.files);
      }}
    >
      {previewSrc && (
        <img
          src={previewSrc}
          alt="Uploaded FLAIR slice, awaiting analysis"
          className="absolute inset-0 w-full h-full object-contain select-none"
          draggable={false}
        />
      )}

      <FrameFurniture tone={active ? "active" : "rest"} />

      {!inert && (
        <button
          type="button"
          onClick={onChoose}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          className="absolute inset-0 w-full h-full flex flex-col items-center justify-center gap-3 px-8 text-center focus-visible:outline-none"
          aria-label="Choose a FLAIR slice to analyze (PNG or JPG)"
        >
          <span
            className={`wdth-narrow uppercase tracking-label text-[0.85rem] leading-none transition-colors duration-200 ease-out ${
              active ? "text-bone" : "text-bone-dim"
            }`}
          >
            Drop a FLAIR slice
          </span>
          <span className="text-[0.85rem] leading-snug text-bone-dim">
            PNG or JPG · or <span className="text-bone underline decoration-rule-strong underline-offset-4">choose a file</span>
          </span>
        </button>
      )}

    </div>
  );
}
