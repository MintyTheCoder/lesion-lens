import { Link } from "react-router-dom";
import type { ReactNode } from "react";

interface Props {
  to: string;
  children: ReactNode;
  /**
   * `large` is the plate's own action; `quiet` is a small restatement;
   * `hero` is the page-ending call to action the pitch walks through.
   */
  size?: "large" | "quiet" | "hero";
}

/** The plate's action: a ruled box that fills to bone on hover. Nothing else on the page fills. */
export default function PlateAction({ to, children, size = "large" }: Props) {
  const pad =
    size === "hero"
      ? "px-8 py-7 sm:px-10 sm:py-8 text-[clamp(1.15rem,2vw,1.6rem)] w-full"
      : size === "large"
        ? "px-6 py-4 text-[0.85rem] w-full"
        : "px-4 py-3 text-[0.75rem]";
  const arrow = size === "hero" ? { width: 40, height: 22, viewBox: "0 0 40 22", d: "M0 11h37M28 2l9 9-9 9", stroke: 1.5 } : { width: 22, height: 12, viewBox: "0 0 22 12", d: "M0 6h20M15 1l5 5-5 5", stroke: 1.25 };
  return (
    <Link
      to={to}
      className={`group inline-flex items-center justify-between gap-6 border border-bone/70 text-bone wdth-narrow uppercase tracking-label leading-none transition-colors duration-200 ease-out hover:bg-bone hover:text-plate focus-visible:bg-bone focus-visible:text-plate ${pad}`}
    >
      <span>{children}</span>
      <svg
        width={arrow.width}
        height={arrow.height}
        viewBox={arrow.viewBox}
        fill="none"
        aria-hidden="true"
        className="shrink-0 transition-transform duration-300 ease-out group-hover:translate-x-1"
      >
        <path d={arrow.d} stroke="currentColor" strokeWidth={arrow.stroke} strokeLinecap="square" />
      </svg>
    </Link>
  );
}
