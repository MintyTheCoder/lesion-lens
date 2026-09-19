import type { ReactNode } from "react";
import type { AnalysisResult } from "../../api/types";
import PlateFigure from "../plate/PlateFigure";
import BurdenKey from "./BurdenKey";
import FindingsNote from "./FindingsNote";
import ValidationTable from "./ValidationTable";

interface Props {
  result: AnalysisResult;
  /** The plate's single action, beneath the legend (Analyze another slice, or back to the case list). */
  action: ReactNode;
  /** Extra caption spans: how long the read took, and so on. */
  caption?: ReactNode;
}

/**
 * A finished plate: the landing's Plate 1 composition with the clinician's own slice, the
 * burden as the plate's key, the note as the hand-off, and the cross-dataset check last.
 * Shared by the Analyze result and a reopened case so the two never drift.
 */
export default function CaseView({ result, action, caption }: Props) {
  const stamp = new Date(result.created_at);
  return (
    <>
      <section className="border-t border-rule px-4 sm:px-8 pt-10 lg:pt-12 pb-16">
        <PlateFigure
          result={result}
          imageSrc={result.image.data_url}
          aside={<BurdenKey burden={result.burden} />}
          action={action}
          legendDetail
          emptyLegend="No white-matter lesions were detected in this slice. The plate is kept as a documented negative read."
          caption={
            <>
              {caption}
              <span className="tnum">
                {stamp.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}{" "}
                {stamp.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}
              </span>
              <span>
                model {result.model.id} · trained on {result.model.trained_on}
              </span>
            </>
          }
        />
      </section>

      <section className="border-t border-rule px-4 sm:px-8 pt-16 pb-16">
        <FindingsNote summary={result.summary} />
      </section>

      <section className="border-t border-rule px-4 sm:px-8 pt-16 pb-20">
        <ValidationTable />
      </section>
    </>
  );
}
