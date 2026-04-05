# OPERATIONAL AUDIT CHECKLIST V1

## Objective
Transform the Baribudos Studio from a technically strong system into an operationally robust daily-use system without reopening architecture and without destabilizing green builds.

## Scope of this phase
This checklist is for real operational auditing after the main Studio and Website merges.

It does **not** reopen:
- Studio vs Website separation
- source of truth decisions
- repository fusion
- already green build pipelines

It focuses on:
- real usage flow
- friction reduction
- publish/sync/reconcile confidence
- operational governance
- daily usability for family/team

---

## 1. End-to-end real flow audit

Audit the full path with real content and record every friction point.

### Sequence to validate
1. create IP
2. create saga
3. create project
4. define project mode
5. define stage modes
6. input story text
7. paginate / edit story
8. create or validate continuity / typography context
9. generate illustrations
10. define voice profiles
11. define audio cast
12. generate outputs
13. freeze publication package
14. inspect readiness gates
15. publish to Website
16. inspect materialization on Website
17. inspect reconcile/divergence state
18. test remote controls from Studio

### For each step capture
- was the step obvious?
- was the correct next action visible?
- what inputs were mandatory?
- what defaults were weak or missing?
- what errors were unclear?
- where would a non-technical family user hesitate?

---

## 2. True production flow audit

Classify the Studio flow by operational mode.

### Mandatory
List steps that must happen before publish.

Target expectation:
- project exists
- text exists
- required metadata exists
- readiness gate passes
- publication package is frozen
- Website contract is valid enough to publish

### Optional
List steps that enrich quality but should not block the whole system unless explicitly required.

Examples:
- advanced SEO polish
- extra gallery assets
- additional audio variants
- non-critical campaign visuals

### Assisted
List steps where the Studio should guide the user but still require confirmation.

Examples:
- story pagination suggestions
- credit generation
- package assembly
- publish recommendation
- divergence warnings

### Automatic
List steps that should happen automatically whenever safe.

Examples:
- derived credits
- readiness recomputation
- package timestamps
- publication metadata stamping
- Website control status refresh

---

## 3. Panel order and operational clarity

Validate whether the panel order matches real production.

### Expected operator journey
1. project creation mode
2. story source
3. story layout / editorial text shaping
4. illustration pipeline
5. voice profiles
6. audio cast
7. outputs / production pipeline
8. package / readiness
9. Website control / publish / reconcile

### Audit questions
- does Dashboard guide this order clearly?
- are panels discoverable in the order people actually work?
- does the user understand what to do next without guessing?
- does the Studio overexpose technical controls too early?
- are operational controls visible at the correct moment?

---

## 4. Publish / sync / reconcile audit

Validate that Studio remains source of truth and Website remains runtime projection.

### Publish
Check:
- publication package exists
- publish action returns clear receipt
- project records Website sync state
- publication identifiers are stable

### Sync
Check:
- repeated publish is idempotent enough
- updated package updates Website consistently
- Studio sees current Website status without ambiguity

### Reconcile
Check:
- divergence is visible
- checksum / project_version mismatches are visible
- missing active products / variants are visible
- corrective action path is obvious

### Remote controls
Check:
- health
- summary
- catalog
- publication status
- revalidate
- unpublish

---

## 5. Publication package and outputs audit

Validate final package quality, not only structure.

### Credits
- real voice owner remains linked
- credited name is correct
- variation policy remains visible and non-destructive
- audio contributors are correctly derived

### Metadata
- editorial metadata is complete enough
- commercial metadata is coherent
- Website payload is clean and minimal enough
- continuity and typography are represented correctly

### Outputs
- ebook
- audiobook
- video
- guide

For each output capture:
- present or missing
- required or optional
- quality acceptable or not
- blocking or non-blocking

---

## 6. Daily usability audit

This system must be comfortable for family/team daily use.

### Validate
- error messages are understandable
- actions have enough confirmation and feedback
- forms have useful defaults
- repetitive friction is reduced
- hidden complexity stays hidden when possible
- operational language is clear

### Record specifically
- where a wife/admin user gets lost
- where an owner/super-admin expects stronger control
- where a content-only operator sees too much technical detail

---

## 7. Real content audit

Do not treat technical green states as final proof.

Audit with real:
- IPs
- sagas
- projects
- texts
- voice profiles
- audio casts
- assets
- publication packages
- Website publications

### Required outcome
Every major subsystem must be validated with at least one realistic content path.

---

## 8. Governance audit

### Permissions
Validate separation between:
- owner / super-admin
- admin editorial/commercial
- other contributors

### Credentials
Validate:
- local Studio credential handling
- Website API key handling
- no accidental secret exposure to frontend

### Operational discipline
Validate:
- PR discipline
- merge discipline
- no direct destabilizing changes in green paths
- control-plane changes remain incremental

---

## 9. Audit result template

For every audited item, classify as:
- green = operationally ready
- yellow = usable but uncomfortable / incomplete
- red = blocking for real usage

### Result fields
- area
- status
- evidence
- friction
- user impact
- recommended fix
- priority

---

## 10. Exit criteria for this phase

This phase is complete when:
- the true production flow is explicit
- the operator journey is clear
- the publish/sync/reconcile path is trusted
- the Website remains a clean projection layer
- the Studio is comfortable enough for real daily operation
- governance and permissions are credible enough for continued scaling
