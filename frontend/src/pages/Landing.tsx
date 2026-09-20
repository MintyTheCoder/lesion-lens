import type { AnalysisResult } from "../api/types";
import mock from "../mocks/analysis.json";
import PlateAction from "../components/plate/PlateAction";
import PlateFigure from "../components/plate/PlateFigure";
import { HONESTY_LINE, NOT_A_DIAGNOSIS, PRODUCT_NAME } from "../brand";

// The sample slice in public/plate/. The fixture's boxes were placed on this slice's visible
// hyperintensities by hand (see public/plate/README.md); swap in the model's own result via
// save_to_demo_cache() once it runs so the caption can drop "not model output".
const HERO_SLICE = "/plate/hero-slice.png";
const hero = mock as AnalysisResult;

// Kaisey M, et al. Incidence of multiple sclerosis misdiagnosis in referrals to two academic
// centers. Mult Scler Relat Disord. 2019;30:51-56. 241 referrals; 17% (Cedars-Sinai) and 19%
// (UCLA) misdiagnosed, migraine the most common alternate diagnosis.
const KAISEY_2019 = "https://doi.org/10.1016/j.msard.2019.01.048";
// Solomon AJ, et al. The contemporary spectrum of multiple sclerosis misdiagnosis: a multicenter
// study. Neurology. 2016;87(13):1393-1399. 110 misdiagnosed patients; 33% misdiagnosed >=10 years,
// 72% received disease-modifying therapy.
const SOLOMON_2016 = "https://doi.org/10.1212/WNL.0000000000003152";

const KEY = [
  {
    figure: "18%",
    statement: "of multiple sclerosis diagnoses are wrong.",
    source: "Kaisey et al., 2019",
    href: KAISEY_2019,
  },
  {
    figure: "33%",
    statement: "stay misdiagnosed for ten years or more.",
    source: "Solomon et al., 2016",
    href: SOLOMON_2016,
  },
  {
    figure: "72%",
    statement: "of misdiagnosed patients are put on MS medication they do not need.",
    source: "Solomon et al., 2016",
    href: SOLOMON_2016,
  },
];

const CRITERIA = [
  {
    name: "Periventricular location",
    detail: "Abutting the lateral ventricles, where MS plaques characteristically form.",
  },
  {
    name: "Perpendicular elongation",
    detail: "Ovoid lesions set at right angles to the ventricle along the medullary veins: Dawson's fingers.",
  },
  {
    name: "Ovoid shape",
    detail: "Rather than the small, round, punctate foci typical of small-vessel change.",
  },
];

