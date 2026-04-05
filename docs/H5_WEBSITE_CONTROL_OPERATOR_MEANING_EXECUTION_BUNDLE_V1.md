# H5 WEBSITE CONTROL OPERATOR MEANING EXECUTION BUNDLE V1

## Objective
Turn H5 into a small, reviewable implementation bundle inside `feat/studio-operational-integration-v1`.

This bundle exists to make Website control surfaces feel operationally meaningful for daily use, without reopening architecture and without destabilizing green paths.

---

## Problem
The Studio already exposes Website control data, but operators can still hesitate because:
- health/status information can feel too technical
- publication detail can require developer intuition
- divergence/reconcile reasons may not feel actionable enough
- next corrective action is not always explicit

---

## Scope of this execution bundle
This H5 execution bundle should cover:
- clearer Website health meaning
- clearer publication detail meaning
- clearer divergence/reconcile meaning
- stronger next corrective action guidance
- lower technical interpretation burden in daily use

This H5 bundle should not cover:
- Website architecture redesign
- new control-plane architecture
- deep backend refactor unless a real blocker appears
- public storefront redesign

---

## Main surfaces expected to change
Studio-side first, primarily:
- `WebsiteControlPanel.jsx`
- divergence section
- publication detail section
- operator-facing Website control labels/messages

---

## Recommended visible operator model
### Primary labels
- `Website operacional`
- `Website com atenção necessária`
- `Website indisponível`
- `Materialização confirmada`
- `Materialização incompleta`
- `Divergência detetada`
- `Próximo passo recomendado`

### Core operator questions
- is the Website healthy enough?
- is this publication really reflected?
- is there mismatch or incomplete reflection?
- what should I do next?

---

## Implementation checklist
### H5.1 Health meaning
- [ ] translate health/status into clearer operator language
- [ ] reduce dependence on backend intuition

### H5.2 Publication detail meaning
- [ ] make publication detail easier to read operationally
- [ ] clarify whether the publication is properly reflected
- [ ] reduce interpretation burden around variants/products state

### H5.3 Divergence meaning
- [ ] translate divergence reasons into more practical language
- [ ] help operator understand what kind of mismatch exists

### H5.4 Next corrective action
- [ ] show a clearer next safe action where possible
- [ ] examples: revalidar, rever publicação, abrir reconcile, corrigir bloqueio antes de republicar

### H5.5 Lower technical noise
- [ ] keep useful technical evidence available
- [ ] but make operator-facing meaning primary

---

## Minimal UI recommendation
Inside Website control surfaces, aim for:
1. one clear health meaning label
2. one clear publication/control meaning label
3. one explicit divergence meaning when relevant
4. one next recommended action

### Example
**Estado do Website:** Website operacional
**Significado:** O Website está acessível e a responder corretamente ao Studio.

**Estado da publicação:** Materialização confirmada
**Significado:** A publicação já está refletida no lado público/comercial.

**Próximo passo recomendado:** Rever status final ou continuar operação.

---

## Acceptance criteria
This H5 bundle is complete when:
- operator can understand Website health without backend intuition
- publication detail feels more operationally readable
- divergence reasons feel more meaningful in practical language
- next safe action is easier to identify
- Website control feels less developer-shaped in daily use
- the branch remains green after the changes

---

## Risk level
Low if treated as:
- interpretation and wording first
- UI grouping second
- no major control-plane or backend rewrite

---

## Recommended next step after H5 bundle
Once H5 is visibly implemented and green:
1. review H1-H5 together for consistency
2. remove redundant legacy messaging carefully
3. move toward final branch exit criteria only when operator experience is clearly stronger than current `main`
