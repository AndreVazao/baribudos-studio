# OPERATIONAL EXECUTION MATRIX V1

## Purpose
Convert the operational audit phase into an executable matrix for real Baribudos Studio daily usage.

This document is for execution.
It is not architecture design.
It is not a rebuild plan.
It is the practical matrix for validating whether the Studio is comfortable, governable and reliable in real operation.

---

## Status model

Use this status model for every line item:
- GREEN = operationally ready
- YELLOW = works but causes friction or ambiguity
- RED = blocks or seriously weakens real use

Use this evidence model for every line item:
- technical evidence
- operator experience evidence
- publish/control evidence when relevant

---

## 1. Project bootstrap execution matrix

| Area | Expected outcome | Type | Status | Evidence | Friction | Fix priority |
|---|---|---:|---|---|---|---|
| project mode selection | operator understands official vs standalone vs hidden modes | mandatory | TBD |  |  | high |
| stage_modes setup | operator understands story/image/audio/video flow selection | mandatory | TBD |  |  | high |
| project creation success feedback | operator sees clear confirmation and next step | assisted | TBD |  |  | high |
| defaults quality | sensible default values reduce setup friction | automatic | TBD |  |  | medium |
| hidden-mode field clarity | hidden continuity/IP/saga fields are understandable | assisted | TBD |  |  | high |

Audit questions:
- does the user know what each project mode means?
- is the next action obvious after creation?
- are any fields too technical for family/team usage?

---

## 2. Story input and editorial shaping matrix

| Area | Expected outcome | Type | Status | Evidence | Friction | Fix priority |
|---|---|---:|---|---|---|---|
| StorySourcePanel clarity | user knows where and how to insert text | mandatory | TBD |  |  | high |
| raw text vs structured text clarity | no ambiguity on input style | assisted | TBD |  |  | high |
| StoryLayoutPanel usefulness | pagination/editing feels natural | mandatory | TBD |  |  | high |
| editorial completeness signal | user can tell when story is ready enough to move on | assisted | TBD |  |  | high |
| continuity / typography visibility | context rules are visible when relevant | optional | TBD |  |  | medium |

Audit questions:
- can a non-technical user understand the text-first flow?
- is there enough feedback after saving or editing?
- does the system explain when text is ready for the next stage?

---

## 3. Visual production matrix

| Area | Expected outcome | Type | Status | Evidence | Friction | Fix priority |
|---|---|---:|---|---|---|---|
| visual entry timing | users only start visuals at the correct time | assisted | TBD |  |  | medium |
| illustration pipeline clarity | visual generation controls are understandable | mandatory | TBD |  |  | high |
| consistency warnings visibility | character/IP consistency issues surface early | assisted | TBD |  |  | high |
| result feedback | user knows if a visual step succeeded or not | mandatory | TBD |  |  | high |
| optional polish controls | advanced controls do not clutter the main path | optional | TBD |  |  | low |

Audit questions:
- are users pushed into visuals too early?
- are failures actionable?
- is visual consistency protected without overcomplicating the flow?

---

## 4. Voice profile and audio cast matrix

| Area | Expected outcome | Type | Status | Evidence | Friction | Fix priority |
|---|---|---:|---|---|---|---|
| voice owner clarity | real owner remains explicit | mandatory | TBD |  |  | high |
| credited name clarity | credits are understandable and predictable | mandatory | TBD |  |  | high |
| variation policy clarity | variants are editorial, visible and non-destructive | mandatory | TBD |  |  | high |
| voice selection comfort | assigning voices is not repetitive or confusing | assisted | TBD |  |  | medium |
| AudioCastPanel clarity | narrator/character assignment is easy to read | mandatory | TBD |  |  | high |

Audit questions:
- can the family/team understand owner vs credited name vs variant?
- does the panel reduce or create repeated work?
- are unsuitable voice assignments clearly blocked or warned?

---

## 5. Outputs and package matrix

| Area | Expected outcome | Type | Status | Evidence | Friction | Fix priority |
|---|---|---:|---|---|---|---|
| output visibility | user can see which outputs exist and which are missing | mandatory | TBD |  |  | high |
| package freeze clarity | freeze action is intentional and well understood | mandatory | TBD |  |  | high |
| publish readiness credibility | readiness reflects real blocking state | mandatory | TBD |  |  | high |
| output priority understanding | user knows what is required vs optional | assisted | TBD |  |  | high |
| final review comfort | package can be reviewed before publish confidently | assisted | TBD |  |  | medium |

Audit questions:
- can the user tell what still blocks publish?
- do labels explain reality or just decorate the UI?
- is package freeze too easy or too obscure?

---

## 6. Website publish and control matrix

| Area | Expected outcome | Type | Status | Evidence | Friction | Fix priority |
|---|---|---:|---|---|---|---|
| publish action confidence | user trusts that publish really happened | mandatory | TBD |  |  | high |
| receipt visibility | Studio shows clear receipt/acknowledgement | mandatory | TBD |  |  | high |
| website health visibility | operator can see website operational state | assisted | TBD |  |  | medium |
| status / catalog / publications visibility | operator can observe public materialization clearly | assisted | TBD |  |  | high |
| reconcile clarity | divergence is visible and understandable | mandatory | TBD |  |  | high |
| remote actions clarity | revalidate / unpublish are safe and understandable | assisted | TBD |  |  | high |

Audit questions:
- does the Studio explain publish success in operator language?
- can the user understand what the Website actually received?
- when divergence exists, is the corrective next step obvious?

---

## 7. Daily usability matrix

| Area | Expected outcome | Type | Status | Evidence | Friction | Fix priority |
|---|---|---:|---|---|---|---|
| error messages | messages are understandable to real operators | mandatory | TBD |  |  | high |
| action feedback | success/failure feedback is immediate and clear | mandatory | TBD |  |  | high |
| defaults | sensible defaults reduce typing and confusion | automatic | TBD |  |  | high |
| guided flow | user can follow the path without guessing | assisted | TBD |  |  | high |
| technical noise control | advanced controls do not pollute family/team usage | assisted | TBD |  |  | medium |

Audit questions:
- where does a family/team user hesitate?
- where does an owner/admin want stronger control?
- where is friction repeated and therefore expensive?

---

## 8. Governance matrix

| Area | Expected outcome | Type | Status | Evidence | Friction | Fix priority |
|---|---|---:|---|---|---|---|
| role separation | owner/admin/contributor expectations are credible | mandatory | TBD |  |  | high |
| credential handling | secrets remain server-side and predictable | mandatory | TBD |  |  | high |
| deploy control clarity | operational controls are understandable | assisted | TBD |  |  | medium |
| db control clarity | operational database controls are understandable | assisted | TBD |  |  | medium |
| PR/merge discipline | changes remain incremental and safe | mandatory | TBD |  |  | medium |

---

## 9. Publish / sync / reconcile acceptance criteria

### Minimum acceptable for real initial operation
- publish creates a visible receipt
- Website reflects publication materialization clearly
- publication status can be read from Studio
- reconcile can expose divergence
- revalidate works when needed
- unpublish works when needed

### Minimum acceptable for mature daily operation
- users understand publish state without technical interpretation
- divergence reasons are explicit
- corrective actions are obvious
- control panel does not require developer intuition

---

## 10. Execution rule for this phase

Do not use this matrix to reopen architecture.
Use it to identify:
- friction
- missing defaults
- unclear guidance
- missing operational feedback
- missing or weak reconcile meaning

Use resulting fixes only if they are:
- incremental
- low-risk
- compatible with green paths
- aligned with Studio as source of truth
