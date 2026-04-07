# H4 VOICE OWNERSHIP / CREDITS / VARIANTS EXECUTION BUNDLE V1

## Objective
Turn H4 into a small, reviewable implementation bundle inside `feat/studio-operational-integration-v1`.

This bundle exists to improve voice ownership clarity, credited naming trust and editorial variant handling in daily Studio use without reopening architecture and without destabilizing green paths.

---

## Problem
The Studio already models the right voice concepts, but operators can still hesitate because:
- real owner and credited name are easy to confuse
- original voice vs editorial variant is not always operationally obvious
- cast assignment can create repeated work
- usage confidence is not always explicit enough

---

## Scope of this execution bundle
This H4 execution bundle should cover:
- clearer owner vs credited-name meaning
- clearer original vs variant visibility
- clearer usage-confidence language
- lower friction in AudioCast assignment
- stronger confidence in automatic credits

This H4 bundle should not cover:
- clone engine redesign
- destructive voice data-model changes
- broad Website/public redesign
- deep backend rewrite unless a real blocker appears

---

## Main surfaces expected to change
Studio-side only, primarily:
- `VoiceProfilesPanel`
- `AudioCastPanel`
- package/product credits visibility where relevant
- operator-facing voice usage labels/messages

---

## Recommended visible operator model
### Primary labels
- `Dono real`
- `Nome para créditos`
- `Tipo de voz: original`
- `Tipo de voz: variante editorial`
- `Uso recomendado`
- `Próximo passo recomendado`

### Core distinctions
- real owner identity
- credited/public display name
- original profile
- editorial variant linked to original owner/profile

---

## Implementation checklist
### H4.1 Owner vs credited-name clarity
- [ ] make `Dono real` visually explicit
- [ ] make `Nome para créditos` visually explicit
- [ ] reduce hesitation between internal ownership and public attribution

### H4.2 Original vs variant visibility
- [ ] make it easier to identify original voice vs editorial variant
- [ ] show variant linkage to original owner/profile more clearly
- [ ] reduce the risk of treating variants like identity replacements

### H4.3 Usage-confidence language
- [ ] show clearer operator language for safe/review/attention states
- [ ] reduce uncertainty about whether a voice/variant is suitable in context

### H4.4 Lower friction in AudioCast assignment
- [ ] reduce repeated work when assigning voices
- [ ] clarify narrator vs character assignment meaning where useful
- [ ] surface warnings when assignments feel inconsistent

### H4.5 Credits confidence
- [ ] strengthen trust that automatic credits will use the right public attribution
- [ ] preserve internal ownership clarity while credits remain operator-readable

---

## Minimal UI recommendation
Inside voice surfaces, aim for:
1. one clear owner field meaning
2. one clear credited-name field meaning
3. one visible original vs variant indicator
4. one short usage-confidence message
5. one next recommended action where relevant

### Example
**Dono real:** Maria Silva
**Nome para créditos:** Voz da Avó Baribuda
**Tipo de voz:** Variante editorial ligada ao perfil original
**Uso recomendado:** Seguro para narração desta coleção
**Próximo passo recomendado:** Aplicar esta voz ao papel de narradora

---

## Acceptance criteria
This H4 bundle is complete when:
- operator can distinguish owner from credited name without hesitation
- operator can distinguish original voice from editorial variant
- credits logic feels more trustworthy
- AudioCast assignment causes less repeated friction
- unclear or risky usage cases are easier to detect
- the branch remains green after the changes

---

## Risk level
Low to medium if treated as:
- label clarity first
- usage interpretation second
- repeated-work reduction third
- no deep data-model rewrite

---

## Recommended next step after H4 bundle
Once H4 is visibly implemented and green:
1. move to H5 Website control meaning
2. keep improvements incremental inside `feat/studio-operational-integration-v1`
3. continue protecting `main` until the branch clearly beats current `main` operationally
