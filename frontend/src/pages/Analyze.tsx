import { useCallback, useEffect, useRef, useState } from "react";
import { analyze } from "../api/client";
import type { AnalysisResult } from "../api/types";
import mock from "../mocks/analysis.json";
import { SAMPLES, type SampleSlice } from "../samples";
import CaseView from "../components/case/CaseView";
import PlateAction from "../components/plate/PlateAction";
import { PLATE_GRID, PlateCaption } from "../components/plate/PlateFrame";
import PlateIntake, { ACCEPTED_TYPES, MAX_BYTES } from "../components/plate/PlateIntake";

/**
 * One plate, four states. The intake is the plate with no figure; processing is the figure
 * with an empty legend; the result is the landing's Plate 1 with the clinician's slice; an
 * error keeps the slice in the frame and names the problem where the legend would be.
 */
type Phase =
  | { kind: "idle"; rejection: string | null }
  | { kind: "processing"; file: File; url: string; startedAt: number }
  | { kind: "done"; result: AnalysisResult; elapsedMs: number }
  | { kind: "error"; file: File; url: string; message: string; retryable: boolean };

/** Map what the backend actually returns (see backend/app/routes/analyze.py) to a sentence and a recovery. */
function describeFailure(e: unknown): { message: string; retryable: boolean } {
  const text = e instanceof Error ? e.message : String(e);
  const status = Number.parseInt(text, 10);
  if (status === 503) {
    return {
      message:
        "The model service did not respond, and this slice is not in the rehearsed set. Check the connection and try again, or start from a rehearsed slice.",
      retryable: true,
    };
  }
  if (status === 400 || status === 415) {
    return {
      message: "This file could not be read as a FLAIR slice. Upload a PNG or JPG axial slice.",
      retryable: false,
    };
  }
  if (Number.isFinite(status)) {
    return { message: `The analysis service returned an error (${text}). Try again.`, retryable: true };
  }
  return {
    message: "The analysis service is unreachable. Check that the backend is running and try again.",
    retryable: true,
  };
}

function rejectionFor(file: File): string | null {
  if (!ACCEPTED_TYPES.includes(file.type)) {
    const ext = file.name.includes(".") ? file.name.split(".").pop()?.toUpperCase() : null;
    return `That is ${ext ? `a ${ext} file` : "not an image"}. Upload a PNG or JPG FLAIR slice.`;
  }
  if (file.size > MAX_BYTES) {
    return `That file is ${(file.size / 1048576).toFixed(0)} MB, larger than a single slice export. Upload one FLAIR slice as PNG or JPG.`;
  }
  return null;
}

