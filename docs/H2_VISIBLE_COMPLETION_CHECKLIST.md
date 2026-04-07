# H2 VISIBLE COMPLETION CHECKLIST

## Purpose
Close the first visible H2 slice in the Studio operational integration branch with a strict, low-risk validation checklist.

This checklist starts after the H2 readiness/publication-policy upgrade is visibly added to the current Website publish flow.

---

## A. Readiness summary validation

### Required
- [ ] one primary readiness summary is visible
- [ ] `Pronto para publicar` appears only when no required blockers remain
- [ ] `Ainda bloqueado` appears when real blockers still exist
- [ ] `Pronto com melhorias opcionais pendentes` appears only when blockers are gone but optional items remain
- [ ] readiness feels like a real operational verdict rather than decorative status text

---

## B. Required blockers bucket validation

### Required
- [ ] one `Bloqueia publicação` bucket is visible when real blockers exist
- [ ] the bucket contains only true blockers
- [ ] optional enrichments are not mixed into the blockers bucket
- [ ] blockers are easy to scan visually

---

## C. Optional improvements bucket validation

### Required
- [ ] one `Melhorias opcionais` bucket is visible when optional enrichments exist
- [ ] the bucket contains only non-blocking items
- [ ] the optional bucket feels secondary to the blockers bucket
- [ ] the operator understands that optional items do not automatically stop publish

---

## D. Freeze vs ready validation

### Required
- [ ] `Package congelado` remains visible when relevant
- [ ] frozen package is clearly not treated as identical to final readiness verdict
- [ ] blocked-but-frozen states remain understandable

---

## E. Website contract meaning validation

### Required
- [ ] one operator-facing contract meaning is visible
- [ ] contract meaning is easier to understand than raw score/status alone
- [ ] contract meaning supports readiness confidence instead of confusing it
- [ ] raw contract score/status can remain secondary if useful

---

## F. Next-step validation

### Required
- [ ] one `Próximo passo recomendado` is visible in the readiness area
- [ ] the next action changes according to the real readiness state
- [ ] the next action reduces hesitation after reading readiness/policy information

---

## G. Duplication control

### First safe pass
- [ ] legacy detail remains acceptable during transition
- [ ] no severe contradictory messaging exists between old and new readiness/policy elements

### After validation
- [ ] duplicated legacy wording can be simplified safely in a follow-up pass

---

## H. H2 visible completion rule

The first visible H2 slice can be considered complete when:
- [ ] readiness verdict is immediately understandable
- [ ] blockers and optional items are clearly separated
- [ ] frozen and ready are not confused
- [ ] Website contract meaning is clearer
- [ ] one next action is visible
- [ ] the branch remains green

---

## I. Safe immediate next step after visible H2 completion

After this checklist is green:
1. move to the visible H3 story-first slice
2. keep all work inside `feat/studio-operational-integration-v1`
3. continue using PR `#5` as the single operational trail
