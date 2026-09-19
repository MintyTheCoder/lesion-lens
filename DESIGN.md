---
name: MS Lesion Specificity
description: A numbered MRI atlas plate. Matte black ground, bone hairlines and tabular numerals, Archivo across its width axis, orange and sky as the only chroma.
colors:
  plate: "#0b0b0c"
  plate-raised: "#121214"
  bone: "#ece9e2"
  bone-dim: "#a39f96"
  bone-faint: "#6b675f"
  rule: "rgba(236, 233, 226, 0.16)"
  rule-strong: "rgba(236, 233, 226, 0.42)"
  typical: "#ff7a1a"
  atypical: "#4fc3f7"
typography:
  display:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(1.55rem, 2.05vw, 2.15rem)"
    fontWeight: 500
    lineHeight: 1.06
    letterSpacing: "-0.03em"
    fontVariation: "wdth 112"
  headline:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(1.6rem, 2.4vw, 2.25rem)"
    fontWeight: 500
    lineHeight: 1.08
    letterSpacing: "-0.03em"
    fontVariation: "wdth 112"
  key-figure:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(3.75rem, 8vw, 6rem)"
    fontWeight: 600
    lineHeight: 0.86
    letterSpacing: "-0.03em"
    fontFeature: "tnum"
    fontVariation: "wdth 112"
  statement:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(1.4rem, 2.3vw, 2.1rem)"
    fontWeight: 400
    lineHeight: 1.15
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 500
    lineHeight: 1.25
    letterSpacing: "normal"
  numeral:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "normal"
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.625
    letterSpacing: "normal"
  caption:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 400
    lineHeight: 1.375
    letterSpacing: "normal"
    fontFeature: "tnum"
  label:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "0.08em"
    fontVariation: "wdth 78"
rounded:
  none: "0px"
spacing:
  gutter: "16px"
  gutter-sm: "32px"
  row: "14px"
  row-lg: "20px"
  row-key: "28px"
  row-key-md: "36px"
  block: "32px"
  column: "64px"
  section: "80px"
  header: "56px"
components:
  action-large:
    backgroundColor: "transparent"
    textColor: "{colors.bone}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "16px 24px"
    width: "100%"
  action-large-hover:
    backgroundColor: "{colors.bone}"
    textColor: "{colors.plate}"
  action-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.bone}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "12px 16px"
  action-quiet-hover:
    backgroundColor: "{colors.bone}"
    textColor: "{colors.plate}"
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.bone-dim}"
    typography: "{typography.label}"
    padding: "8px 0"
  nav-link-active:
    textColor: "{colors.bone}"
  legend-row:
    backgroundColor: "transparent"
    textColor: "{colors.bone}"
    rounded: "{rounded.none}"
    padding: "14px 0"
  plate-frame:
    backgroundColor: "{colors.plate}"
    rounded: "{rounded.none}"
---

# Design System: MS Lesion Specificity

## Overview

**Creative North Star: "The Atlas Plate"**

The interface is a numbered MRI atlas plate in the Duvernoy/Talairach lineage. The scan is the figure; every lesion is a numbered callout joined by a hairline leader to a ruled legend in the margin; the misdiagnosis statistics are the plate's key. Nothing on the surface is decoration: every rule separates two things a clinician needs to tell apart, every numeral indexes a real object, and every color means a pattern flag. The ground is a matte black plate, the ink is bone white, and the page reads like a printed reference sheet held up to the light rather than a software product.

Density is editorial and unhurried. Sections are long ruled stanzas separated by single hairlines, not stacked panels. Type does the layering: Archivo's width axis is worked hard, with wide, tight-tracked display and plate-scale numerals against narrow, letterspaced uppercase labels, and secondary text steps down to a dimmed bone rather than a smaller size. The only motion is the leaders drawing in once on load and the brighten/dim gesture when a legend entry is hovered or focused: the atlas "find the label" moment.

The world refuses the glowing-brain hero, the feature-card grid, gradients, glass, and shadows. It also carries two copy commitments from the product: the honesty line about encoded criteria, and the "decision support, not a diagnosis" line, both rendered verbatim from `frontend/src/brand.ts`.

