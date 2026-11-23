# Authenticated Editorial Approval — Implementation Contract

**Date:** 2026-11-23  
**Status:** Design contract / implementation gate only  
**Scope:** Studio editorial approval of immutable story revisions  
**Safety:** Documentation only. No auth runtime, database, production, or credential changes.

## 1. Problem statement

The immutable story revision ledger records content snapshots and integrity checksums, but it does not authenticate a reviewer or grant production permission. Approval fields in project JSON (including `approved`, `approval_state`, and `editorial_status`) are mutable client-controlled data and must never be authoritative for production, packaging, publication, or release.

The Studio currently lacks a demonstrated central server authentication boundary. The existing identity/client patterns and route inventory are not sufficient to build an approval endpoint safely in isolation. This design must be implemented only after central authentication and server-side authorization are established.

## 2. Required invariants

1. **Default deny:** missing, invalid, expired, revoked, or ambiguous identity/session → no approval or production.
2. **Server-authenticated actor:** reviewer identity is derived exclusively from validated server session/token context, never request payload, project JSON, localStorage, PIN profile, or caller-supplied actor ID.
3. **Immutable target:** approval binds to an exact revision ID and content SHA-256, not a project/story mutable object.
4. **Canon binding:** approval binds to IP, saga, locale, canon version/hash, and age band/brief version where those influence editorial content.
5. **Decision immutability:** approval/rejection is an append-only decision event. Corrections create a new event with explicit supersession/revocation; no silent edits.
6. **Change invalidation:** any content, locale, canon, age, or editorial-brief change creates a new revision/hash and requires new review.
7. **Separate permissions:** story editing, reviewing, approving, generating media, publication, and commercial administration are distinct capabilities.
8. **No client trust:** client approval flags may be retained for compatibility/UI but are non-authoritative and must not open any backend gate.
9. **No self-approval policy decision:** product owner must explicitly choose whether author and approver may be the same authenticated person. Default proposed policy: require a distinct reviewer for release approvals.
10. **No silent production claim:** generated assets remain draft/needs-review until each output has independent validation and its required approval.

## 3. Proposed decision record

A future server-owned approval event should contain:

- decision_id (UUID, unique)
- event type and decision: approve / reject / revoke / supersede
- authenticated actor_id from server principal
- actor role/capability and scope snapshot (not a substitute for live authorization)
- project_id, story_id, revision_id
- content_sha256
- IP / saga / locale identity
- canon_version and canon_sha256
- age band and editorial brief/version hash
- decision timestamp (UTC, server generated)
- optional reviewer note (bounded, sanitized, non-secret)
- previous decision reference / superseded decision ID
- audit correlation/request ID

Do not persist session tokens, PINs, passwords, secret values, or full principal/session payloads in the decision record.

## 4. Server-side flow

1. Authenticate request using the future central session/auth middleware.
2. Resolve principal and enforce reviewer capability plus project/IP ACL server-side.
3. Load revision from the immutable ledger; validate ledger integrity and requested revision ID.
4. Recompute content hash and compare with revision record; mismatch or integrity failure blocks.
5. Resolve and verify canon/brief snapshots and their hashes.
6. Verify revision is reviewable, not already superseded, and policy permits this actor to approve it.
7. Append a decision event using concurrency-safe append/transaction semantics; unique/idempotency key prevents duplicate approvals.
8. Return a minimized decision DTO; do not echo secrets or mutable project approval flags.
9. For rejection/revocation, append an event and require a new review for changed content or a later approval event.
10. Production gate independently re-resolves authenticated/authorized decision and all bound hashes at execution time.

## 5. Fail-closed production gate

The production pipeline must accept only an authoritative server-side decision with all of these verified:

- decision is APPROVE and not revoked/superseded
- reviewer principal exists and authorization remains valid for the operation
- exact story revision ID exists and its content checksum matches
- IP/saga/locale/age/editorial brief and canon hashes match current frozen inputs
- requested output artifact is permitted by the approved scope
- story/revision is not stale, edited, or replaced
- all independent language/safety/editorial validation requirements are complete

Any missing field, storage corruption, exception, mismatch, or unavailable approval service must block production. Never fall back to project JSON flags or a default owner/PIN profile.

## 6. Capability and scope proposal

- `story.read`: view assigned project/revision
- `story.edit`: create a new revision; never mutate an existing ledger revision
- `story.review`: submit review feedback
- `story.approve`: approve/reject within assigned IP/project scope
- `media.generate`: request draft media for eligible revisions
- `production.execute`: run approved, scoped production jobs
- `publication.release`: release/publish after separate readiness checks
- `admin.users` and `admin.secrets`: owner/admin only, separate from editorial capabilities

Capability checks are server-side and scope-aware. Role names alone are insufficient. No route should rely on a frontend `canEditorialApprove` flag as enforcement.

## 7. Revision lifecycle

`generated/editable → revision-created → review-pending → approved | rejected`

Edits after revision creation produce a new revision. A rejection is recorded, not erased. Re-review of changed content creates a new decision tied to the new revision. Revoke/supersede events invalidate prior approval for execution. Editorial approval is not publication approval and does not imply ebook, audiobook, illustration, animation, or series outputs are complete.

## 8. Volume and media rules

- One approved story revision is eligible for story-level media planning only after its own gate.
- A volume guide/compilation is gated on exactly five distinct approved story revisions sharing the IP, saga and locale.
- Never generate or mark a parent guide/compilation as ready from a single story.
- Audiobook script, miniseries adaptation, illustrations, animatic/slideshow and final animation are distinct artifact types and need their own status/validation.
- A slideshow or animatic must never be represented as a final animated miniseries.

## 9. Negative test matrix (required before merge)

### Authentication / authorization
- anonymous request → 401
- invalid, expired, revoked session → 401
- authenticated non-reviewer → 403
- reviewer without IP/project scope → 403
- request-supplied actor spoofing ignored/rejected
- project JSON approval flags cannot grant permission
- reviewer role/capability downgrade blocks subsequent approval/production

### Revision and decision integrity
- unknown revision → 404/blocked
- tampered content or ledger hash → integrity failure / blocked
- canon, locale, age or brief hash mismatch → blocked
- concurrent duplicate decision → one canonical event / deterministic idempotent result
- append failure or approval storage unavailable → blocked
- rejection/revocation/supersession invalidates prior approval
- edit after approval creates new revision and is not covered by old decision

### Production
- client approval flags alone → blocked
- stale decision or mismatched revision → blocked
- exactly five distinct approved revisions required for volume guide/compilation
- one story cannot open volume-level guide/compilation gate
- separate output scope cannot be inferred from story approval
- no endpoint leaks tokens, PINs, secret values, filesystem paths or internal storage DTOs

## 10. Rollout prerequisites and sequence

1. Finish central authentication/session/revocation model and cross-client contract (desktop + mobile).
2. Establish server principal, capability checks and project/IP scope; close route inventory P0s before any network exposure.
3. Define protected storage or transactional persistence, backups, concurrency semantics, recovery and retention.
4. Implement approval event ledger and API in a dedicated small PR.
5. Add production gate integration in a separate PR; remove reliance on mutable approval flags.
6. Add tests above, including negative HTTP tests and concurrency.
7. Confirm exact-SHA CI; review threat model and client integration; no production deployment until explicit release approval.

## 11. Current status

- Immutable story revision ledger exists and is evidence of content history only.
- Authenticated reviewer approval does **not** exist yet.
- The Studio route surface still requires a coordinated central-auth migration; adding isolated approval auth is unsafe.
- Production remains blocked; this document is a proposal and does not change runtime behavior.
