# STUDIO WEBSITE OPERATIONAL HANDOFF V1

## Purpose
Define the operational handoff between Studio and Website for the real post-merge phase.

This document exists to validate that:
- Studio remains the source of truth
- Website remains the projection/runtime layer
- publish, sync and reconcile are operationally trustworthy

---

## 1. Studio side responsibilities

The Studio must own:
- editorial truth
- commercial truth
- package freezing
- readiness logic
- credit derivation
- continuity and typography intent
- publish decision
- Website control observation

The Studio should not depend on the Website for editorial reconstruction.

---

## 2. Website side responsibilities

The Website must own:
- intake of approved public package/envelope
- persistence of public-facing commerce/publication runtime data
- public runtime materialization
- status exposure
- reconcile visibility
- revalidate / unpublish operational endpoints

The Website should not become the source of truth for editorial/commercial logic.

---

## 3. Handoff validation points

### Publish handoff
Validate:
- Studio publishes only frozen/approved public material
- Website accepts only the intended contract
- auth is enforced
- receipt is explicit enough

### Persistence handoff
Validate:
- publication identity is stable
- variant identity is stable
- product materialization is stable enough
- Studio metadata survives the trip

### Observation handoff
Validate:
- Studio can read Website health
- Studio can read Website summary
- Studio can read Website catalog/publications
- Studio can detect divergence signals

### Control handoff
Validate:
- Studio can revalidate publication projection
- Studio can unpublish projection when needed
- control actions are explicit and safe

---

## 4. Divergence classes to watch

### Class A — metadata drift
Examples:
- checksum mismatch
- project_version mismatch
- stale payload metadata

### Class B — materialization drift
Examples:
- publication marked published but no active product
- published publication with zero published variants
- active products under unpublished publication

### Class C — operator drift
Examples:
- operator cannot understand current Website state
- operator cannot tell whether publish worked
- operator cannot identify next corrective action

---

## 5. Acceptance criteria for handoff trust

Handoff is trustworthy when:
- publish result is clear
- Website status is readable from Studio
- reconcile output has operational meaning
- operator can tell whether the public layer matches the Studio intent
- corrective action path is visible without developer interpretation

---

## 6. Safe next improvements after audit

Only consider improvements that are:
- incremental
- observable
- compatible with current green state
- clearly tied to real operational friction

Priority examples:
- stronger publish receipt visibility
- clearer reconcile language
- better defaults in publish flow
- stronger guidance around required vs optional outputs
- more obvious next action after each major phase