**Key Characteristics:**
- Matte black plate ground (`#0b0b0c`) with bone-white ink; no tonal surfaces, no fills at rest.
- Hairlines do all the structure: 1px rules at 16% and 42% bone alpha, square frames, corner ticks, orthogonal leaders.
- Two chroma roles only: orange for MS-typical, sky for atypical or nonspecific; always paired with a numeral and a label.
- One variable face, Archivo, across its width axis: narrow (78%) labels, wide (112%) display and numerals, tabular figures everywhere a number appears.
- Zero radius, zero shadow, zero gradient. Depth is opacity and stroke weight.
- Motion is a single draw-in and a 300ms opacity shift, both on the standard out-curve, both respecting reduced motion.

## Colors

A monochrome plate with two semantic inks: bone on black for everything structural, and orange or sky only where a lesion's pattern flag is stated.

### Primary
- **Plate Black** (`{colors.plate}`): the page ground, the frame interior, the inverted text color on a filled action. Set as the `theme-color` and `color-scheme: dark`.
- **Bone** (`{colors.bone}`): primary text, the wordmark, plate numerals, legend numerals, the active leader and active-numeral fill, the focus ring, the selection highlight, and the hover fill of the action. Everything that would be ink on a printed plate.

### Secondary
- **MS-typical Orange** (`{colors.typical}`): the stroke of a lesion box flagged MS-typical, its numeral and tick, its legend pattern label, and the names of the three MS-typical criteria. At 18% fill opacity inside an active box.
- **Atypical Sky** (`{colors.atypical}`): the stroke of a lesion box flagged atypical or nonspecific, its numeral and tick, and its legend pattern label. Same active-fill treatment as orange.

### Neutral
- **Bone Dim** (`{colors.bone-dim}`): secondary and supporting text: descriptor, body copy in the margin, legend reasons, confidence figures, captions, citation sources, orientation letters, inactive nav links.
- **Bone Faint** (`{colors.bone-faint}`): a third text step reserved for the quietest annotations. Defined in the token set; the landing does not yet reach for it.
- **Rule** (`{colors.rule}`): the standard hairline: header bottom rule, section separators, legend and key row rules, the criteria list, the footer rule.
- **Rule Strong** (`{colors.rule-strong}`): the plate frame border, the corner ticks, and the nav link hover underline. Used where a hairline must read as a boundary rather than a separator.
- **Plate Raised** (`{colors.plate-raised}`): a one-step lift for pending surfaces that need an input well or a row hover. Defined in the token set; unused on the landing.

Two alpha variants of bone recur without a token of their own: bone at 70% (`rgba(236,233,226,0.7)`) is both the resting leader stroke and the action's border, and the terminal dot at the box end of a leader takes the same stroke color. Treat 70% bone as the "resting ink" step between rule-strong and full bone.

### Named Rules
**The Two Inks Rule.** Orange and sky are the only chroma on any surface, and each appears only where a lesion's pattern flag is being stated: box, numeral, tick, legend label, criteria name. No accent color for links, buttons, states, charts, or brand. Bone and its alphas carry every other role.

**The Never Alone Rule.** Pattern is never conveyed by color alone. Every orange or sky element sits beside a numeral and its label text ("MS-typical pattern" / "Atypical or nonspecific pattern"), so the flag survives monochrome and color-blind viewing.

**The No Fill Rule.** Nothing on the page has a filled background at rest. The single exception is the action on hover and focus, which fills to bone and inverts to plate text; that inversion is what makes it read as the one thing to press.

## Typography

**Display Font:** Archivo variable, self-hosted (`/fonts/Archivo-Variable.woff2`, wght 100 to 900, wdth 62% to 125%), with `system-ui, sans-serif` fallback
**Body Font:** Archivo (same file)
**Label Font:** Archivo at 78% width, uppercase, 0.08em tracking

