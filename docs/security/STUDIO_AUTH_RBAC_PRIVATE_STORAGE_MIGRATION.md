# Studio authentication, authorization and private-storage migration

**Status:** implementation specification; no runtime security change is made by this document.  
**Date:** 2026-11-18  
**Scope:** `AndreVazao/baribudos-studio` API, desktop and mobile clients.

## Security decision

The Studio is a private household/editorial system. Authentication and authorization must be enforced by the server for every request. A client-supplied name, role, user ID, project owner, or UI state is data, never proof of identity or permission.

The current default branch is not safe to expose as a network service. The findings below are source-level observations, not evidence of a successful exploit against a running installation.

## Confirmed source findings on main

| Area | Evidence | Consequence |
|---|---|---|
| Application middleware | `studio_core/api/main.py` installs CORS with wildcard origins, credentials, methods and headers; no global authentication dependency/middleware is registered there | Cross-origin policy is overbroad and route protection is not centrally enforced |
| Static storage | `main.py` mounts the resolved storage root at `/storage` whenever it exists | Private JSON and operational files may become static HTTP resources |
| User records | `studio_core/api/routes/users.py` creates the default owner with PIN `1234`; `User` in `core/models.py` contains a plaintext `pin` field | Predictable bootstrap credential and plaintext credential persistence |
| User API | `users.py` exposes list/create/update/PIN-update/login handlers without visible authorization dependencies; list and mutation responses return stored user records | No demonstrated server-side owner boundary; credential material may be returned |
| Project API | `projects.py` accepts caller-provided identity fields on create/list and caller-provided role/name on update | Authorization can be forged by a caller |
| Updater | `routes/updater.py` exposes check/download handlers without visible authorization dependencies; service-level URL/path risks are tracked in Studio issue #43 | Privileged update operations need owner-only authorization and strict input confinement |

The runtime inventory previously recorded 219 APIRoute entries, zero global dependencies and zero duplicate route entries. All 219 were still unclassified in the inventory snapshot. Re-run that inventory against the implementation branch before any route is opened.

## Target architecture

### 1. Identity and sessions

- Persist password/PIN verifiers only; never persist or return plaintext credentials.
- Use a maintained password-hashing implementation with an explicit work factor (prefer Argon2id where the supported runtime/dependency set permits it). Do not invent a home-grown hash.
- Replace predictable default-owner credentials with a one-time bootstrap flow. Bootstrap secret must be generated outside source control, short-lived, single-use, and never logged.
- Require the owner to set a strong individual credential before normal Studio use. Do not retain `1234` as a fallback.
- Login returns a short-lived opaque session token; persist only a cryptographic hash of the token server-side.
- Sessions carry user ID, creation/expiry, revocation state and credential/session version. Check active-user state and revocation on every authenticated request.
- Support logout, owner-triggered session revocation, password reset with forced credential change, and credential rotation.
- Rate-limit login and bootstrap attempts; apply bounded lockout/backoff without enabling trivial permanent denial of service.
- Never return credential hashes, bootstrap secrets, session hashes or internal security metadata from user APIs.

### 2. Client transport and storage

- Browser UI: prefer an HttpOnly, Secure, SameSite cookie with explicit CSRF protection for state-changing requests.
- Tauri and Capacitor: use platform secure credential storage; do not store the full user object or bearer token in ordinary localStorage.
- Keep a minimal, non-authoritative display profile in UI memory. The server remains authoritative.
- Migrate React, Tauri and Capacitor together. Do not ship a server change that strands an older supported client without a documented compatibility/upgrade path.
- Do not add paid services or assume a particular keychain plugin is already installed. Select and test supported platform storage before client implementation.

### 3. Server-side authorization

- Add one central authentication dependency and a deny-by-default route policy.
- Route policy must classify every route as one of: public-read, public-ingest-with-machine-auth, authenticated-user, editor, owner, or disabled/internal.
- Public routes must be explicitly allowlisted (initially only minimal health/readiness and deliberately public, non-sensitive assets). Login/bootstrap are narrowly scoped unauthenticated entry points, not general public routes.
- Every non-public route must resolve the principal from a verified session, then authorize action + resource + IP/project scope on the server.
- Ignore/remove client-provided `user_role`, `user_name`, `user_id`, `created_by` and similar fields as authorization authority. Populate creator/audit fields from the authenticated principal.
- Child role is limited to approved guided activities (e.g. assigned voice recording/dictation). It cannot administer accounts, change permissions, publish, price, configure integrations, or delete content.
- Enforce owner-only access for users, secret control, DB control, deployment control, updater, settings with secrets, and security-sensitive diagnostics.
- Machine-to-machine Studio→Website publication must retain a separate scoped credential, constant-time verification, rotation/revocation and endpoint-specific authorization. A machine credential is not a human session.
- Return 401 for absent/invalid/expired/revoked sessions and 403 for authenticated but unauthorized actions. Avoid leaking resource existence across scopes.

