# H5 WEBSITE CONTROL OPERATOR MEANING IMPLEMENTATION V1

## Objective
Make the Website control area in Baribudos Studio feel operationally meaningful for daily use, instead of requiring developer intuition.

This block should reduce interpretation burden and make control/status/reconcile information easier to act on, without reopening architecture and without destabilizing already green paths.

---

## Problem to solve
The Studio may already expose useful Website control data, but operators can still experience friction if:
- health, summary and catalog data feel too technical
- reconcile/divergence data exists but the practical meaning is not obvious
- publication detail is readable only to someone already thinking like a developer
- corrective next actions are implied instead of explicit

---

## Operational target
After H5, the operator should be able to answer immediately:
- is the Website operationally healthy?
- is the public/commercial layer in a good state?
- is this publication properly reflected on the Website?
- if something is wrong, what should I do next?

---

## Scope
This H5 block covers:
- health/status meaning in operator language
- clearer reconcile/divergence interpretation
- clearer publication detail meaning
- stronger next-step guidance in Website control surfaces
- lower technical interpretation burden in daily use

This H5 block does **not** cover:
- Website architecture redesign
- new control-plane architecture
- deep backend refactor unless a real blocker proves it necessary
- public storefront redesign

---

## Recommended implementation surfaces
Primary surfaces most likely to change:
- `WebsiteControlPanel.jsx`
- divergence / reconcile section
- publication detail section
- supporting operator-facing labels/messages

---

## Canonical operator questions to support
### Health
- Is the Website reachable and healthy enough for operation?

### Publication status
- Has the Website received and reflected the publication correctly?

### Reconcile
- Does the Website still match Studio intent?

### Corrective action
- If not, what is the next safe action?

---

## Safe implementation targets
### H5.1 Health meaning
Translate health/status information into clearer operator language.
Examples:
- `Website operacional`
- `Website com atenção necessária`
- `Website indisponível`

### H5.2 Summary meaning
Make summary counters feel operational, not decorative.
The operator should understand what the numbers mean for real usage.

### H5.3 Publication detail meaning
Reduce interpretation burden in publication detail.
Make it easier to understand:
- what publication is being inspected
- whether it is reflected correctly
- whether variants/products are in a healthy state

### H5.4 Divergence meaning
Make divergence reasons feel like operational findings, not just raw mismatch data.
Examples:
- Website recebeu, mas ainda não reflete tudo
- publicação ativa sem produtos ativos
- materialização incompleta
- versão/checksum diferente da esperada

### H5.5 Next corrective action
Always show a clearer next action where possible.
Examples:
- revalidar
- rever publicação
- abrir reconcile
- corrigir bloqueio antes de republicar

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
H5 is acceptable when:
- operator can understand Website health without backend intuition
- publication detail feels operationally readable
- divergence reasons feel meaningful in practical language
- the next safe action is easier to identify
- Website control feels less developer-shaped in daily use

---

## Risk level
Low if approached as:
- interpretation and wording first
- UI grouping second
- no major control-plane or backend rewrite

---

## Recommended follow-up after H5
Once H5 is visibly stable:
1. review the full H1-H5 sequence for consistency
2. remove redundant legacy messaging carefully
3. continue only with incremental, low-risk improvements inside `feat/studio-operational-integration-v1`
