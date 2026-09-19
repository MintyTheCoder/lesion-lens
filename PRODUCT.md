# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primary: radiologists and neurologists** reading a FLAIR MRI slice, at the moment they must judge whether a white-matter lesion pattern looks MS-typical or nonspecific. They are advising hospital staff or writing a referral/charting note. The job is a *second look*: a quantified, documentable check on a call that today is purely visual and subjective.

**Immediate evaluators:** VTHacks 14 judges watching a timed 4-minute pitch and live demo. They are not the design target — the interface is designed for the clinician, and judges assess whether it would work for one. Judging tracks: MLH Best Use of Gemini API, Best Use of MongoDB Atlas; general Best Ut Prosim, Best DEI Hack, Overall.

**Never a user:** the patient. Output is never shown to the patient.

## Product Purpose

Upload a FLAIR MRI slice → every white-matter lesion is boxed, each lesion is flagged **MS-typical pattern** vs **atypical/nonspecific pattern**, and the clinician gets a lesion count + total area (burden score), a plain-language summary of findings, and a precision / false-positive readout including performance on a dataset the model never trained on.

Why it exists: MS misdiagnosis runs ~18% (Kaisey et al.). 72% of misdiagnosed patients are put on MS medication they don't need; ~33% stay misdiagnosed 10+ years (Solomon et al. 2016). The root cause is over-calling nonspecific white-matter lesions as MS-typical. Migraine is the most common mimic and disproportionately affects women.

Success: the clinician's subjective read becomes a repeatable, quantified one — exact count, area, per-lesion flag — usable directly for referral notes or charting, and the cross-hospital validation panel answers "does this hold outside the site it was trained on?"

## Positioning

Lesion *detection* already works; this product adds the two missing pieces:

