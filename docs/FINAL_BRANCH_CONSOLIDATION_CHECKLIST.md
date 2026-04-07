# FINAL BRANCH CONSOLIDATION CHECKLIST

## Purpose
Close `feat/studio-operational-integration-v1` with discipline before any final merge review.

This checklist begins only after the visible H1 → H5 slices are already live in real Studio surfaces and the branch remains green.

---

## A. Scope freeze

### Required
- [ ] no new architectural discussions are reopened
- [ ] no repo-fusion changes are introduced
- [ ] no broad redesigns are introduced in the name of cleanup
- [ ] further changes stay limited to safe consolidation only

---

## B. Visible-slice confirmation

### Required
- [ ] H1 publish confidence remains visible and green
- [ ] H2 readiness credibility remains visible and green
- [ ] H3 story-first comfort remains visible and green
- [ ] H4 voice/cast clarity remains visible and green
- [ ] H5 Website control meaning remains visible and green

---

## C. Duplication reduction

### Required
- [ ] duplicated wording is only reduced where the old and new layers clearly overlap
- [ ] no useful legacy detail is removed prematurely
- [ ] no contradictory operator messaging remains in visible surfaces
- [ ] cleanup stays local and low-risk

---

## D. Consistency pass

### Required
- [ ] operator language feels coherent across H1 → H5
- [ ] `Próximo passo recomendado` style is consistent where used
- [ ] status / readiness / guidance wording is not fighting itself across panels
- [ ] cards added during this branch still feel part of one Studio language

---

## E. Green-state verification

### Required
- [ ] branch checks stay green after consolidation edits
- [ ] no regression is introduced in the previously stabilized slices
- [ ] no accidentally deleted file or missing import remains

---

## F. Honest exit-criteria check

### Required
- [ ] the branch is reviewed against `docs/OPERATIONAL_INTEGRATION_EXIT_CRITERIA_V1.md`
- [ ] merge readiness is based on real comfort, not impatience
- [ ] unresolved friction is acknowledged honestly if still present

---

## G. Merge-readiness gate

The branch can be reviewed for final merge only when:
- [ ] H1 → H5 remain visible and green
- [ ] safe duplication reduction is done where useful
- [ ] consistency pass is acceptable
- [ ] exit criteria are honestly satisfied
- [ ] the branch still feels safer to merge than to keep reworking blindly

---

## H. Rule after this checklist

If the checklist is not honestly green:
1. keep working inside `feat/studio-operational-integration-v1`
2. do not touch `main`
3. fix the real weak points only

If the checklist is honestly green:
1. perform merge-readiness review
2. confirm green state again
3. only then move toward final merge