**Character:** One face across its width axis stands in for a pairing. Wide (112%) and tight-tracked (-0.03em) for display, headlines, and the plate-scale key figures, so numbers feel set in metal; narrow (78%) and letterspaced for uppercase labels, so they read as atlas marginalia. Tabular numerals are on globally (`font-feature-settings: "tnum" 1`) and reinforced with `.tnum` wherever numbers align in columns.

### Hierarchy
- **Key Figure** (600, `clamp(3.75rem, 8vw, 6rem)`, line-height 0.86, wide, tnum, -0.03em): the 18% / 72% / 33% figures in the key. Sized to be read at two metres; sits on a `min-width: 4.2ch` column so statements align.
- **Display** (500, `clamp(1.55rem, 2.05vw, 2.15rem)`, line-height 1.06, wide, -0.03em, balanced): the single h1 at the head of the margin.
- **Headline** (500, `clamp(1.6rem, 2.4vw, 2.25rem)`, line-height 1.08, wide, -0.03em, balanced, max 24ch): section h2s ("The numbers behind a wrong diagnosis", "What the pattern flag encodes").
- **Statement** (400, `clamp(1.4rem, 2.3vw, 2.1rem)`, line-height 1.15, -0.03em, max 26ch): the sentence beside each key figure. The honesty aside uses the same form one step down (500, `clamp(1.35rem, 1.9vw, 1.75rem)`).
- **Numeral** (500, 1.5rem, line-height 1, tnum): the index number at the head of each legend row and of each criteria row. On the plate itself the numeral is held at a constant rendered 18px (600) regardless of frame size.
- **Title** (500, 1.1rem, line-height tight): the pattern label in a legend row, in its pattern color; criteria names.
- **Body** (400, 0.95rem, line-height 1.625, `text-wrap: pretty`): running copy, in bone-dim when supporting a display element and in bone when it is the point. The root-cause lead paragraph uses the same step in bone. Measure 44ch in the margin, 62 to 64ch in full-width prose.
- **Caption** (400, 0.85rem, line-height 1.375, tnum): figcaption, confidence figures, footer definition list.
- **Label** (400, 0.72rem, line-height 1, uppercase, 0.08em, narrow 78%): nav links, citation sources, "Plate 1", footer terms, orientation letters; the action text steps up to caption size (0.85rem large / 0.75rem quiet); the slot notice sits at caption size.

### Named Rules
**The Width Axis Rule.** Hierarchy is carried by width and tracking before size. Display and numerals go wide and tight; labels go narrow and open; body sits at 100%. Do not introduce a second family or a monospace for numbers; Archivo's tabular figures are the numeric voice.

**The Tabular Rule.** Every number that a clinician might compare (counts, percentages, confidence, plate numerals) is set with tabular numerals so columns align and hover states do not reflow.

## Layout

The page is full-bleed on the plate ground with a 16px gutter (32px from `sm`). The header is a single 56px row closed by one hairline. Sections are separated by one hairline each and breathe 80px above and below; the plate section is tighter (32px top, 40px from `lg`, 64px bottom) so the figure reaches the first viewport.

The plate is a two-column grid from `lg` (1024px): `minmax(0, 1.5fr)` for the figure and `minmax(21rem, 1fr)` for the margin, 64px column gap. The figure is a square frame capped at `calc(100vh - 12rem)` so the whole plate fits the first viewport; the margin stacks title, ruled legend, and the action in three rows, with the action directly beneath the legend. The same 1.5fr / 1fr grid is reused for the criteria-plus-honesty section and the footer, so the margin column persists down the page. Below `lg` everything stacks in one column (title, figure, legend, action), leaders are not drawn, and the numerals on the boxes carry the link to the legend.

Ruled lists are the recurring spatial unit: a top hairline on the list, a bottom hairline on each row, no side borders, content in a two- or three-column grid inside the row. Row padding is 14px in the legend, 20px in the criteria list, and 28px (36px from `md`) in the key. Between figure and caption is 16px; between a heading and its list is 40 to 48px.