### 4. Private and public files

- Remove the root `/storage` StaticFiles mount. No private data directory, user record, settings, project JSON, voice record, export, update package or unpublished media may be reachable through static serving.
- Replace broad filesystem exposure with authenticated file-delivery endpoints that resolve a logical asset ID, enforce resource permissions, verify path containment and stream only the requested file.
- Maintain a separate explicit public-asset allowlist. Public serving must not infer permission merely from a file being under a directory named `public`.
- Resolve symlinks and canonical paths before access; reject traversal, absolute-path escape and symlink escape.
- Preserve existing internal asset URLs through a controlled migration/compatibility layer; do not silently break desktop/mobile media, EPUB, audiobook, video, voice preview or updater consumers.
- Test with isolated temporary fixtures only. Never probe production user files or download private production data for validation.

### 5. Updater hardening

- Require an authenticated owner session.
- Accept only a server-configured, trusted update manifest/source. Never fetch arbitrary request-supplied URLs.
- Validate artifact name as a basename and enforce resolved-path containment under the dedicated downloads directory.
- Restrict redirects and destination hosts; reject loopback, private, link-local and metadata-service destinations.
- Download to a temporary file, verify a trusted checksum/signature, then atomically publish the artifact.
- Do not expose raw internal exception details to callers.

## Route inventory and rollout gates

Before enforcing policy, regenerate the route inventory from the fully constructed FastAPI app (including mounts), record method/path/name/module and classify every entry. Unknown or newly added routes must fail closed in CI. The inventory must distinguish ordinary API routes from static mounts and machine-to-machine endpoints.

Roll out in small, coordinated increments:

1. **Inventory-only:** generate and review the complete route manifest; no behavior change.
2. **Identity foundation:** credential verifier, one-time owner bootstrap, session issue/verify/revoke, unit tests.
3. **Client migration:** browser, Tauri and Capacitor session lifecycle and secure storage; compatibility tests.
4. **Central policy:** explicit route classifications and server-side principal/permission checks; remove spoofable identity authority.
5. **Storage boundary:** remove root static mount and migrate every known asset consumer to scoped delivery.
6. **Updater boundary:** owner-only, trusted manifest, path/host validation and artifact integrity.
7. **Enforcement:** deny-by-default CI gate, negative HTTP tests, migration/rollback rehearsal, then controlled release.

Do not combine all seven phases into one high-risk deployment. Each phase needs a small PR, green CI and a clear rollback strategy. The existing Draft PR #60 is a separate editorial/media guardrail and must remain Draft until its own explicit restriction is lifted; do not merge it as part of this security work.

## Mandatory automated tests

- Anonymous access to every protected route is denied.
- Valid session succeeds for permitted role/resource.
- Expired, revoked, tampered and unknown session is denied.
- Deactivated user loses access immediately.
- Child cannot call owner/editor operations even when UI controls are bypassed.
- Forged role/name/user ID/creator fields never elevate permissions or change audit identity.
- Cross-project and cross-IP access is denied unless explicitly granted.
- User list/create/update/reset responses never contain plaintext credentials, hashes or session secrets.
- Bootstrap secret is single-use, expires, is not logged and cannot be reused.
- CORS rejects unapproved origins and does not combine wildcard origins with credentials.
- `/storage/data/users.json`, settings, projects and unpublished assets are not served statically.
- Authenticated file delivery rejects traversal, absolute paths and symlink escapes; public delivery serves only allowlisted assets.
- Updater rejects arbitrary URLs, private/local destinations, unsafe redirects, traversal filenames and invalid checksums/signatures.
- Existing desktop/mobile asset and session flows pass end-to-end tests after migration.
- Route-manifest test fails when a new route is unclassified or a protected route is accidentally made public.

## Operational boundaries

This specification does not authorize changes to production data, schemas, credentials, secrets, Supabase, Vercel, storage providers, deployments or paid services. No live production data should be used in security tests. Implementation must first pass isolated tests and CI; production rollout requires its own explicit approval.


## CI route-inventory evidence (2026-11-18)

The Studio CI run for this branch completed successfully (run 618, commit `41dd59ea3ca0766a5a747a4638cab2ac008e72b6`). Its uploaded route-authorization artifact was inspected after the run.

Runtime manifest snapshot:
- **219** registered FastAPI method/path entries: 100 GET, 97 POST, 19 PATCH, 2 DELETE and 1 PUT.
- **219/219** entries remain `UNCLASSIFIED`; none has a reviewed route policy.
- **6** additional non-APIRoute HTTP entries: `/docs`, `/docs/oauth2-redirect`, `/openapi.json`, `/redoc`, and two static mounts.
- **2** StaticFiles mounts: `/public` and `/storage`. Both were detected with an isolated CI storage root; the exporter explicitly records `authorization_verified: false`. This confirms the mount registration in the tested CI app, not access to any production file.
- **0** global FastAPI dependencies.
- One registered CORS middleware with `allow_origins=["*"]`, `allow_credentials=true`, `allow_methods=["*"]` and `allow_headers=["*"]`.

