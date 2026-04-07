# NEXT VISIBLE IMPLEMENTATION TARGET — H2

## Objective
Define the next visible Studio change to implement inside `feat/studio-operational-integration-v1` after the H1 publish-confidence slice.

This document exists to move from planning into the next concrete UI change with minimal ambiguity.

---

## Immediate target
Upgrade the current publication policy / readiness area so the operator can immediately answer:
- can I publish now?
- what blocks me?
- what is optional?
- is frozen the same as ready?
- is the Website contract acceptable enough?
- what should I do next?

---

## Primary surface to change
First target surface:
- current publication policy / readiness box inside the Website publish flow

Keep this change Studio-side and UI-first.

---

## Visible implementation order
### 1. Primary readiness summary
Add one visible summary label:
- `Pronto para publicar`
- `Ainda bloqueado`
- `Pronto com melhorias opcionais pendentes`

### 2. `Bloqueia publicação`
Add one explicit blockers bucket with only true blockers.

### 3. `Melhorias opcionais`
Add one explicit optional bucket with only non-blocking enrichments.

### 4. Freeze vs ready distinction
Keep package-freeze visible, but separate it from final publish-ready verdict.

### 5. Website contract meaning
Translate contract state into practical operator language.

### 6. `Próximo passo recomendado`
End the area with one clear next action.

---

## Safe first-pass rule
During the first visible H2 pass:
- add the new readiness interpretation layer
- keep existing detailed policy information below it
- do not redesign the whole panel
- simplify duplicated wording only after visual validation

---

## Acceptance target
This H2 visible slice is acceptable when:
- the operator can understand readiness without reading dense policy details first
- blockers and optional items are clearly separated
- frozen and ready are not confused
- contract meaning is understandable
- one next action is visible
- the branch remains green

---

## Branch rule
Implement only in `feat/studio-operational-integration-v1`.
Do not touch `main`.
Do not reopen architecture.
Prefer visible clarity over policy-engine ambition.
