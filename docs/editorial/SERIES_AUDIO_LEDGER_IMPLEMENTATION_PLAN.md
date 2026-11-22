# Series adaptation and audio approval ledger — implementation plan

Status: design gate for issue #57. This document does not create approvals, consent, audio, or production records.

## Objective

Build a separately versioned miniseries adaptation and narration workflow. The audiobook remains the complete spoken edition of the approved story; it must never be used as miniseries narration. Current output remains `animatic_only` until a genuine character-animation pipeline and its review gates exist.

## Data model (first implementation, local server-owned storage)

Use a server-owned append-only ledger under the Studio's protected data storage. Do not accept ledger records from client payloads or project JSON. The ledger must be integrity-checked on read and written atomically. Each record includes:

- record ID, event type, creation timestamp and server actor context;
- saga/IP ID, project ID, story revision/checksum, episode ID and language;
- adaptation script revision, non-empty script text and SHA-256;
- editorial decision ID, decision, reviewer, timestamp, script revision and matching checksum;
- audio artifact relative path, checksum, media type and measured duration;
- audio approval decision ID, reviewer, timestamp and checksum binding;
- voice identity ID, consent record ID, scope `series_narration`, grantor, timestamp, expiry/revocation status and scope details;
- provenance: approved script revision → generated/recorded audio artifact → audio approval;
- revocation/supersession references; never overwrite prior approval events.

## Trust and storage requirements

1. Resolve storage paths only through the server's protected storage root; reject traversal and symlink escapes.
2. Store audio and scripts as server-owned artifacts; verify checksum and file type on every approval resolution.
3. Ledger append must be atomic, locked against concurrent writes, and reject duplicate event IDs. A tampered or malformed ledger fails closed.
4. The resolver returns a path only when all current approvals, consent scope, checksum, revision, language and revocation checks match. Otherwise return a typed blocker, not a guessed path.
5. Project JSON/API payloads may contain display metadata only; they cannot mint approval or consent.
6. Do not clone a voice. A recorded or synthesized voice requires documented authorization covering this specific series-narration use.

## Workflow and API (planned)

- Create adaptation draft from the approved story revision; preserve source lineage and generate a distinct script.
- Save immutable script revisions; human review approves a specific revision/checksum.
- Produce or import dedicated series audio only after script approval and consent validation.
- Human audio review approves a specific artifact checksum; any edit regenerates checksum and invalidates prior approval.
- Renderer consumes only resolver-returned approved series audio and approved animation shots. Audiobook fields are ignored and explicitly tested.
- Export remains `animatic_only`, `finalizable=false` until character animation, visual continuity, audio and pedagogical/editorial gates all pass.

## Acceptance tests

- Audiobook path and legacy `audio_path` never reach the series renderer.
- Draft/unapproved adaptation, script, audio, missing consent, revoked consent, wrong voice scope, checksum mismatch, stale story revision, wrong language, tampered ledger and path traversal all block audio resolution.
- Valid approved script + matching dedicated audio + matching consent resolves audio, but only enables animatic review (not final miniseries).
- Approval events are append-only; supersession/revocation does not erase history.
- Tests use synthetic fixtures and temporary storage; they must not create real approval or consent.

## Sequencing

1. Implement storage/ledger and integrity primitives with tests.
2. Add adaptation/script revision endpoints and UI.
3. Add consent registry and dedicated audio artifact workflow.
4. Add human approval UX with checksum-bound decisions.
5. Connect renderer only to the fail-closed resolver.
6. Build real animation pipeline and its own finalization gates.

## Explicitly out of scope

No Supabase schema changes, production-data edits, secret access, provider calls, paid services, automatic approval, publication, merge or deployment in this work.