The separate heuristic scanner reports 233 handler candidates across 78 route modules, including 97 handlers flagged as sensitive/operational and 29 referencing client identity fields. These 233 static handler candidates and the 219 runtime method/path entries are different measurements; do not treat them as a one-to-one discrepancy or infer that the remaining 14 handlers are missing routes without reconciling their source locations.

Immediate review priorities from the runtime manifest include:
- `/api/users` and `/api/users/{user_id}` credential/account operations;
- `/api/secret-control/*`, `/api/settings`, `/api/db-control/*`, `/api/deploy-control/*`, `/api/updater/*` and `/api/diagnostics`;
- publication, readiness and website-publisher mutation routes;
- voice library/profile upload and mutation routes;
- static `/storage` removal and a separate content review of `/public`.

The manifest artifact is an inventory snapshot from CI, not a live production probe and not proof that any route was successfully exploited. Keep all route policies denied/unclassified until each is reviewed against its service and storage effects and covered by HTTP tests.

## Prioritized route review from the CI evidence artifact (2026-11-18)

The downloadable `studio-route-authorization-evidence` artifact from Studio CI run **616** (GitHub run ID `44312969350`, commit `420ab2e9630e4386f8d7ddbb98794888935360b1`, PR #60 head) was inspected. Both CI jobs completed successfully. The artifact contains:
- `studio-fastapi-route-manifest.json/.md`: 219 runtime method/path entries plus six non-APIRoute HTTP entries.
- `studio-route-inventory.json/.md`: 233 source-level handler candidates across 78 modules.

The following endpoints are prioritized for policy review. **They remain UNCLASSIFIED**; the group labels below are review targets, not implemented permissions or proof of current runtime denial.

### P0 — owner-only review target
- `GET /api/users`
- `POST /api/users`
- `PATCH /api/users/{user_id}`
- `PATCH /api/users/{user_id}/pin`
- `GET /api/secret-control/vaults`
- `POST /api/secret-control/vaults`
- `GET /api/secret-control/vault/{vault_id}`
- `PATCH /api/secret-control/vault/{vault_id}`
- `DELETE /api/secret-control/vault/{vault_id}`
- `GET /api/secret-control/export/{vault_id}`
- `GET /api/db-control/readiness`
- `GET /api/db-control/status`
- `GET /api/deploy-control/vercel/deployments`
- `GET /api/deploy-control/vercel/summary`
- `GET /api/settings`
- `POST /api/settings`
- `POST /api/updater/check`
- `POST /api/updater/download`

### P1 — editor/owner or scoped machine identity review target
- `POST /api/assets/{asset_id}/publish`
- `GET /api/publish-readiness/{project_id}`
- `POST /api/publish-readiness/{project_id}/mark-ready`
- `POST /api/publish-readiness/{project_id}/sync`
- `POST /api/publish-readiness/{project_id}/unmark-ready`
- `GET /api/publishing`
- `POST /api/publishing/publish`
- `POST /api/website-publisher/publish/{project_id}`
- `POST /api/website-publisher/revalidate/{project_id}`
- `POST /api/website-publisher/unpublish/{project_id}`
- `POST /api/website-bundles/publish/{group_id}`
- `POST /api/website-visual-sets/publish-all`
- `POST /api/website-visual-sets/publish/{item_id}`
- `PATCH /api/website-admin/products/{product_id}/pricing`
- `PATCH /api/website-admin/products/{product_id}/visibility`

### P1 — private voice/media review target
- `GET /api/voice-library`
- `POST /api/voice-library/upload`
- `GET /api/voice-library/{voice_id}`
- `POST /api/voice-preview`
- `GET /api/voice-profiles`
- `POST /api/voice-profiles`
- `PATCH /api/voice-profiles/{voice_profile_id}`
- `GET /api/voice-profiles/{voice_profile_id}/validate`

### Non-APIRoute HTTP surface
- `/storage`: remove the broad StaticFiles mount; replace only after authenticated asset delivery and client-consumer migration are tested.
- `/public`: retain only after an explicit file-level public allowlist review.
- `/docs`, `/docs/oauth2-redirect`, `/openapi.json`, `/redoc`: disable outside controlled development or put behind owner/developer authorization; do not assume they are harmless metadata.

### Evidence and CI correction

The artifact inspected above belongs to Studio CI **run number 616** (run ID `44312969350`) and both `frontend-build` and `backend-validate` succeeded. The earlier conversational reference to **CI #619** is not substantiated by the run evidence retrieved in this check; do not report #619 as passed or pending without retrieving its exact run record. This is an evidence correction, not a code or runtime change.

The 233 source-level candidates are heuristic and not a route authorization map. The 219 runtime entries are the definitive route enumeration for that tested app construction. Reconcile handlers to runtime endpoints before authoring any allowlist. No route policy is implemented by this annex.
