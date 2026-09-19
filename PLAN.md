# VTHacks 14 — MS Lesion Specificity: Project Brief

**Updated:** 2026-09-19
**Locked:** RF-DETR-B + Roboflow architecture · Option B (heuristic lesion-pattern layer)

---

## 1. The Build

**Problem.** MS misdiagnosis runs ~18% (Kaisey et al.) and persists: 72% of misdiagnosed patients are put on MS medication they don't need, ~33% stay misdiagnosed 10+ years (Solomon et al. 2016). Root cause is over-calling nonspecific white matter lesions as MS-typical. Migraine is the most common mimic pattern, and disproportionately affects women.

**Product.** Web app for clinicians. Upload a FLAIR MRI slice → get back:

- Annotated image, every white-matter lesion boxed
- Per-lesion flag: **MS-typical pattern** vs **atypical/nonspecific pattern**
- Lesion count + total area (burden score)
- Plain-language summary of findings
- Precision / false-positive readout, including performance on a dataset the model never trained on

**Flow.** Upload → RF-DETR inference (boxes + confidence) → heuristic pattern scoring per lesion → burden metrics → Gemini plain-language summary → save case to MongoDB → UI renders annotated image, burden score, explanation, validation panel.

**Framing (keep prominent):** decision support for a doctor's second look. Never shown to the patient, never a standalone diagnosis. This preempts most safety questions in Q&A.

---

## 2. Value to the Clinician

Judging whether a lesion pattern looks "MS-typical" is currently a subjective visual call with no quantified baseline — which is exactly where the 18% comes from.

| What changes                     | Why it matters                                                                   |
| -------------------------------- | -------------------------------------------------------------------------------- |
| Subjective read → quantified one | Exact count, area, per-lesion flag; repeatable and documentable                  |
| Second opinion at decision point | Atypical flag = concrete prompt to consider migraine, small-vessel disease       |
| Burden tracked over time         | Rising vs. stable count/area becomes a number, not an eyeball comparison         |
| Review time saved                | Counting, sizing, pattern-judging returned in inference time                     |
| Plain-language output            | Usable directly for referral notes or charting                                   |
| Cross-hospital trust             | MSLesSeg validation answers "does this hold outside the site it was trained on?" |
| Fits existing workflow           | Sits alongside McDonald criteria, doesn't replace judgment                       |

---

## 3. Architecture

Not replicating MS3SEG's 4-class dense tri-mask segmentation. Instead:

