# TRUE PRODUCTION FLOW AUDIT V1

## Purpose
Define the real operational path the Baribudos Studio should support for daily use after the main merges and green builds.

This document is not architecture design.
It is an operational audit map.

---

## A. Production flow target

The target flow is:
1. create project correctly
2. input/shape text correctly
3. produce visuals/audio/outputs in a sane order
4. freeze the public package only when ready
5. publish to Website cleanly
6. observe and control Website from Studio

If users cannot follow this path comfortably, the system is not yet operationally mature even if builds stay green.

---

## B. Recommended operator sequence

### Phase 1 — project bootstrap
Panels / areas expected:
- Project creation mode
- saga/IP context
- stage modes

Target result:
- project exists
- correct project mode chosen
- stage modes reflect intended workflow
- hidden/official rules are explicit enough

Operational risks to audit:
- user does not understand project mode impact
- hidden fields feel too technical
- stage modes exist but do not guide next actions

---

### Phase 2 — story input and editorial shaping
Panels / areas expected:
- StorySourcePanel
- StoryLayoutPanel
- continuity / typography context where relevant

Target result:
- text-first flow is obvious
- raw story is captured
- editable structure is understandable
- pagination/edit shaping feels natural

Operational risks to audit:
- user unsure whether to input raw text or structured text
- layout step appears too early or too late
- no clear signal of editorial completeness

---

### Phase 3 — visual production
Panels / areas expected:
- illustration pipeline
- image generation controls
- character/IP consistency visibility where needed

Target result:
- user knows when visuals can start
- consistency constraints are visible enough
- blocking issues are surfaced early

Operational risks to audit:
- users generate visuals before story is stable
- character lock / consistency warnings are too hidden
- too much technical noise in visual pipeline

---

### Phase 4 — voice and audio production
Panels / areas expected:
- VoiceProfilesPanel
- AudioCastPanel

Target result:
- real voice owner is preserved
- credits are automatically derived correctly
- variant policy remains visible and safe
- audio casting is understandable at product level

Operational risks to audit:
- confusion between real owner, credited name and variant
- uncertainty around which voices are approved for which context
- too much manual work to assign voices repeatedly

---

### Phase 5 — outputs and package assembly
Panels / areas expected:
- production pipeline
- package / publication package
- publish readiness

Target result:
- user sees what outputs exist
- missing blocking items are obvious
- freezing package is intentional and clearly explained
- readiness feels credible, not decorative

Operational risks to audit:
- package can be frozen with weak understanding
- readiness labels are too abstract
- users do not understand what is still blocking publish

---

### Phase 6 — Website publish and operational control
Panels / areas expected:
- Website control panel
- publish actions
- health / summary / catalog / publications / reconcile

Target result:
- publish action is trustworthy
- Website state is visible from Studio
- divergence is visible
- revalidate/unpublish are available when needed

Operational risks to audit:
- users do not know whether publish actually worked
- Studio shows data but not enough operational meaning
- divergence exists but corrective next step is unclear

---

## C. Mandatory vs optional vs assisted vs automatic

### Mandatory before publish
- project exists
- story exists
- required editorial/commercial metadata exists
- critical outputs required by policy exist
- readiness gate passes
- package is frozen

### Optional for richer launch
- extra SEO polish
- extended gallery/media
- additional variants
- extra campaign packaging

### Assisted by Studio
- guided progression through panels
- credit derivation
- readiness explanation
- package review
- Website state interpretation

### Automatic where safe
- timestamps
- derived credits
- package metadata stamping
- Website status refresh
- reconcile refresh

---

## D. Friction audit questions

For each phase ask:
- what is the intended next action?
- is that next action obvious in the UI?
- what would a non-technical operator misunderstand?
- which fields should have better defaults?
- what error should be rewritten in clearer language?
- what feedback is missing after a successful action?

---

## E. Daily operation readiness score

Use this scoring model for honest maturity assessment:

### 0–25
Technical only, not operationally usable.

### 26–50
Usable by builder/admin with effort.

### 51–75
Usable for initial real work, but still tiring.

### 76–90
Operationally strong for real daily use with some friction.

### 91–100
Comfortable, governable, repeatable production system.

---

## F. Immediate audit targets for the next phase

### Audit target 1
Project creation clarity.

### Audit target 2
Text-first flow comfort.

### Audit target 3
Voice ownership / credits / variants clarity.

### Audit target 4
Package freezing and readiness credibility.

### Audit target 5
Website publish confidence and reconcile trust.

### Audit target 6
Family/team usability under real conditions.

---

## G. Expected deliverable after this audit phase

At the end of this phase the Studio should have:
- a clear true production flow
- explicit mandatory vs optional steps
- better defaults and feedback targets
- a known list of operational friction points
- a prioritized list of safe improvements that do not destabilize green systems
