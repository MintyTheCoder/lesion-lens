---
version: 1
slug: "frontend-src-pages-analyze-tsx"
primary_target: "frontend/src/pages/Analyze.tsx"
related_targets: ["frontend/src/components/case/CaseView.tsx","frontend/src/components/plate/PlateIntake.tsx"]
---

# Analyze (`/analyze`) — surface brief

**Scope / mode:** Operate. The clinician (or a judge alone) uploads one FLAIR slice and reads the result; the 1:15–3:00 pitch beat runs on this screen. Full-bleed plate; the pre-world `max-w-7xl` container is gone for this route.

**Thesis:** the landing showed a finished plate; Analyze is the same plate being made. One composition (`PLATE_GRID`, `PlateFrame`), four states: intake = empty frame as the drop target + rehearsed sample list in the margin; processing = uploaded slice in the frame, "Reading slice" + tabular elapsed seconds, samples dimmed; result = `CaseView` (landing's Plate 1 with the clinician's slice, burden as the plate's key, legend with location · area, note with Copy, validation last); error = slice stays in frame, problem named where the legend would be, Try again / Choose another, samples still live.

**States mapped to the backend:** 415/400 → not readable as a slice (choose another); 503 → model service + not cached (try again, samples as the offline path); network → service unreachable; client-side reject on type/size before any request. 0 lesions is a finding, not an error. >12 lesions: leaders off, frame sticky.

**Motion:** the leader draw-in on result arrival is the reveal; nothing else animates beyond 200–300ms opacity/stroke.

**Kept verbatim:** `HONESTY_LINE` (validation margin), `NOT_A_DIAGNOSIS` (note margin), `PATTERN_LABEL` on every orange/sky element.

**Unresolved:** sample slice files (`public/samples/`, see README there) and their demo_cache entries; real validation figures (section shows a labelled pending row until `n_scans > 0`).
