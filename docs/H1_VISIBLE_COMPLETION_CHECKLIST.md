# H1 VISIBLE COMPLETION CHECKLIST

## Purpose
Close the first visible H1 slice in the Studio operational integration branch with a strict, low-risk validation checklist.

This checklist starts **after** the final UI wiring step that inserts `WebsitePublishConfidenceCard.jsx` into `WebsiteControlPanel.jsx`.

---

## A. Wiring validation

### Required
- [ ] `WebsitePublishConfidenceCard.jsx` is imported in `WebsiteControlPanel.jsx`
- [ ] the card is rendered in the `Publicar e sincronizar Website` section
- [ ] the card appears after publication policy and before main publish actions
- [ ] no runtime error appears after render

---

## B. State ladder validation

### Required
- [ ] operator can see the state ladder clearly
- [ ] `Pacote pronto para publicar` appears only when package/readiness evidence supports it
- [ ] `Publicação enviada` does not pretend Website receipt already exists
- [ ] `Website confirmou receção` appears only when acknowledgement evidence exists
- [ ] `Website materializado` appears only when Website control evidence supports it
- [ ] `Divergência detetada` appears when reconcile/status evidence proves mismatch

---

## C. Receipt validation

### Required
- [ ] receipt card appears after successful Website acknowledgement
- [ ] `publication_id` is visible when available
- [ ] `variant_id` is visible when available
- [ ] `received_at` is visible when available
- [ ] sync label is visible
- [ ] receipt is not confused with full materialization

---

## D. Next-step validation

### Required
- [ ] one `Próximo passo recomendado` is visible
- [ ] next step changes according to current state
- [ ] operator can continue without guessing

---

## E. Failure-language validation

### Required
- [ ] failures show operator-first language
- [ ] primary label is understandable
- [ ] practical meaning is understandable
- [ ] one recommended next action is visible
- [ ] technical/raw backend language is not the main message

---

## F. Duplication control

### First safe pass
- [ ] legacy blocks remain acceptable during transition
- [ ] no severe contradictory messaging exists between old and new blocks

### After validation
- [ ] duplicated legacy operator messaging can be simplified safely in a follow-up pass

---

## G. H1 visible completion rule

The first visible H1 slice can be considered complete when:
- [ ] the new publish-confidence card is live in the Website control section
- [ ] operator confidence is visibly improved
- [ ] sent / received / materialized distinction is understandable
- [ ] failures read like operational language
- [ ] no backend/API redesign was needed
- [ ] the branch remains green

---

## H. Safe immediate next step after visible H1 completion

After this checklist is green:
1. simplify redundant legacy messaging carefully
2. move to H2 readiness credibility
3. continue accumulating improvements only in `feat/studio-operational-integration-v1`