Breakpoints in use: `sm` 640px (gutter, footer dl columns), `md` 768px (descriptor in header, key row grid), `lg` 1024px (two-column plate, leaders, frame cap). Pending surfaces (Analyze, History) currently sit in a centered `max-w-7xl` container with 24px padding inherited from the pre-world shell; that container is not part of this system.

## Elevation & Depth

There are no shadows, no gradients, no blur, and no tonal surfaces. The page is one flat plate. Depth is conveyed three ways only: stroke alpha (rule 16%, rule-strong 42%, resting ink 70%, bone 100%), stroke weight (1px hairlines, 1.25px box strokes, 2px on the active box, 1.25px on the active leader), and opacity shifts on interaction (inactive legend rows drop to 0.38, inactive boxes to 0.3, inactive leaders to 0.25, all over 300ms on the out-curve). The active box gains an 18% fill of its own pattern color, the only translucent fill in the world.

### Named Rules
**The Flat Plate Rule.** Surfaces never lift. If two things must be distinguished in depth, use a hairline between them or dim one of them; never a shadow, a lighter panel, or a blur.

**The Dim The Rest Rule.** Emphasis is achieved by lowering everything else, not raising the target. Hover or focus brightens one callout to full bone stroke and dims its neighbours; the target's own scale, weight, and position do not change.

## Shapes

Every corner is square (0px radius) on every element: frame, boxes, action, legend rows, nav underline, focus ring. Borders are 1px hairlines and are used on one or two sides far more often than four: the header has only a bottom rule, list rows only a bottom rule, the nav active state only an underline. The four-sided frame is reserved for the plate figure (rule-strong) and the action (bone at 70%).

The plate frame carries atlas furniture: four 16px L-shaped corner ticks set 12px inside the frame edge, and single orientation letters (A / P / R / L, radiological convention) centred on each side in label type. Leaders are orthogonal only (horizontal, vertical, horizontal), with a 2px-radius terminal dot at the box end and a 7px stagger between trunks so upper rows take the outer trunk and no arm crosses a neighbour's trunk. Lesion callouts are a 1.25px rectangle padded 3 image-pixels outside the detection, an 8px tick on the left centreline, and the numeral 12px beyond it, right-aligned. The action arrow is an authored 22x12 SVG stroke with square caps, not an icon-set glyph.

## Components

### Buttons
The plate has one action and it is drawn like a ruled callout, not a pill. Nothing else on the page fills.
- **Shape:** square (0px), 1px border of bone at 70%.
- **Large (`action-large`):** transparent ground, bone text, label type at 0.85rem (narrow, uppercase, 0.08em), 16px 24px padding, full width of the margin column, content justified between the text and a 22x12 authored arrow (1.25px stroke, square caps).
- **Quiet (`action-quiet`):** same construction at 0.75rem with 12px 16px padding and intrinsic width; the restatement at the foot of the page, right-aligned to the margin column.
- **Hover / Focus:** background fills to bone and text inverts to plate over 200ms on the out-curve; the arrow translates 4px right over 300ms. Focus-visible additionally shows the global 1px bone outline offset 3px.

### Navigation
- **Header:** one 56px row, bottom hairline (rule), 16/32px gutters, wordmark at left and links at right with 24px gaps.
- **Wordmark:** wide Archivo, 600, 0.95rem, -0.03em, bone; the descriptor beside it in 0.72rem bone-dim from `md`.
- **Links:** label type (narrow uppercase 0.72rem, 0.08em), 8px vertical padding, 1px bottom border. Default bone-dim on a transparent border; hover bone on rule-strong; active bone on bone. Colors transition 200ms on the out-curve. Mobile keeps the same row; only the descriptor hides.

### Ruled Lists (key, criteria, legend, footer dl)
The system's container. A top hairline on the list, a bottom hairline per row, no side rules, no background. Inside each row a grid: numeral column (2.5rem legend / 2.25rem criteria / `auto` with 4.2ch min in the key), then `minmax(0, 1fr)` for text, then an optional `auto` trailing column for a figure such as confidence. Rows never fill on hover; state is carried by opacity.

