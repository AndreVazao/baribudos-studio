# Series adaptation and narration contract

Status: implementation gate, not an editorial approval or production record  
Scope: Studio project output metadata; no database migration or production-data mutation

## Non-negotiable separation

The audiobook is the complete spoken edition of the canonical story. It must never be supplied to the miniseries renderer as narration.

A miniseries requires its own adaptation script, its own approved narration/dialogue track, and traceable voice consent. The current FFmpeg slideshow renderer is an **animatic renderer**, not a character-animation pipeline. Every output from it must remain **animatic_only** and **finalizable=false**, even when a separate series track is present.

## Read-only project metadata consumed by the renderer

The optional project field is:

- outputs.series_adaptations[language]

The resolver accepts it only when all of the following are present and consistent:

1. Adaptation, script and audio states are explicitly approved.
2. Script contains non-empty text, a non-empty revision, and a SHA-256 matching the UTF-8 text.
3. Script decision contains id, decision=approved, decided_by, decided_at, and the same script revision and SHA-256.
4. Audio contains an existing file_path, a SHA-256 matching the file bytes, a non-empty voice_id, and an explicit audio decision with id, decision=approved, decided_by, decided_at, and the same audio SHA-256.
5. voice_consent contains id, status=granted, the matching voice_id, scope=series_narration, granted_by, and granted_at; a revoked consent is rejected.

The resolver does not create or infer any decision, consent, voice, script or asset. Missing or inconsistent evidence means no audio is passed to the renderer. The legacy audio_path field is ignored.

## Output semantics

The current renderer emits artifact_kind=animatic, status=animatic_only, production_status=animatic_only, finalizable=false, and blocked_reason=real_character_animation_pipeline_not_implemented.

A separate approved narration track may be included in the animatic for technical review, but this does not turn the output into a final miniseries. Real approved character animation, continuity and editorial/pedagogical review remain separate gates.

## Validation scope

Automated tests use temporary files and synthetic bytes/audio. They prove routing, metadata and checksum behavior only. They do not create editorial approval, voice consent, publishable content or real Baribudos assets.
