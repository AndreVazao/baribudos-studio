# H2 READINESS CREDIBILITY EXECUTION BUNDLE V1

## Objective
Turn H2 into a small, reviewable implementation bundle inside `feat/studio-operational-integration-v1`.

This bundle exists to improve readiness credibility visibly in the Studio without reopening architecture and without destabilizing green paths.

---

## Problem
The Studio already exposes readiness and publication policy signals, but operators can still hesitate because:
- required blockers and optional enrichments are mixed together
- readiness can feel decorative instead of operational
- package frozen and ready-to-publish are easy to confuse
- Website contract status is visible but not translated into practical language

---

## Scope of this execution bundle
This H2 execution bundle should cover:
- clearer readiness state summary
- required blocker bucket
- optional improvement bucket
- clearer Website contract meaning
- clearer distinction between frozen package and publish-ready confidence

This H2 bundle should not cover:
- architectural redesign
- new Website-side logic
- deep backend policy rewrite unless a real blocker appears
- broad dashboard redesign

---

## Main surfaces expected to change
Studio-side only, primarily:
- publication policy box
- package/readiness area
- Website publish gating explanation
- operator-facing readiness labels/messages

---

## Recommended visible operator model
### Primary readiness states
- `Pronto para publicar`
- `Ainda bloqueado`
- `Pronto com melhorias opcionais pendentes`

### Required bucket
Use one explicit section:
- `Bloqueia publicação`

### Optional bucket
Use one explicit section:
- `Melhorias opcionais`

### Contract meaning examples
- `Contrato Website válido para publicar`
- `Contrato Website ainda incompleto`
- `Contrato Website precisa de revisão antes de publicar`

---

## Implementation checklist
### H2.1 Primary readiness label
- [ ] define one visible readiness summary label
- [ ] make the label reflect practical publish readiness, not decorative status only

### H2.2 Required blocker bucket
- [ ] show required blockers in one explicit list
- [ ] make blockers easy to scan
- [ ] avoid burying blockers in dense policy text

### H2.3 Optional improvement bucket
- [ ] show optional enrichments separately from blockers
- [ ] make it clear that optional items do not block publish by default

### H2.4 Freeze vs ready distinction
- [ ] keep `package frozen` visible
- [ ] make it explicit that frozen is necessary but not identical to publish-ready confidence

### H2.5 Website contract meaning
- [ ] translate contract status into operator language
- [ ] reduce interpretation burden around score/status values

### H2.6 Next recommended action
- [ ] show one clear next action from readiness state
- [ ] examples: close blockers, review contract, proceed to publish

---

## Minimal UI recommendation
Inside the readiness/policy area, aim for:
1. one primary readiness label
2. one short practical meaning line
3. one blockers bucket
4. one optional improvements bucket
5. one next recommended action

### Example
**Estado de readiness:** Ainda bloqueado
**Significado:** O projeto ainda tem bloqueios que impedem publicação segura.

**Bloqueia publicação**
- Package ainda não congelado
- Contrato Website incompleto

**Melhorias opcionais**
- SEO avançado pendente
- Visual promocional extra pendente

**Próximo passo recomendado:** Fechar os bloqueios obrigatórios antes de publicar.

---

## Acceptance criteria
This H2 bundle is complete when:
- operator can clearly see what blocks publish
- operator can clearly see what is optional
- readiness feels operational instead of decorative
- package frozen is not confused with publish-ready confidence
- Website contract state is understandable in practical language
- the branch remains green after the changes

---

## Risk level
Low if treated as:
- UI and interpretation first
- reuse of existing policy data where possible
- no broad logic rewrite

---

## Recommended next step after H2 bundle
Once H2 is visibly implemented and green:
1. move to H3 story-first comfort
2. simplify redundant messaging carefully where needed
3. keep accumulating only in `feat/studio-operational-integration-v1`