### Plate Figure (signature)
The world's defining component (`frontend/src/components/plate/PlateFigure.tsx`).
- **Frame:** square, rule-strong 1px border, plate ground, corner ticks and orientation letters, capped at `calc(100vh - 12rem)` on `lg`. When the slice image fails to load, a labelled slot in label type sits low in the frame; the frame and furniture still render so the plate reads as a plate.
- **Boxes:** SVG in image-pixel coordinates (`viewBox` = image width and height, `vector-effect: non-scaling-stroke`), stroked in the pattern color at 1.25px, padded 3 image px; numerals held at a constant rendered 18px (600, tabular) by dividing by the frame scale.
- **Leaders:** measured from the DOM on `lg` and redrawn on resize, font load, and breakpoint change; orthogonal paths from the box's right centreline to the legend row's left edge, 1px bone at 70% with a 2px terminal dot; draw in once over 900ms on the out-curve with a 60ms stagger per row (`prefers-reduced-motion` skips the draw).
- **Legend rows:** `<button>` elements with `aria-pressed`, keyboard focusable; numeral (1.5rem), pattern label in pattern color (1.1rem), reasons joined by " · " in bone-dim (body, 0.95rem), confidence to two decimals in caption tnum.
- **Interaction:** hover, focus, or click on either a box or a row sets the active lesion; the active box gets a 2px stroke, an 18% fill, and a bone numeral, its leader goes full bone at 1.25px, and everything else dims (0.38 row / 0.3 box / 0.25 leader) over 300ms. Click pins; clicking again unpins.
- **Caption:** "Plate 1" in label type in bone, then modality, then tabular counts and burden in bone-dim, then a source note.

### Inputs / Fields
Not yet built in this world. The Analyze upload dropzone and History list are pending surfaces still on the pre-world Tailwind slate defaults; when they are brought in, derive them from the ruled-list and plate-frame vocabulary (hairline borders, plate-raised well, label type), not from their current styling.

## Do's and Don'ts

### Do:
- **Do** set the ground to Plate Black and every structural line as a 1px hairline in rule (16%) or rule-strong (42%); use rule-strong only for boundaries (frames, ticks, the nav hover underline).
- **Do** pair every orange or sky element with a numeral and its exact label text ("MS-typical pattern" / "Atypical or nonspecific pattern"); the Never Alone Rule is load-bearing for clinical use.
- **Do** use Archivo's width axis for hierarchy: wide (112%) and -0.03em for display and figures, narrow (78%) uppercase with 0.08em for labels, 100% for body.
- **Do** set every comparable number in tabular numerals and hold plate numerals at a constant rendered 18px.
- **Do** build containers as ruled lists (top rule on the list, bottom rule per row) and reuse the 1.5fr / minmax(21rem, 1fr) margin grid from `lg`.
- **Do** keep the action a bordered square that fills to bone and inverts on hover and focus; it is the only fill on the page.
- **Do** carry the honesty line and the "decision support, not a diagnosis" line verbatim from `frontend/src/brand.ts` wherever the product is described.
- **Do** transition state with opacity and stroke on `cubic-bezier(0.16, 1, 0.3, 1)` at 200 to 300ms, and respect `prefers-reduced-motion`.

### Don't:
- **Don't** add glow, gradient, glass, blur, or box-shadow anywhere; the plate is flat.
- **Don't** use cards, tiles, or filled panels; separate content with a hairline instead.
- **Don't** introduce any chroma beyond orange (MS-typical) and sky (atypical), and never use either for a non-pattern role such as a link, button, or brand mark.
- **Don't** round a corner; the radius scale has one step and it is 0px.
- **Don't** add eyebrows or kicker lines above headings; the only uppercase labels are functional atlas marginalia (plate number, citation source, definition terms, orientation letters, nav).
- **Don't** use icon-set glyphs; the arrow is an authored SVG stroke, and any future mark should be drawn the same way.
- **Don't** write "accuracy" as a metric; the words are precision and false positives per scan, and the pattern flag is reported descriptively.
- **Don't** show stat counters, brain renders, "AI-powered" copy, or fabricated validation numbers, logos, or testimonials.