export default function Analyze() {
  const [phase, setPhase] = useState<Phase>({ kind: "idle", rejection: null });
  const [now, setNow] = useState(0);
  const [samples, setSamples] = useState<SampleSlice[] | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const urlRef = useRef<string | null>(null);
  const lastFile = useRef<File | null>(null);

  // One object URL at a time: retrying the same file keeps its URL, a new file revokes the old one.
  const holdUrl = (file: File) => {
    if (lastFile.current === file && urlRef.current) return urlRef.current;
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    urlRef.current = URL.createObjectURL(file);
    lastFile.current = file;
    return urlRef.current;
  };
  useEffect(
    () => () => {
      if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    },
    [],
  );

  const submit = useCallback(async (file: File) => {
    const rejection = rejectionFor(file);
    if (rejection) {
      setPhase({ kind: "idle", rejection });
      return;
    }
    const url = holdUrl(file);
    const startedAt = performance.now();
    setPhase({ kind: "processing", file, url, startedAt });
    try {
      const result = await analyze(file);
      setPhase({ kind: "done", result, elapsedMs: performance.now() - startedAt });
    } catch (e) {
      setPhase({ kind: "error", file, url, ...describeFailure(e) });
    }
  }, []);

  // Elapsed counter while the hosted model reads the slice. Honest: one request, no fake phases.
  useEffect(() => {
    if (phase.kind !== "processing") return;
    const t = window.setInterval(() => setNow(performance.now()), 100);
    return () => window.clearInterval(t);
  }, [phase.kind]);

  // Hide sample entries whose file is not in public/samples yet; the list disappears when none are.
  useEffect(() => {
    let cancelled = false;
    Promise.all(
      SAMPLES.map(async (s) => {
        try {
          const res = await fetch(s.file, { method: "HEAD" });
          return res.ok && (res.headers.get("content-type") ?? "").startsWith("image/") ? s : null;
        } catch {
          return null;
        }
      }),
    ).then((found) => {
      if (!cancelled) setSamples(found.filter((s): s is SampleSlice => s !== null));
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const runSample = async (s: SampleSlice) => {
    try {
      const blob = await fetch(s.file).then((r) => r.blob());
      const name = s.file.split("/").pop() ?? "sample.png";
      submit(new File([blob], name, { type: blob.type || "image/png" }));
    } catch {
      setPhase({ kind: "idle", rejection: "That rehearsed slice could not be loaded." });
    }
  };

  const reset = () => {
    setPhase({ kind: "idle", rejection: null });
    window.scrollTo({ top: 0 });
  };

  const chooseFile = () => inputRef.current?.click();

  return (
    <article>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(",")}
        hidden
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) submit(f);
          e.target.value = "";
        }}
      />

      {/* Title row: the page names itself once; the plate below carries the state. */}
      <section className="px-4 sm:px-8 pt-12 pb-10 lg:pt-16 lg:pb-12">
        <div className={`${PLATE_GRID} lg:items-start`}>
          <h1 className="wdth-wide font-medium tracking-plate leading-[1.06] text-[clamp(1.6rem,2.4vw,2.25rem)]">
            Analyze a slice
          </h1>
          <p className="text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch] lg:pt-1">
            Upload an axial FLAIR slice as PNG or JPG. Every white-matter lesion is boxed and counted, and each is
            flagged with the reasons behind the flag.
          </p>
        </div>
      </section>

      {phase.kind === "done" ? (
        <>
          <CaseView
            result={phase.result}
            action={<PlateAction onClick={reset}>Analyze another slice</PlateAction>}
            caption={<span className="tnum">read in {(phase.elapsedMs / 1000).toFixed(1)} s</span>}
          />
          <footer className="border-t border-rule px-4 sm:px-8 pt-10 pb-16">
            <div className="grid grid-cols-1 gap-y-8 lg:grid-cols-[minmax(0,1.5fr)_minmax(21rem,1fr)] lg:gap-x-16 items-end">
              <p className="text-pretty text-[0.85rem] leading-snug text-bone-dim max-w-[64ch]">
                Detection is a fine-tuned RF-DETR model; the pattern flag is a rule layer on top of it, so every
                reason is printed beside every lesion. Reopen this case any time from History.
              </p>
              <div className="lg:justify-self-end">
                <PlateAction size="quiet" onClick={reset}>
                  Analyze another slice
                </PlateAction>
              </div>
            </div>
          </footer>
        </>
      ) : (
        <section className="border-t border-rule px-4 sm:px-8 pt-10 lg:pt-12 pb-16">
          <div className={`${PLATE_GRID} lg:grid-rows-[auto_auto_1fr]`}>
            {/* Margin head: what the plate is waiting for, doing, or could not do */}
            <div className="lg:col-start-2 lg:row-start-1 order-1">
              {phase.kind === "idle" && (
                <>
                  <h2 className="wdth-wide text-balance font-medium tracking-plate leading-[1.06] text-[clamp(1.55rem,2.05vw,2.15rem)]">
                    Drop a FLAIR slice into the frame, or start from a rehearsed one.
                  </h2>
                  <p className="mt-5 text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch]">
                    The read takes a few seconds. What comes back: every lesion boxed and numbered, the lesion burden,
                    a pattern flag with the reasons behind it, and a findings note you can chart.
                  </p>
                </>
              )}
              {phase.kind === "processing" && (
                <div role="status" aria-live="polite">
                  <div className="flex items-baseline justify-between gap-6">
                    <span className="wdth-narrow uppercase tracking-label text-[0.85rem] leading-none text-bone">
                      Reading slice
                    </span>
                    <span className="tnum text-[1.5rem] leading-none font-medium">
                      {(Math.max(0, now - phase.startedAt) / 1000).toFixed(1)}
                      <span className="text-[0.85rem] text-bone-dim"> s</span>
                    </span>
                  </div>
                  <p className="mt-5 text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch]">
                    Detecting white-matter lesions and reading each one against the pattern criteria.
                  </p>
                </div>
              )}
              {phase.kind === "error" && (
                <div role="alert">
                  <span className="wdth-narrow uppercase tracking-label text-[0.85rem] leading-none text-bone">
                    The read did not complete
                  </span>
                  <p className="mt-5 text-pretty text-[1.1rem] leading-relaxed max-w-[44ch]">{phase.message}</p>
                  {import.meta.env.DEV && (
                    <div className="mt-5">
                      <PlateAction
                        size="quiet"
                        onClick={() => setPhase({ kind: "done", result: mock as AnalysisResult, elapsedMs: 0 })}
                      >
                        Load development fixture
                      </PlateAction>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Figure: the frame, empty or holding the slice */}
            <figure className="lg:col-start-1 lg:row-start-1 lg:row-span-3 order-2 min-w-0">
              <PlateIntake
                onFile={submit}
                onChoose={chooseFile}
                previewSrc={phase.kind === "idle" ? null : phase.url}
                inert={phase.kind !== "idle"}
              />
              <PlateCaption plate="Plate —">
                <span>FLAIR, axial</span>
                {phase.kind === "idle" && <span>awaiting slice</span>}
                {phase.kind === "processing" && (
                  <>
                    <span className="truncate max-w-[24ch]">{phase.file.name}</span>
                    <span>processing</span>
                  </>
                )}
                {phase.kind === "error" && (
                  <>
                    <span className="truncate max-w-[24ch]">{phase.file.name}</span>
                    <span>read failed</span>
                  </>
                )}
              </PlateCaption>
            </figure>

            {/* Margin list: a rejection, then the rehearsed slices */}
            <div className="lg:col-start-2 lg:row-start-2 order-3 self-start">
              {phase.kind === "idle" && phase.rejection && (
                <p role="alert" className="border-t border-rule pt-4 pb-5 text-[0.95rem] leading-relaxed text-pretty max-w-[44ch]">
                  {phase.rejection}
                </p>
              )}
              <SampleList
                samples={samples}
                dimmed={phase.kind === "processing"}
                onPick={runSample}
              />
            </div>

            {/* Margin action */}
            <div className="lg:col-start-2 lg:row-start-3 order-4 self-start mt-2">
              {phase.kind === "idle" && <PlateAction onClick={chooseFile}>Choose a file</PlateAction>}
              {phase.kind === "error" &&
                (phase.retryable ? (
                  <PlateAction onClick={() => submit(phase.file)}>Try again</PlateAction>
                ) : (
                  <PlateAction onClick={chooseFile}>Choose another file</PlateAction>
                ))}
            </div>
          </div>
        </section>
      )}
    </article>
  );
}

interface SampleListProps {
  /** `null` while availability is still being checked. */
  samples: SampleSlice[] | null;
  dimmed: boolean;
  onPick: (s: SampleSlice) => void;
}

/** The rehearsed slices as a ruled list, numbered like a legend. Doubles as the offline path via the demo cache. */
function SampleList({ samples, dimmed, onPick }: SampleListProps) {
  if (samples === null) return null;
  if (samples.length === 0) {
    return (
      <p className="border-t border-rule pt-4 text-[0.85rem] leading-snug text-bone-faint max-w-[44ch] text-pretty">
        No rehearsed slices yet. Place them in frontend/public/samples (see the README there) and they will be listed
        here.
      </p>
    );
  }
  return (
    <div
      className={`transition-opacity duration-300 ease-out ${dimmed ? "opacity-[0.38] pointer-events-none" : ""}`}
      aria-hidden={dimmed}
    >
      <h3 className="wdth-narrow uppercase tracking-label text-[0.72rem] leading-none text-bone-dim mb-3">
        Rehearsed slices
      </h3>
      <ol className="border-t border-rule">
        {samples.map((s, i) => (
          <li key={s.file} className="border-b border-rule">
            <button
              type="button"
              onClick={() => onPick(s)}
              disabled={dimmed}
              className="group w-full text-left grid grid-cols-[2.5rem_minmax(0,1fr)_auto] gap-x-3 py-3.5 items-start"
            >
              <span className="tnum text-[1.5rem] leading-none font-medium">{i + 1}</span>
              <span className="min-w-0">
                <span className="block text-[1.1rem] leading-tight font-medium">{s.name}</span>
                <span className="block mt-1.5 text-[0.95rem] leading-snug text-bone-dim text-pretty">{s.description}</span>
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
    </div>
  );
}
