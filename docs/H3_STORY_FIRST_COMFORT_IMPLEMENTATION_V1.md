# H3 STORY-FIRST COMFORT IMPLEMENTATION V1

## Objective
Make the Baribudos Studio text-first production path feel natural, guided and comfortable for daily use.

This block should improve the real operator journey from story input to story shaping without reopening architecture and without destabilizing already green paths.

---

## Problem to solve
The Studio is text-first by design, but the operator can still experience friction if:
- StorySourcePanel and StoryLayoutPanel do not feel like one clear sequence
- raw text vs structured/editable story state is ambiguous
- save/edit actions do not produce enough confidence
- the user does not know when the story is ready to move into visuals

---

## Operational target
After H3, the operator should be able to answer immediately:
- where do I put the story text?
- what happens after I save it?
- when do I move from raw story input to shaping/layout?
- when is the story stable enough to proceed to illustrations?

---

## Scope
This H3 block covers:
- story input flow clarity
- story shaping progression
- save/edit confidence
- clearer text-first guidance
- better operator next-step visibility after story actions

This H3 block does **not** cover:
- architectural redesign
- new editorial backend systems
- large panel rewrites unless a real blocker proves them necessary
- illustration pipeline redesign

---

## Recommended implementation surfaces
Primary surfaces most likely to change:
- StorySourcePanel
- StoryLayoutPanel
- supporting dashboard guidance around stage progression
- operator-facing labels/messages after story actions

---

## Canonical operator journey
### Step 1 — insert story
The operator should understand clearly that this is the entry point for raw story text.

### Step 2 — save and confirm
The Studio should confirm that the story is stored and available for shaping.

### Step 3 — move to shaping/layout
The operator should see that the next natural action is editorial shaping/pagination.

### Step 4 — confirm readiness for visuals
The Studio should help the operator understand when the story is mature enough to proceed into illustration work.

---

## Safe implementation targets
### H3.1 Story entry clarity
Make StorySourcePanel feel unambiguous as the text-first entry point.

### H3.2 Save/edit confidence
Improve operator confidence after story save or update.
Examples:
- clearer success message
- clearer changed/saved state
- more obvious last action confirmation

### H3.3 Raw vs shaped distinction
Make the difference clear between:
- raw text input
- shaped/editable story state

### H3.4 Next-step guidance
After story actions, show a clearer next step such as:
- continue editing text
- move to layout/shaping
- review story completeness
- proceed to illustrations when stable enough

### H3.5 Readiness-for-illustration meaning
Help the operator understand when the story is stable enough for visual production.
This should reduce premature illustration work.

---

## Minimal UI recommendation
Inside story-first flow surfaces, aim for:
1. one clear entry message in StorySourcePanel
2. one visible confirmation after save/edit
3. one explicit distinction between raw input and shaped story state
4. one recommended next action

### Example
**Estado atual:** Texto guardado
**Significado:** A história já está guardada no Studio e pronta para edição/paginação.
**Próximo passo recomendado:** Abrir layout para organizar páginas e estrutura.

---

## Acceptance criteria
H3 is acceptable when:
- operator knows where story input starts
- operator trusts save/edit results
- raw text and shaped story state are clearly distinguished
- next step after story actions is visible
- user can tell when it is reasonable to proceed to illustrations

---

## Risk level
Low to medium if approached as:
- guidance and feedback first
- reuse of current stage flow where possible
- no major panel redesign unless really necessary

---

## Recommended follow-up after H3
Once H3 is visibly stable:
1. move to H4 voice ownership / credits / variants clarity
2. keep improvements incremental in `feat/studio-operational-integration-v1`
3. continue protecting `main` until the operational branch feels truly comfortable
