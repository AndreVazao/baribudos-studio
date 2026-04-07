# H2 READINESS CREDIBILITY IMPLEMENTATION V1

## Objective
Improve publish/readiness credibility in Baribudos Studio so operators can clearly distinguish:
- what truly blocks publish
- what is optional enrichment
- what is already safe enough to proceed

This block must remain low-risk, Studio-side first, and compatible with already green paths.

---

## Problem to solve
The system may already expose readiness/policy data, but the operator can still experience friction if:
- blockers are mixed with optional enrichments
- readiness feels decorative instead of operational
- package frozen and ready to publish are confused
- Website contract status is visible but not operationally explained

---

## Operational target
After H2, the operator should be able to answer immediately:
- can I publish now?
- what exactly is blocking me?
- what is optional and can wait?
- what still needs editorial/commercial completion?
- is the Website contract good enough or not?

---

## Scope
This H2 block covers:
- readiness presentation clarity
- required vs optional distinction
- blocker visibility
- clearer publish gating explanation
- stronger operator trust in readiness/policy UI

This H2 block does **not** cover:
- architectural redesign
- major backend policy rewrite unless a real blocker proves it necessary
- Website-side redesign
- large dashboard restructuring

---

## Recommended implementation surfaces
Primary surfaces most likely to change:
- package/readiness area
- publication policy panel or box
- publish gating explanation in Website control
- supporting operator-facing labels/messages

---

## Canonical readiness model
### Required blockers
These must block publish.
Examples:
- project not ready for publish
- publication package not frozen
- Website contract not acceptable enough
- required core metadata missing
- required output missing under current policy

### Optional enrichments
These should not block publish by default unless policy explicitly says so.
Examples:
- advanced SEO polish
- extra campaign visuals
- additional media variants
- non-critical presentation enrichments

### Ready state
Ready means:
- no required blockers remain
- package is frozen
- Website contract is sufficiently valid
- publish can proceed with confidence

---

## Safe implementation targets
### H2.1 Required vs optional split
Show two explicit buckets:
- `Bloqueia publicação`
- `Melhorias opcionais`

### H2.2 Clear readiness summary
Show one compact readiness summary such as:
- `Pronto para publicar`
- `Ainda bloqueado`
- `Pronto com melhorias opcionais pendentes`

### H2.3 Blocker list visibility
Make required blockers easy to scan.
Avoid hiding them in dense policy text.

### H2.4 Contract meaning in operator language
Translate Website contract state into clearer operator language.
Examples:
- `Contrato Website válido para publicar`
- `Contrato Website ainda incompleto`
- `Contrato Website precisa de revisão antes de publicar`

### H2.5 Freeze vs ready distinction
Make these distinct:
- package frozen
- ready to publish

A frozen package is necessary, but not automatically the same as ready-to-publish confidence.

---

## Minimal UI recommendation
Inside readiness/policy area, aim for:
1. one primary readiness label
2. one short meaning line
3. one explicit blockers bucket
4. one explicit optional improvements bucket
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
H2 is acceptable when:
- operator can clearly see what blocks publish
- operator can clearly see what is optional
- readiness feels operational rather than decorative
- package frozen is no longer confused with publish-ready
- Website contract state is understandable in practical language

---

## Risk level
Low if approached as:
- presentation and interpretation first
- existing policy data reused where possible
- no large policy engine rewrite

---

## Recommended follow-up after H2
Once H2 is visibly stable:
1. move to H3 story-first comfort
2. keep improvements incremental in `feat/studio-operational-integration-v1`
3. avoid reopening architecture while improving usability
