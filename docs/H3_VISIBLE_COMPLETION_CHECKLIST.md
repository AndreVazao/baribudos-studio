# H3 VISIBLE COMPLETION CHECKLIST

## Purpose
Close the first visible H3 slice in the Studio operational integration branch with a strict, low-risk validation checklist.

This checklist starts after the H3 story-first guidance layer is visibly wired into the real story surfaces.

---

## A. Story entry validation

### Required
- [ ] the story entry point is visibly clearer than before
- [ ] `StorySourcePanel` reads as the canonical raw-text entry surface
- [ ] the operator can tell where the story starts without hesitation

---

## B. Save/edit confidence validation

### Required
- [ ] saved-state confidence is visibly stronger
- [ ] the operator can tell when the current text is already stored
- [ ] story actions create less hesitation than before

---

## C. Raw vs shaped distinction validation

### Required
- [ ] raw story input and shaped/editable story state are more clearly distinguished
- [ ] `StorySourcePanel` feels text-first
- [ ] `StoryLayoutPanel` feels structure/layout-first

---

## D. Next-step guidance validation

### Required
- [ ] one next recommended action is visible where relevant
- [ ] the next action reduces uncertainty after story actions
- [ ] story progression feels calmer and more guided

---

## E. Illustration-readiness validation

### Required
- [ ] the operator has a clearer sense of when it is reasonable to move toward illustration
- [ ] the system reduces premature movement into visuals
- [ ] the signal remains guidance-first, not a heavy blocker

---

## F. Duplication control

### First safe pass
- [ ] legacy detail remains acceptable during transition
- [ ] no severe contradictory messaging exists between old and new story-flow elements

### After validation
- [ ] duplicated legacy wording can be simplified safely in a follow-up pass

---

## G. H3 visible completion rule

The first visible H3 slice can be considered complete when:
- [ ] story entry is clearly understood
- [ ] save/edit confidence is stronger
- [ ] raw vs shaped distinction is clearer
- [ ] the next step feels more obvious
- [ ] illustration-readiness guidance feels calmer and more useful
- [ ] the branch remains green

---

## H. Safe immediate next step after visible H3 completion

After this checklist is green:
1. move to the visible H4 voice/cast slice
2. keep all work inside `feat/studio-operational-integration-v1`
3. continue using PR `#5` as the single operational trail