1. A **pattern layer** that encodes established radiological criteria (elongation and orientation relative to ventricles — Dawson's fingers; periventricular vs. juxtacortical vs. deep white-matter location; ovoid shape) to flag each detected lesion as MS-typical vs. atypical/nonspecific.
2. **Cross-dataset validation** — trained on MS3SEG, validated on MSLesSeg (115 multi-hospital scans, sealed from training).

**Framing that must stay prominent on every screen:** decision support for a doctor's second look. Never a standalone diagnosis. Sits alongside McDonald criteria; does not replace judgment.

## Operating Context

- **Clinical flow:** clinician has a FLAIR slice as PNG/JPG → uploads → waits a few seconds for hosted inference → reviews annotated slice, per-lesion table, burden, summary, validation panel → may reopen past cases from History.
- **Demo flow (pitch):** 0:00 patient story + Kaisey/Solomon stats → 0:45 "detectors exist; we built the pattern layer + cross-hospital validation" → 1:15–3:00 live demo (upload, detections with flags, precision/FP rate holding on MSLesSeg) → 3:00 workflow fit + honesty line verbatim → 3:30 close on the patient. Demo cases: one clean detection, one clear pattern-flag contrast, one cross-dataset.
- **Infrastructure:** inference is an HTTP call to Roboflow's hosted API (free plan; weights cannot be downloaded), so the demo depends on Wi-Fi. Backend falls back to precomputed `backend/app/fixtures/demo_cache/` for rehearsed scans. `USE_MOCK_INFERENCE=1` (default) returns a canned fixture so the UI works with no keys and no model.
- **Graceful degradation:** no Gemini key → template summary; no MongoDB URI → in-memory store.
- **Team:** three workstreams (`data/`, `ml/`, `backend/`+`frontend/`) on three branches; this user owns backend + frontend.

## Capabilities and Constraints

**Surfaces (confirmed):**
- Landing page — in scope. Three jobs in order: one-line app highlight; the misdiagnosis numbers (18% / 72% / 33% / root cause + migraine-mimic line); single CTA → Analyze.
- Analyze — upload dropzone → annotated slice with SVG box overlay (MS-typical vs atypical color-coded) → burden card → per-lesion table (row click ↔ viewer selection) → summary card with the fixed "decision support, not a diagnosis" line → validation panel.
- History — saved cases from MongoDB; click to reopen.

**Data contract:** `AnalysisResult` (`backend/app/schemas.py` ↔ `frontend/src/api/types.ts` ↔ `backend/app/fixtures/mock_analysis.json`); change all three together. Per lesion: bbox `[x,y,w,h]` in preprocessed-image pixels, confidence, area_px, pattern, features (elongation, orientation_deg, location, ovoid_score), reasons[]. Burden: lesion_count, total_area_px, total_area_pct, ms_typical_count, atypical_count. Validation: per-dataset precision, recall, fp_per_scan, atypical_pct + note.

**Terminology (use exactly):** "MS-typical pattern" / "atypical or nonspecific pattern"; "lesion burden"; "periventricular / juxtacortical / deep white matter"; "FLAIR slice"; "precision" and "false positives per scan" (never "accuracy" as the headline metric). Pattern-layer results are reported descriptively ("X% of detected lesions flagged atypical") — there is no ground truth to validate the flag against, so never present it as an accuracy figure.

**Existing UI conventions (incumbent, not binding beyond function):** orange = MS-typical, sky = atypical box colors; dark slate header; Tailwind 3 with no custom theme yet.

**Fallback order if time runs out:** (1) cut the heuristic pattern layer → detection + burden only; (2) cut UI polish before model reliability; (3) cut MongoDB before Gemini.

**Undecided:** product name (see Brand Commitments). Whether the landing page is `/` with Analyze at `/analyze` (FLOW.md) or Analyze stays at `/` (current App.tsx).

## Brand Commitments

- **Name — undecided.** Two candidates in the repo: **"Val United"** (README title, repo name) and **"MS Lesion Specificity"** (app header, CLAUDE.md). Record both; do not invent a third. Whichever is not the name may serve as a descriptor.
- **Voice:** plain clinical language. Summaries are 3–5 sentences, no bullets, written so a radiologist can paste them into a note.
- **Honesty rule — binding on every piece of UI copy and every Gemini prompt:**
  - ✅ "We encode established diagnostic criteria used to distinguish MS-typical lesions from nonspecific ones."
  - ❌ Never "trained to detect migraine" / "distinguishes MS from migraine." There is no migraine-patient data in either dataset.
- **Fixed line on the summary and in the app header:** decision support for clinician review — not a diagnosis.
- No logo or visual identity exists yet.

## Evidence on Hand

- **Sample FLAIR slices:** the user has sample scans to use in the UI (path not yet recorded — ask before building a surface that needs them; do not scrape MRI images from any other source).
- **Citations (real, cite in UI fine print and README):** Kaisey et al. (~18% misdiagnosis); Solomon et al. 2016 (72% on unneeded MS medication; ~33% misdiagnosed 10+ years).
- **Datasets (public, cite both):** MS3SEG (~2,000 annotated FLAIR slices, training); MSLesSeg (115 multi-hospital scans, validation only).
- **Mock result:** `backend/app/fixtures/mock_analysis.json` / `frontend/src/mocks/analysis.json` — a canned `AnalysisResult` for building without the model.
- **Validation numbers:** `ml/results/validation.json` currently holds placeholder zeros. Real precision / FP-per-scan figures arrive from the ml teammate. **Do not fabricate metrics, testimonials, hospital partners, or clinical outcomes.** Hide or clearly label the validation panel until real numbers exist.

## Product Principles

1. **Second look, never the verdict.** Every surface carries the decision-support framing; nothing reads as a diagnosis or a patient-facing result.
2. **Quantify what was subjective.** Count, area, per-lesion flag, and the reasons behind each flag are the product — show them explicitly and make them documentable.
3. **Honesty over pitch.** Say exactly what the pattern layer is (encoded criteria) and what the metrics are (precision, FP per scan, descriptive atypical %). Never imply migraine detection.
4. **Trust travels with validation.** The cross-hospital result is the strongest moment; give it a real place, but only with real numbers.
5. **Fits the workflow.** Read alongside McDonald criteria, usable for a referral note, fast enough to be part of a real review.

## Accessibility & Inclusion

The product addresses a misdiagnosis pattern that disproportionately affects women (migraine as MS mimic) — this is part of the DEI-track framing and should be stated factually, not dramatized. No specific accessibility standard has been set; clinical UI should at minimum not rely on color alone to distinguish MS-typical from atypical lesions (color-blind-safe pairing plus a text/shape cue).
