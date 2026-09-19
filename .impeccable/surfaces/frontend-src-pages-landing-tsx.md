---
version: 1
slug: "frontend-src-pages-landing-tsx"
primary_target: "frontend/src/pages/Landing.tsx"
related_targets: ["frontend/src/App.tsx","frontend/index.html"]
---

# Landing (`/`) — surface brief

**Scope / mode:** Persuade, as a pitch backdrop. On screen during the 0:00–1:15 pitch beats, viewed 1–2 m across a table under bright hall light; must also survive a judge opening it alone. Routes: landing `/`, Analyze moved to `/analyze`, History `/history`.

**Audience & job:** radiologist/neurologist is the audience of record; judges evaluate whether it works for one. In one viewport they must understand: boxes every white-matter lesion on a FLAIR slice and reads each against established criteria for MS-typical vs. atypical/nonspecific. Then believe the stakes (18% · 72% · 33%). Then do one thing: **Analyze a slice →**.

**Proof:** a real annotated slice with per-lesion reasons (mock detections until a real slice lands at `frontend/public/plate/hero-slice.png`); the honesty line; both datasets cited. No validation numbers, logos, testimonials.

**Direction — MRI Atlas Plate** (Duvernoy/Talairach MRI atlas plates; Dawson 1916 lineage). The landing *is* a numbered atlas plate: slice as the figure, lesions as numbered callouts with hairline leaders to a margin legend, misdiagnosis numbers as the plate's key. Matte black plate ground, off-white hairlines and tabular numerals, ruled legend, figure captions carrying citations; orange = MS-typical, sky = atypical are the only chroma. No glow, gradients, glass, brain renders, "AI-powered", stat counters, or the word "accuracy".

**Memorable moment:** hover/focus a legend entry and its box + leader brighten while the rest dim — the atlas "find the label" gesture. Leaders draw in once on load; that is the only motion.

**Sequence:** Plate 1 (mechanism shown) → the key (18/72/33 as plate-scale ruled rows with citations + root-cause line) → honesty footnote → CTA again, nothing after.

**Layout:** desktop two columns (figure ~⅔ + margin legend); mobile stacks, leaders hidden, numerals on boxes carry the link. Legend entries keyboard-reachable; pattern never carried by color alone.

**Unresolved:** product name (Val United vs. MS Lesion Specificity — `PRODUCT_NAME` constant); hero slice file.
