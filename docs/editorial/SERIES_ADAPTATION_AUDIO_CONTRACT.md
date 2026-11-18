# Series adaptation and narration contract

Status: fail-closed implementation gate; not an editorial approval or production record  
Scope: Studio project output metadata; no database migration or production-data mutation

## Non-negotiable separation

The audiobook is the complete spoken edition of the canonical story. It must never be supplied to the miniseries renderer as narration.

A miniseries requires its own adaptation script, its own separately approved narration/dialogue track, and traceable voice consent. The current FFmpeg slideshow renderer is an **animatic renderer**, not a character-animation pipeline. Every output from it must remain **animatic_only** and **finalizable=false**, even when a separate technical audio track is supplied in an isolated renderer test.

## Current trust boundary

No project-embedded approval metadata is currently trusted as an authoritative approval source. The resolver deliberately returns no series-audio path until an immutable, server-owned editorial approval ledger exists and can be read by the backend. A field such as status=approved, a client-supplied decision ID, or a consent-shaped JSON object is not sufficient by itself.

Consequences:

- Studio factory, manual production pipeline and video export route do not pass any project audio to the miniseries renderer.
- The legacy audiobook output and legacy audio_path field are ignored.
- Missing authoritative approval evidence means silent animatic output only.
- No approval, consent, voice, script or asset is created or inferred by this change.

## Future ledger record requirements

When the immutable approval ledger is implemented, a series adaptation must be linked to an IP, story revision, episode and language. The record must bind:

1. Non-empty adaptation script text, revision and SHA-256.
2. Human editorial decision ID, decision, actor, timestamp, exact script revision and checksum.
3. Separate audio artifact path and SHA-256, with a human decision bound to that exact checksum.
4. Voice identity and consent record with matching voice ID, scope=series_narration, grantor, timestamp and revocation state.
5. Provenance from the approved script revision to the audio artifact.

The future resolver must verify the ledger record server-side and re-hash the file before returning a path. It must not trust an approval object supplied by an API request or ordinary project JSON.

## Output semantics

The current renderer emits artifact_kind=animatic, status=animatic_only, production_status=animatic_only, finalizable=false, and blocked_reason=real_character_animation_pipeline_not_implemented.

A separate approved narration track may eventually be included in an animatic for technical review, but this does not turn the output into a final miniseries. Real approved character animation, visual continuity and editorial/pedagogical review remain separate gates.

## Validation scope

Automated tests use temporary files and synthetic bytes/audio. They prove routing and output-state behavior only. They do not create editorial approval, voice consent, publishable content or real Baribudos assets.
