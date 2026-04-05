# OPERATIONAL SEQUENCE AFTER H1

## Purpose
Define the next safe execution order in the Studio operational integration branch after the first visible H1 slice is wired into the Website control panel.

This document exists to keep the post-H1 work sequential, low-risk and operationally meaningful.

---

## Current position
H1 already has:
- helper logic for publish confidence
- isolated UI card for publish confidence
- documented final integration step into `WebsiteControlPanel.jsx`

The next sequence starts **after** that visual wiring step is completed.

---

## Phase 1 — close H1 visibly in the Studio

### Goal
Finish the first operator-facing publish confidence slice.

### Required step
Integrate:
- `client/mobile-app/src/components/WebsitePublishConfidenceCard.jsx`
into:
- `client/mobile-app/src/components/WebsiteControlPanel.jsx`

### Acceptance
- state ladder visible
- receipt visible
- next step visible
- clearer operator failure language visible
- sent / received / materialized distinction visible

---

## Phase 2 — H2 readiness credibility and required-vs-optional clarity

### Goal
Make package/readiness feel operationally trustworthy instead of decorative.

### Safe improvement targets
- distinguish required blockers vs optional enrichments
- make missing critical items easier to scan
- improve wording around readiness and publish eligibility
- reduce ambiguity around frozen package vs ready to publish

### Main surfaces
- package/readiness area
- publication policy area
- publish gating explanation

### Risk
Low if kept at presentation and guidance level first.

---

## Phase 3 — H3 story-first comfort

### Goal
Make the text-first production path feel natural for daily use.

### Safe improvement targets
- make StorySourcePanel -> StoryLayoutPanel progression clearer
- improve save/edit feedback
- reduce ambiguity between raw text and shaped/editable text
- clarify when the user can move to illustration

### Main surfaces
- story source
- story layout
- dashboard guidance

### Risk
Low to medium depending on UI guidance changes.

---

## Phase 4 — H4 voice ownership / credits / variants clarity

### Goal
Make voice ownership and editorial credits easier to understand and trust in daily use.

### Safe improvement targets
- clearer owner vs credited name explanation
- clearer variant policy visibility
- reduce repeated work in audio cast assignment
- surface invalid/unclear usage earlier

### Main surfaces
- VoiceProfilesPanel
- AudioCastPanel
- package credits visibility

---

## Phase 5 — H5 Website control meaning in operator language

### Goal
Make Website control screens feel operational instead of developer-shaped.

### Safe improvement targets
- better meaning for health / summary / publications / reconcile
- more obvious next corrective action
- clearer divergence wording
- lower interpretation burden for family/team users

### Main surfaces
- Website control panel
- divergence section
- publication detail section

---

## Safe execution rule
Always prefer:
- small PRs
- low-risk UI/state interpretation changes first
- Studio-side changes before deeper backend changes
- clear operational evidence before expanding scope

Do **not** reopen architecture while executing this sequence.

---

## Merge discipline
Use `feat/studio-operational-integration-v1` as the accumulation branch.
Only merge to `main` when:
- the accumulated block remains green
- the visible operator experience is clearly improved
- no destabilizing regressions appear
