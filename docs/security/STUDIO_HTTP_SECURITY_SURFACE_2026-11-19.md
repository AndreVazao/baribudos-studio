# Studio HTTP security surface — evidence snapshot

**Date:** 19 November 2026  
**Evidence source:** [Studio CI #616](https://github.com/AndreVazao/baribudos-studio/actions/runs/44312969350), artifact `studio-route-authorization-evidence`, generated from PR #60 head `420ab2e9630e4386f8d7ddbb98794888935360b1`.  
**Purpose:** establish a reproducible baseline before the coordinated authentication/RBAC migration. This is an inventory, not an authorization audit or proof that every route is exposed.

## Counts (two distinct scanners)

### Heuristic source inventory

- 78 route modules scanned.
- 233 handler declarations found.
- 233 handlers had no local authorization signal detected by the heuristic.
- 29 handlers reference client identity fields.
- 97 handlers have sensitive/operational signals.

These are heuristic counts. A local signal is not proof of correct authorization; no local signal is not proof of exposure. Imported dependencies, middleware, service-level guards and runtime behaviour require manual tracing.

### Runtime FastAPI manifest

- 219 registered `APIRoute` method/path entries.
- 6 additional non-`APIRoute` HTTP entries.
- 2 `StaticFiles` mounts.
- 0 top-level route dependency edges and 0 global FastAPI dependencies were reported by the manifest.
- 1 registered middleware: `CORSMiddleware` configured with wildcard origins, credentials enabled, wildcard methods and wildcard headers.

The static and runtime counts measure different things and must not be compared as if they were the same set.

## Non-API HTTP surface and mounts

| Surface | Methods/configuration | Inventory status |
|---|---|---|
| `/docs`, `/docs/oauth2-redirect`, `/redoc`, `/openapi.json` | GET/HEAD | Unclassified; decide exposure policy |
| `/public` | StaticFiles; directory configured and present | Authorization not verified by manifest |
| `/storage` | StaticFiles; directory configured and present | Authorization not verified by manifest; private-data risk |

Do not remove mounts or change authentication in isolation. Existing desktop/mobile/updater clients and public-approved asset delivery need a coordinated migration.

## Priority route groups for manual handler → service review

The manifest includes, among others:

- **Identity:** `/api/users`, `/api/users/login`, `/api/users/{user_id}`, `/api/users/{user_id}/pin`.
- **File/asset mutation:** `/api/assets/register`, `/api/assets/upload`, asset publish/archive/rollback; illustration and voice uploads.
- **Editorial and publishing:** `/api/publishing/publish`, `/api/website-publisher/publish/{project_id}`, unpublish/revalidate/status/envelope; publish-readiness mark/sync/unmark.
- **Commercial control:** website-admin product pricing/visibility, website-bundle publishing, reconciliation and distribution-hub mutation.
- **Sensitive operations:** secret-control export, DB-control status/readiness, deploy-control Vercel endpoints, diagnostics, updater check/download.
- **Production/export:** ebook, audiobook, EPUB and video export; story generation, project factory and production pipeline.

This list is intentionally a risk-focused subset, not a substitute for the full manifest.

## Required manual review before auth/RBAC implementation

For every registered method/path:

1. Identify the handler, request model, response model and client callers (desktop, mobile, dashboard, updater, Website sender).
2. Trace service calls and every imported dependency/middleware check. Record whether authentication is enforced server-side and whether authorization is role/resource scoped.
3. Classify as public-approved, authenticated read, authenticated write, editor, admin, commercial/admin, secrets, or integration service.
4. Replace client-supplied `user_name`, `user_role`, PIN and identity assertions with the server-owned session identity; confirm the route never treats a role in a path/body as authority.
5. Confirm private storage is not reachable through an unauthenticated mount. Public asset delivery must be explicit, confined and approval-backed; updater downloads must be authenticated.
6. Design the migration as one compatible rollout: credential hashing, signed/expiring server sessions, RBAC, restricted CORS, route policy coverage and client transition.
7. Test 401/403, expired/revoked sessions, disabled users, cross-user/resource access, anonymous storage traversal, upload/publish/export and all legitimate client flows.

## Current conclusion

The evidence confirms a large unclassified runtime surface and the absence of global dependency enforcement in the manifest. It does **not** establish whether individual handlers have imported/service-level checks. The coordinated security migration remains P0. No authentication code, storage mount, data, credential, production configuration or infrastructure was changed by this inventory.


## Source recheck — 24 November 2026

**Main reviewed:** `ee9acd90ff62bf8f751f60d3652918a8741b13b9`  
**Scope:** static source and existing regression tests only; no HTTP exploit test, desktop/mobile run, storage probe, or runtime route-manifest regeneration.

### Fresh source evidence

- `studio_core/api/main.py` still configures CORS with wildcard origins, methods and headers while credentials are enabled. It mounts `/public` and the entire resolved storage directory at `/storage` when the directories exist.
- `studio_core/api/routes/videos.py` exposes `POST /api/videos/export/{project_id}` without a FastAPI auth dependency or server-derived principal in the handler. It loads the project by supplied ID, selects the story/locale, builds storyboard frames, invokes video generation and writes the result into the project's output JSON.
- This route is a sensitive write/production operation. The absence of a route-local dependency is not proof of every possible external check, but the inspected application wiring does not show a central auth boundary that protects it.
- `studio_core/services/video_service.py` currently makes `resolve_approved_series_audio()` fail closed (returns no audio until the server-owned approval ledger exists). The renderer accepts `series_audio_path`, ignores the legacy `audio_path` field, and returns `animatic_only`, `finalizable=false`, with `real_character_animation_pipeline_not_implemented`.
- Existing regression tests cover audiobook isolation and the fail-closed gate: `tests/test_series_adaptation_audio_isolation.py`; factory, manual pipeline and direct route tests in `tests/test_project_factory_video_sequence.py` assert an empty series-audio path and no legacy `audio_path` fallback when no approved series narration is available.

### Reconciliation

The 19 Nov counts (78 route modules / 233 heuristic handlers / 219 APIRoute entries / 6 other HTTP entries / 2 static mounts) remain **historical artifact counts**; they were not regenerated from this main commit in this run. The source-level CORS and static-mount findings above were rechecked.

Issue [#57 — series adaptation audio isolation](https://github.com/AndreVazao/baribudos-studio/issues/57) is **partially addressed by merged PR #60**: audiobook audio is no longer used as miniseries narration and false final-miniseries completion is blocked. It remains open for a separate approved series script/audio and real character animation pipeline.

### P0 decision

Do not patch this route in isolation. Authentication/RBAC, private storage and CORS must be migrated together with all handlers and React/Tauri/Capacitor clients, with deny-by-default policies, route coverage, 401/403 tests, backup and rollback. Keep Studio private/domestic and do not expose it to the Internet.

No runtime, client, data, schema, migration, credential, secret, permission, storage, production or infrastructure changes were made in this recheck.
