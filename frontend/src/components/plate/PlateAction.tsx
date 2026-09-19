import { Link } from "react-router-dom";
import type { ReactNode } from "react";

interface Props {
  to: string;
  children: ReactNode;
  /** `large` is the plate's own action; `quiet` is the restatement at the foot of the page. */
  size?: "large" | "quiet";
}

/** The plate's action: a ruled box that fills to bone on hover. Nothing else on the page fills. */
export default function PlateAction({ to, children, size = "large" }: Props) {
  const pad = size === "large" ? "px-6 py-4 text-[0.85rem]" : "px-4 py-3 text-[0.75rem]";
  return (
    <Link
      to={to}
      className={`group inline-flex items-center justify-between gap-6 border border-bone/70 text-bone wdth-narrow uppercase tracking-label leading-none transition-colors duration-200 ease-out hover:bg-bone hover:text-plate focus-visible:bg-bone focus-visible:text-plate ${pad} ${
        size === "large" ? "w-full" : ""
      }`}
    >
      <span>{children}</span>
      <svg
        width="22"
        height="12"
        viewBox="0 0 22 12"
        fill="none"
        aria-hidden="true"
        className="shrink-0 transition-transform duration-300 ease-out group-hover:translate-x-1"
      >
        <path d="M0 6h20M15 1l5 5-5 5" stroke="currentColor" strokeWidth="1.25" strokeLinecap="square" />
      </svg>
    </Link>
  );
}