1. Source lesion masks — MS3SEG (abnormal WMH class) and/or MSLesSeg (binary masks)
2. Masks → bounding boxes via connected-component extraction (one blob = one box)
3. OpenCV preprocessing — slice normalization, CLAHE contrast, consistent resize/pad
4. Export to COCO via Roboflow, fine-tune RF-DETR-B for lesion instance detection
5. **Heuristic pattern layer (locked):** per-lesion geometric features known to separate MS-typical from vascular/nonspecific WMH — elongation and orientation relative to ventricles (Dawson's fingers), periventricular vs. subcortical location, ovoid shape
6. Burden signal — lesion count + total box area per scan
7. Cross-dataset check — train on MS3SEG, infer on MSLesSeg

Chosen over U-Net segmentation because RF-DETR + Roboflow is what the team already knows — protects timeline given the added heuristic scope.

---

## 4. Honesty Rule — Non-Negotiable

There is **no migraine-patient data** in MS3SEG or MSLesSeg. The pattern flag applies established radiological heuristics to detected lesions. It is not a model trained or tested on confirmed migraine-mimic cases.

> ✅ **Say:** "We encode established diagnostic criteria used to distinguish MS-typical lesions from nonspecific ones."
>
> ❌ **Never say:** "We trained this to detect migraine" / "our model distinguishes MS from migraine."

Every team member rehearses this verbatim. It is the single most likely judge question — it's the gap between the misdiagnosis-stat pitch and what the system technically does.

---

## 5. Data

| Dataset  | Role            | Detail                                                                                  |
| -------- | --------------- | --------------------------------------------------------------------------------------- |
| MS3SEG   | Training        | ~2,000 annotated FLAIR slices, tri-mask labels (abnormal WMH class), converted to boxes |
| MSLesSeg | Validation only | 115 scans, multi-hospital, binary lesion masks — untouched during training              |

Both public, no access request. Do not scrape MRI images from any other source. Cite both in the README and in deck fine print — costs nothing, avoids an awkward pause.

---

## 6. Build Steps

**Phase 1 — Data pipeline**
Acquire both datasets → load NIfTI volumes with `nibabel` → masks to boxes via connected components → OpenCV preprocessing → export COCO, upload to Roboflow → split train/val, keep MSLesSeg sealed.

**Phase 2 — Model training**
Fine-tune RF-DETR-B from pretrained checkpoint; confirm the pipeline runs on a small subset first. Checkpoint by **validation precision, not accuracy**. Wrap in an inference function (scan → boxes + confidence + count/area). Confirm latency is demo-fast.

**Phase 3 — Heuristic pattern layer**
Extract geometric features per detected lesion (orientation/elongation vs. ventricles, periventricular vs. subcortical, shape). Build the rule-based MS-typical/atypical classifier — feature-engineered, not separately trained, since there's no labeled migraine data. Integrate flags into inference output.

**Phase 4 — Cross-dataset validation**
One batch script: trained model + heuristic layer over MSLesSeg. Compute precision and per-scan false-positive rate on both held-out MS3SEG and MSLesSeg. Log to a table — this is the validation panel and the strongest demo moment.

**Phase 5 — Backend + Gemini**
One FastAPI/Flask endpoint: upload → inference → JSON (detections + flags + burden). Feed into Gemini for plain-language explanation using Section 4 phrasing exactly. MongoDB Atlas for case metadata, results, flags, explanation.

**Phase 6 — Frontend**
Upload flow → annotated image color-coded by pattern flag, count/area summary, Gemini explanation → validation panel front and center. Polish last.

**Phase 7 — Integration + rehearsal**
End-to-end test on several real scans. Pick 2–3 demo cases: one clean detection, one clear pattern-flag contrast, one cross-dataset. Rehearse the 4-minute pitch timed, with the Section 4 answer verbatim.

> **Checkpoint discipline:** if the core detector isn't training reliably by ~1/3 through build time, cut Phase 3 and ship detection + burden tracking only. A working detector beats a broken two-layer system.

---

## 7. Efficiency Rules

- Fine-tune from RF-DETR-B's checkpoint, never train from scratch
- Test on a reduced subset before any full training run
- Verify inference speed before judging, not during
- Lean backend: one endpoint
- Batch the validation run — one script over all of MSLesSeg
- Build Phase 3 only after the detector is confirmed working; it depends on detection output

---

## 8. Tech Stack

| Tool                          | Job                              |
| ----------------------------- | -------------------------------- |
| MS3SEG                        | Training data                    |
| MSLesSeg                      | Cross-dataset validation         |
| OpenCV                        | Normalization, CLAHE, resize/pad |
| RF-DETR-B + Roboflow          | Lesion instance detection        |
| Geometric feature engineering | MS-typical vs. atypical flagging |
| FastAPI / Flask               | Backend API                      |
| Gemini API                    | Plain-language explanation       |
| MongoDB Atlas                 | Case storage                     |
| React (or similar)            | Frontend                         |

---

## 9. Metrics

**Headline:** precision and per-scan false-positive rate — not accuracy.

- Precision = true lesions detected / all lesions detected
- FP rate per scan = nonspecific lesions wrongly flagged, averaged per scan

**Secondary:** lesion count + total area per scan (burden).

**Pattern layer:** reported descriptively ("X% of detected lesions flagged atypical"). Not an accuracy metric — no ground truth to validate against.

---

## 10. Tracks

- **Sponsor:** none
- **MLH:** Best Use of Gemini API, Best Use of MongoDB Atlas
- **General:** Best Ut Prosim, Best DEI Hack, Overall

---

## 11. Pitch (4 min)

| Time      | Beat                                                                                                                                                              |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:45 | Patient gets an MRI, misdiagnosed with MS — it was migraine. Cite Kaisey/Solomon.                                                                                 |
| 0:45–1:15 | Detectors already work. We built the two missing pieces: a pattern layer using established criteria, and cross-hospital validation nobody's done on this dataset. |
| 1:15–3:00 | Live demo — upload, detections with flags, precision/FP rate, holding up on MSLesSeg.                                                                             |
| 3:00–3:30 | Workflow fit (Section 2) + the Section 4 honesty line, stated exactly.                                                                                            |
| 3:30–4:00 | Close on the patient from the opener.                                                                                                                             |

---

## 12. Fallback Order

1. Cut the heuristic pattern layer → detection + burden tracking only (fully defensible on its own)
2. Cut UI polish before model reliability
3. Cut MongoDB before Gemini

Never claim the model was trained to detect migraine — that distinction holds regardless of which layer ships.
