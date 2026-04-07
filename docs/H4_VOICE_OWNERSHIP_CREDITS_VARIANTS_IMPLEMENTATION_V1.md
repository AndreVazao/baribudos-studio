# H4 VOICE OWNERSHIP / CREDITS / VARIANTS IMPLEMENTATION V1

## Objective
Make voice ownership, credited naming and editorial variants easier to understand, trust and operate in daily Baribudos Studio use.

This block should improve legal/editorial clarity and reduce repetitive friction without reopening architecture and without destabilizing already green paths.

---

## Problem to solve
The Studio already carries the right concepts, but operators can still experience friction if:
- real voice owner vs credited name is not instantly clear
- editorial variants are visible in data but not intuitive in operation
- AudioCast assignment creates repeated work
- usage restrictions or warnings are not obvious enough

---

## Operational target
After H4, the operator should be able to answer immediately:
- who is the real owner of this voice?
- what name will appear in credits?
- is this a true original voice or an editorial variant?
- can this voice/variant be used safely in this context?
- what is the next correct step when assigning voices in AudioCast?

---

## Scope
This H4 block covers:
- owner vs credited-name clarity
- editorial variant visibility
- safer usage interpretation
- lower friction in audio cast assignment
- stronger trust in credits derivation

This H4 block does **not** cover:
- new clone engine architecture
- destructive redesign of voice data model
- large backend rewrite unless a real blocker proves it necessary
- public Website redesign

---

## Recommended implementation surfaces
Primary surfaces most likely to change:
- `VoiceProfilesPanel`
- `AudioCastPanel`
- package/product credits visibility where relevant
- operator-facing labels/messages around voice usage and assignment

---

## Canonical operator model
### Real owner
The real owner must remain explicit and preserved.

### Credited name
The credited name must be clearly separated from the real owner identity.

### Editorial variant
The operator must understand that a variant is not the destruction or replacement of the original voice identity.
It is a controlled editorial variation linked to the original owner.

### Usage confidence
The Studio should help the operator understand whether a voice/variant is safe and suitable for the intended use.

---

## Safe implementation targets
### H4.1 Owner vs credited-name clarity
Make it visually obvious which field means:
- real voice owner
- credited/public display name

### H4.2 Variant visibility
Make it easier to see when a profile is:
- original voice
- editorial variant
- linked to which original owner/profile

### H4.3 Safer usage explanation
Surface clearer operator language such as:
- safe to use
- review recommended
- usage needs attention
- credits will use `<credited name>` while owner remains `<real owner>`

### H4.4 Lower friction in AudioCast assignment
Reduce repeated work in assigning the same voice logic again and again.
Examples:
- clearer visibility of preferred/default assignment
- clearer distinction between narrator and character usage
- clearer warnings when an assignment feels inconsistent

### H4.5 Credits trust
Make operator confidence stronger that automatic credits will derive the right public attribution while preserving real ownership internally.

---

## Minimal UI recommendation
Inside voice surfaces, aim for:
1. one clear owner field meaning
2. one clear credited-name field meaning
3. one visible original vs variant indicator
4. one short usage-confidence message where relevant
5. one next recommended action during cast assignment

### Example
**Dono real:** Maria Silva
**Nome para créditos:** Voz da Avó Baribuda
**Tipo:** Variante editorial ligada ao perfil original
**Uso recomendado:** Seguro para narração desta coleção
**Próximo passo recomendado:** Aplicar esta voz ao papel de narradora

---

## Acceptance criteria
H4 is acceptable when:
- operator can distinguish owner from credited name without hesitation
- operator can distinguish original voice from editorial variant
- credits logic feels trustworthy
- AudioCast assignment causes less repeated friction
- unsafe or unclear usage cases are easier to detect

---

## Risk level
Low to medium if approached as:
- label clarity first
- usage interpretation second
- repeated-work reduction third
- no deep data-model rewrite unless truly necessary

---

## Recommended follow-up after H4
Once H4 is visibly stable:
1. move to H5 Website control meaning in operator language
2. keep all improvements incremental inside `feat/studio-operational-integration-v1`
3. continue protecting `main` until the operational branch is clearly comfortable for daily use
