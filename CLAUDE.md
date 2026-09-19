# VTHacks Project — MS Lesion Detection

Revised given: judges are evaluating based on the live presentation and the repo, not independent research into datasets/papers. That lowers the risk of someone finding the MS3SEG paper mid-judging, but doesn't change what we should actually build — Q&A is still a live fact-check, and the strongest version of this project is the honest version anyway.

## RF-DETR + Roboflow, reframed as lesion instance detection

We're not doing the exact 4-class dense tri-mask segmentation from the MS3SEG paper. Instead:

1. **Source lesion masks** from MS3SEG (abnormal WMH class) and/or MSLesSeg (binary lesion masks).
2. **Convert masks → bounding boxes** via connected-component extraction — each distinct lesion blob becomes one box.
3. **Export to COCO format via Roboflow**, fine-tune RF-DETR-B to detect individual lesions.
4. **OpenCV preprocessing**: slice normalization, CLAHE contrast enhancement, consistent resize/pad before feeding into the model.
5. **Severity/burden signal**: lesion count + total bounding box area per scan → a lesion burden score. This is a real, clinically-used concept (lesion burden tracking over time is an actual MS monitoring metric), and it's a natural fit for what detection outputs give you for free.
6. **Cross-dataset check (still worth doing)**: train on MS3SEG, run inference on MSLesSeg, see if detection holds up on a different hospital/scanner. Keep this even though judges won't research it independently — it's a strong live demo moment ("here's the same model on data it's never seen") and it's genuinely not much extra work once the pipeline exists.

## De-emphasized (not removed): citing the source paper

Since judges are working from the demo/repo rather than outside research, you don't need to build the pitch around "here's the paper we're extending." Optional, low-cost move: a single line in the README or a fine-print citation in the deck. Costs nothing, and if anyone _does_ ask where the dataset came from, you have a clean answer instead of an awkward pause.

## Open decision — explained in full, so you can decide as a team

**The core tension:** the misdiagnosis/migraine-mimic stats (18% misdiagnosis rate, migraine as the top mimic) are your strongest emotional hook. But the lesion detector, as built above, is trained only on already-diagnosed MS patients — there's no migraine or healthy-control data anywhere in MS3SEG or MSLesSeg. So the model can detect and count MS-pattern lesions in a scan, but it has no data to actually learn what a migraine-mimic lesion looks like versus a true MS lesion. That gap is the thing Q&A could expose regardless of what judges research beforehand — "how does counting lesions in a confirmed MS patient help catch a misdiagnosed migraine patient?" is an obvious question to ask live.

Two ways to handle it:

### Narrow the claim

Keep the misdiagnosis stats as **motivating context** ("this is why lesion pattern review matters, here's the scale of the problem") but scope the tool's actual claim to: detects and quantifies lesion burden, flags scans for radiologist review, supports monitoring over time. Don't claim the model itself distinguishes MS from migraine.

- **Pros**: zero extra engineering, fully bulletproof under any question, still uses your best stats as color/motivation.
- **Cons**: less of a direct "this solves the misdiagnosis problem" soundbite — the connection is contextual rather than causal.

### Build a lesion-pattern heuristic layer

Add a feature-engineering layer on top of detection: for each detected lesion, compute geometric features known in radiology to distinguish MS-typical lesions from vascular/nonspecific WMH — elongation and orientation relative to the ventricles ("Dawson's fingers" pattern, classic for MS), periventricular vs. subcortical location, ovoid shape. Use these features to flag lesions as "MS-typical pattern" vs. "atypical/nonspecific pattern," and let that flag support the misdiagnosis-prevention claim directly.

- **Pros**: directly supports the strong framing, adds a distinct second technical component beyond "we fine-tuned a detector" (real feature engineering + a second classification step), more differentiated demo.
- **Cons**: more scope for a weekend; and — this is the important part regardless of what judges dig into — **you have no migraine-patient data to validate this against**. You'd be applying known radiological heuristics, not a heuristic you've tested against confirmed migraine-mimic cases. That's fine to build and demo, but be ready to describe it accurately in Q&A as "we encode established diagnostic criteria" rather than "we trained this to detect migraine," since the second claim isn't something you'll actually have evidence for.

**What we need to decide:** is the extra weekend time for Option B worth it for the stronger pitch, or does Option A's simplicity + bulletproof Q&A answer win out given our timeline? Team call.

## Practical notes carried over

- Don't scrape MRI images — use MS3SEG and MSLesSeg (both public, no request/approval needed) or the Kaggle Brain Tumor 12K set if we ever pivot back.
- Keep the "recommendations go to doctor/hospital only, never shown directly to patient" framing prominent — it preempts safety questions in Q&A independent of the ethics discussion above.
- Scope claims to lesion-level detection, not full patient diagnosis, in whichever option we pick.