export default function Landing() {
  return (
    <article>
      {/* Masthead — the plate's title block. The name runs the full width one step above the key
          figures, the thesis sits under it at statement scale, and the description keeps the margin. */}
      <section className="px-4 sm:px-8 pt-16 pb-14 lg:pt-24 lg:pb-20">
        <h1 className="wdth-wide font-semibold tracking-plate leading-[0.86] text-[clamp(3.5rem,14vw,9rem)] -ml-[0.04em]">
          {PRODUCT_NAME}
        </h1>
        <div className="mt-8 lg:mt-12 grid grid-cols-1 gap-y-6 lg:grid-cols-[minmax(0,1.5fr)_minmax(21rem,1fr)] lg:gap-x-16 lg:items-start">
          <p className="text-balance font-normal tracking-plate leading-[1.15] text-[clamp(1.4rem,2.3vw,2.1rem)] max-w-[30ch]">
            A clinician’s second look at a FLAIR slice, quantified.
          </p>
          <p className="text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch] lg:pt-2">
            Each lesion is boxed, counted, and read against the established criteria that separate an{" "}
            <span className="text-bone whitespace-nowrap">MS-typical pattern</span> from a{" "}
            <span className="text-bone">nonspecific one</span>. Decision support for a clinician. Never a
            standalone diagnosis.
          </p>
        </div>
      </section>

      {/* Plate 1 — the mechanism, shown */}
      <section className="border-t border-rule px-4 sm:px-8 pt-10 lg:pt-12 pb-16">
        <PlateFigure
          result={hero}
          imageSrc={HERO_SLICE}
          sourceNote="development fixture, not model output"
          aside={
            <div>
              <h2 className="wdth-wide text-balance font-medium tracking-plate leading-[1.06] text-[clamp(1.55rem,2.05vw,2.15rem)]">
                Every white-matter lesion, boxed. Each one read against the criteria that separate{" "}
                <span className="whitespace-nowrap">MS-typical</span> from nonspecific.
              </h2>
              <p className="mt-5 text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[44ch]">
                Upload a FLAIR slice. Get back the lesion count, the burden, a pattern flag for every lesion with
                the reasons behind it, and a plain-language note you can chart.
              </p>
            </div>
          }
          action={<PlateAction to="/analyze">Analyze a slice</PlateAction>}
        />
      </section>

      {/* The key — the numbers behind a wrong diagnosis */}
      <section className="border-t border-rule px-4 sm:px-8 pt-20 pb-20">
        <h2 className="wdth-wide text-balance font-medium tracking-plate leading-[1.08] text-[clamp(1.6rem,2.4vw,2.25rem)] max-w-[24ch]">
          The numbers behind a wrong diagnosis
        </h2>
        <ol className="mt-12 border-t border-rule">
          {KEY.map((k) => (
            <li
              key={k.figure}
              className="border-b border-rule py-7 md:py-9 grid gap-x-12 gap-y-3 md:grid-cols-[auto_minmax(0,1fr)] items-start"
            >
              <span className="wdth-wide tnum font-semibold tracking-plate leading-[0.86] text-[clamp(3.75rem,8vw,6rem)] md:min-w-[4.2ch]">
                {k.figure}
              </span>
              <div className="md:pt-1">
                <p className="text-pretty leading-[1.15] tracking-plate text-[clamp(1.4rem,2.3vw,2.1rem)] max-w-[26ch]">{k.statement}</p>
                <p className="mt-3 wdth-narrow uppercase tracking-label text-[0.72rem] text-bone-dim">
                  <a
                    href={k.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline decoration-rule underline-offset-4 hover:text-bone hover:decoration-bone transition-colors"
                  >
                    {k.source}
                  </a>
                </p>
              </div>
            </li>
          ))}
        </ol>
        <p className="mt-10 text-pretty text-[1.1rem] leading-relaxed max-w-[62ch]">
          The root cause is the over-calling of nonspecific white-matter lesions as MS-typical. Migraine is the
          most common mimic, and it disproportionately affects women. Judging whether a pattern looks MS-typical is
          today a subjective visual call with no quantified baseline; that is where the 18% comes from.
        </p>
      </section>

      {/* What the flags encode — proof, and the honesty rule */}
      <section className="border-t border-rule px-4 sm:px-8 pt-20 pb-20">
        <div className="grid grid-cols-1 gap-y-10 lg:grid-cols-[minmax(0,1.5fr)_minmax(21rem,1fr)] lg:gap-x-16">
          <div>
            <h2 className="wdth-wide text-balance font-medium tracking-plate leading-[1.08] text-[clamp(1.6rem,2.4vw,2.25rem)] max-w-[24ch]">
              What the pattern flag encodes
            </h2>
            <ol className="mt-10 border-t border-rule max-w-[64ch]">
              {CRITERIA.map((c, i) => (
                <li key={c.name} className="border-b border-rule py-5 grid grid-cols-[2.25rem_minmax(0,1fr)] gap-x-3">
                  <span className="tnum text-[1.5rem] leading-none font-medium pt-[2px]">{i + 1}</span>
                  <span>
                    <span className="block text-[1.1rem] leading-tight font-medium text-typical">{c.name}</span>
                    <span className="block mt-1.5 text-pretty text-[0.95rem] leading-snug text-bone-dim">
                      {c.detail}
                    </span>
                  </span>
                </li>
              ))}
            </ol>
            <p className="mt-8 text-pretty text-[0.95rem] leading-relaxed text-bone-dim max-w-[62ch]">
              Lesions meeting these criteria are flagged{" "}
              <span className="text-typical">MS-typical pattern</span>. Small, round, deep white-matter foci with
              no ventricular orientation are flagged{" "}
              <span className="text-atypical">atypical or nonspecific pattern</span>, the appearance also seen in
              migraine and small-vessel disease. Detection is a fine-tuned RF-DETR model; the flag is a rule layer
              on top of it, so every reason is printed beside every lesion.
            </p>
          </div>

          <aside className="lg:self-start lg:pt-2">
            <p className="text-pretty font-medium tracking-plate leading-[1.15] text-[clamp(1.4rem,2.3vw,2.1rem)]">
              {HONESTY_LINE}
            </p>
            <p className="mt-5 text-pretty text-[0.95rem] leading-relaxed text-bone-dim">
              There is no migraine-patient data in either dataset. The flag applies established radiological
              heuristics to detected lesions; it is not a model trained or tested on confirmed migraine cases, and
              its output is reported descriptively, never as a performance figure.
            </p>
          </aside>
        </div>
      </section>

      {/* Footnote and the action, restated. Nothing after this. */}
      <footer className="border-t border-rule px-4 sm:px-8 pt-12 pb-16">
        <div className="grid grid-cols-1 gap-y-8 lg:grid-cols-[minmax(0,1.2fr)_minmax(26rem,1fr)] lg:gap-x-16 items-end">
          <dl className="grid gap-y-4 text-[0.85rem] leading-snug max-w-[64ch]">
            <div className="grid sm:grid-cols-[9rem_minmax(0,1fr)] gap-x-6 gap-y-1">
              <dt className="wdth-narrow uppercase tracking-label text-[0.72rem] text-bone-dim pt-[2px]">Trained on</dt>
              <dd>MS3SEG, about 2,000 annotated FLAIR slices; abnormal white-matter class converted to boxes.</dd>
            </div>
            <div className="grid sm:grid-cols-[9rem_minmax(0,1fr)] gap-x-6 gap-y-1">
              <dt className="wdth-narrow uppercase tracking-label text-[0.72rem] text-bone-dim pt-[2px]">Validated on</dt>
              <dd>MSLesSeg, 115 multi-hospital scans, sealed from training. Reported as precision and false positives per scan.</dd>
            </div>
            <div className="grid sm:grid-cols-[9rem_minmax(0,1fr)] gap-x-6 gap-y-1">
              <dt className="wdth-narrow uppercase tracking-label text-[0.72rem] text-bone-dim pt-[2px]">Use</dt>
              <dd className="text-bone">{NOT_A_DIAGNOSIS}</dd>
            </div>
          </dl>
          <div className="w-full lg:justify-self-end">
            <PlateAction to="/analyze" size="hero">
              Analyze a slice
            </PlateAction>
          </div>
        </div>
      </footer>
    </article>
  );
}
