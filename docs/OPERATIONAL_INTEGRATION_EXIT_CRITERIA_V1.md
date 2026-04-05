# OPERATIONAL INTEGRATION EXIT CRITERIA V1

## Objective
Define the minimum exit criteria for `feat/studio-operational-integration-v1` before the branch can leave draft status mentally and become a serious candidate for final merge into `main`.

This document exists to prevent premature merge and to keep the branch focused on operational maturity rather than architectural drift.

---

## Core rule
This branch should only move toward final merge when:
- the accumulated block remains green
- operator confidence is visibly stronger than on current `main`
- the user journey is clearer, not just technically richer
- changes remain incremental and low-risk

---

## Mandatory technical criteria
- [ ] Studio CI remains green on the integration branch
- [ ] Windows EXE build remains green on the integration branch
- [ ] Android APK build remains green on the integration branch
- [ ] no destabilizing regression is introduced in existing green flows
- [ ] no architectural reopening occurred during the branch work

---

## Mandatory operational criteria
### H1 publish confidence
- [ ] publish-confidence card is visibly integrated in the Website control area
- [ ] operator can distinguish sent / received / materialized
- [ ] receipt visibility is stronger
- [ ] next recommended action is visible
- [ ] failure language is more operator-friendly

### H2 readiness credibility
- [ ] required blockers vs optional enrichments are clearer
- [ ] readiness feels operational instead of decorative
- [ ] package frozen is not confused with publish-ready confidence

### H3 story-first comfort
- [ ] story-first progression is easier to understand
- [ ] save/edit confidence is stronger
- [ ] operator can tell when to move from text to layout and then to visuals

### H4 voice ownership / credits / variants clarity
- [ ] owner vs credited name is clearer
- [ ] original vs variant is clearer
- [ ] credits logic feels more trustworthy
- [ ] AudioCast assignment has less repeated friction

### H5 Website control meaning
- [ ] Website control feels more operational and less developer-shaped
- [ ] divergence meaning is easier to understand
- [ ] next corrective action is more explicit

---

## Branch hygiene criteria
- [ ] only the active operational integration branch remains the main working branch
- [ ] obsolete merged branches are already cleaned up
- [ ] PR `#5` remains the single operational integration trail for this phase
- [ ] changes in the branch are still reviewable and not turning into uncontrolled sprawl

---

## Merge-readiness questions
Before considering final merge, answer all of these with confidence:
- [ ] Is the operator experience clearly better than `main`?
- [ ] Did we improve clarity more than complexity?
- [ ] Did we keep the Studio as source of truth and Website as projection layer?
- [ ] Are we merging an operational improvement branch, not an experimental mess?
- [ ] Are the green checks still green on the latest head?

---

## Red flags that should delay final merge
Delay merge if any of these are true:
- [ ] H1 visible integration is still not actually wired into the existing panel
- [ ] readiness logic/UI became more confusing instead of clearer
- [ ] operational branch started accumulating unrelated experiments
- [ ] the branch is green technically but still awkward for daily use
- [ ] confidence improved only on paper, not in the visible operator experience

---

## Exit threshold
This branch becomes a merge candidate only when:
- technical checks stay green
- H1 visible slice is truly visible in Studio
- H2-H5 have at least materially improved clarity in their surfaces
- the operational story from project creation to Website control feels stronger and calmer than current `main`

---

## Final rule
Do not merge this branch because it is long-lived.
Merge it only when it is operationally better and still technically safe.
