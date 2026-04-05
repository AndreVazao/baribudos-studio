# H3 STORY-FIRST COMFORT EXECUTION BUNDLE V1

## Objective
Turn H3 into a small, reviewable implementation bundle inside `feat/studio-operational-integration-v1`.

This bundle exists to improve the text-first daily-use flow in Baribudos Studio without reopening architecture and without destabilizing green paths.

---

## Problem
The Studio is text-first by design, but operators can still hesitate because:
- StorySourcePanel and StoryLayoutPanel do not always feel like one guided sequence
- raw story input vs shaped/editable story state can feel ambiguous
- save/edit actions may not create enough confidence
- the next step after story actions is not always explicit

---

## Scope of this execution bundle
This H3 execution bundle should cover:
- clearer story entry meaning
- clearer save/edit confidence
- clearer raw vs shaped distinction
- clearer next-step guidance after story actions
- clearer readiness-to-move-toward-illustration meaning

This H3 bundle should not cover:
- architectural redesign
- illustration pipeline redesign
- new editorial backend systems
- large panel rewrites unless a real blocker appears

---

## Main surfaces expected to change
Studio-side only, primarily:
- `StorySourcePanel`
- `StoryLayoutPanel`
- operator-facing messages around story save/edit
- supporting dashboard guidance if needed

---

## Recommended visible operator model
### Primary story flow labels
- `História por introduzir`
- `Texto guardado`
- `Pronto para edição e paginação`
- `Pronto para avançar para ilustração`

### Core distinctions
- raw story input
- shaped/editable story state
- stable-enough-for-illustration state

---

## Implementation checklist
### H3.1 Story entry clarity
- [ ] make StorySourcePanel feel unmistakably like the text entry point
- [ ] reduce ambiguity about where raw story text begins

### H3.2 Save/edit confidence
- [ ] show clearer feedback after story save/update
- [ ] make the last successful story action more visible
- [ ] reduce uncertainty about whether the current text is stored

### H3.3 Raw vs shaped distinction
- [ ] distinguish raw text input from shaped/editable story state
- [ ] make it easier to understand when the user should move into layout/pagination

### H3.4 Next-step guidance
- [ ] show one clear next recommended action after story actions
- [ ] examples: continue editing, move to layout, review story completeness

### H3.5 Readiness for illustration meaning
- [ ] help the operator understand when the story is stable enough to proceed to visuals
- [ ] reduce premature illustration work caused by uncertainty

---

## Minimal UI recommendation
Inside story-first surfaces, aim for:
1. one primary story-flow label
2. one short practical meaning line
3. one visible save/edit confirmation when relevant
4. one recommended next action

### Example
**Estado atual:** Texto guardado
**Significado:** A história já está guardada no Studio e pronta para edição/paginação.
**Próximo passo recomendado:** Abrir layout para organizar páginas e estrutura.

---

## Acceptance criteria
This H3 bundle is complete when:
- operator knows where story input starts
- operator trusts save/edit results more
- raw text and shaped story state are clearly distinguished
- next step after story actions is visible
- readiness to move toward illustrations is easier to understand
- the branch remains green after the changes

---

## Risk level
Low to medium if treated as:
- guidance and feedback first
- reuse of existing stage flow where possible
- no broad panel redesign

---

## Recommended next step after H3 bundle
Once H3 is visibly implemented and green:
1. move to H4 voice ownership / credits / variants clarity
2. keep simplifying friction without reopening architecture
3. continue only inside `feat/studio-operational-integration-v1`
