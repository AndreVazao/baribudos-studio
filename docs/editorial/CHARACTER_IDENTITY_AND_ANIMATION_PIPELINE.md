# Character identity and animation pipeline

Status: architecture and validation contract, 18 November 2026

## Non-negotiable identity rule

A character is an individually versioned asset, not a prompt that is re-created independently for each illustration. Its stable ID and approved revision are referenced by every book page, cover, storyboard, animation shot, voice role and localized edition.

The following are identity invariants unless an explicitly approved new life-stage revision says otherwise:

- anatomy, silhouette, body proportions and face landmarks;
- eye shape, size, position and colour;
- nose, mouth, ears, hands, feet and other identifying geometry;
- base fur/skin/hair colours, materials, texture and permanent markings;
- character-specific visual identifiers.

Pose, expression, camera, lighting, environment and approved modular clothing may vary. Seasonal outfits are separate assets attached to the same character ID/revision. Clothing must not alter body geometry or face identity. Temporary narrative effects (mud, water, paint, costume) are scene state and must be reversible; they do not rewrite the canonical model.

Ageing is not an automatic mutation. It creates a new, explicitly approved life-stage revision linked to the original, while preserving historical revisions and published assets.

## Canonical visual package

A recurring visual character is not production-ready until its package contains:

1. Stable character ID and approved revision.
2. Front, three-quarter, side and back turnarounds.
3. Neutral pose and scale/reference sheet.
4. Expression sheet with approved facial shapes.
5. Source model and material/texture references.
6. Reusable rig with documented controls and skeleton.
7. Approved wardrobe assets, separately versioned.
8. Checksums and provenance for source assets.

A character can be text-only/non-visual only when editorially declared as such. A missing package must never be silently treated as approved.

## Free-first production toolchain

- Blender: canonical editable 3D source, materials, rigging, scene layout, animation and rendering.
- FFmpeg/FFprobe: audio/video assembly, transcodes and technical inspection.
- Python validation: stable IDs, revision references, required asset presence, checksums, render metadata and media-stream checks.
- Git/LFS or the approved asset store: source/version lineage. Large binary assets should not be committed blindly into ordinary Git history; storage and licensing must be reviewed before adoption.

No paid generator or subscription is required by this architecture. Image generators may be used for exploration or environment concepts, but their per-shot character redraws are not canonical production assets.

## Animation shot workflow

1. Approved storyboard references character IDs and exact approved revisions.
2. Shot setup loads the canonical model, rig, materials and wardrobe package.
3. Animation uses reusable actions/controls; dialogue timing drives facial/lip controls where supported.
4. Render short shots (for example, 5–10 seconds where practical), retaining handles for transitions.
5. Validate that the rendered shot contains temporal motion, not merely a still frame held for a duration.
6. Assemble shots in story order with dialogue, ambience, music, effects and subtitles.
7. Validate A/V sync, continuity, duration, frame rate, audio streams and source-to-render provenance.
8. Human editorial review approves the episode.

A slideshow or a pan/zoom over still illustrations may be useful as a storyboard animatic, but cannot pass as the finished miniseries animation.

## Age and duration adaptation

Narrative length, audiobook pacing and animation runtime are recommendations scoped to IP, age band, language and format. They are not universal hard limits. The Studio may propose adding a missing beat or shortening repetition, but changes must preserve meaning and receive editorial review. Audiobook and miniseries scripts/tracks are separate deliverables; neither should be speed-adjusted or padded to hit a timer.

## Current implementation status

- Runtime now preserves legacy Baribudos characters even when old records omit a display-name field.
- The character schema carries identity invariants and visual-package status.
- Production readiness validation rejects recurring visual characters whose package is not approved or lacks required source model, rig, turnarounds, expression sheet and neutral pose.
- The five Baribudos visual packages are still concept-only. No 3D model or rig has been approved yet.
- Current video generation still produces a slideshow/animatic. Blender scene building, rig assets, animation rendering and lip-sync remain future implementation work.

## Approval and change control

Changes to identity invariants require a new reviewed revision and explicit approval. Wardrobe revisions do not create a new character identity revision unless they change body/face geometry or permanent identifiers. Published outputs retain the exact source revision and checksums used at render time.
