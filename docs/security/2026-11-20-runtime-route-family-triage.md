# Studio runtime route-family triage — 2026-11-20

**Status:** triage aid only. No route is authorized or opened by this document.  
**Source:** Studio CI run [#44740941984](https://github.com/AndreVazao/baribudos-studio/actions/runs/44740941984), PR head `d940d6215d174dbe0b57f4e481fe38e8603725b0`.  
**Artifact:** `studio-route-authorization-evidence`, artifact ID `14630691485`, SHA-256 `b6b5d097db5e127bdbaf84d9b34d9ef545b976fffdf8bedceb54b3ec45a1e5be`.

## Verified runtime inventory

The CI artifact was downloaded and inspected on 2026-11-20.

| Measurement | Result |
|---|---:|
| Registered FastAPI method/path entries | 219 |
| GET / POST / PATCH / DELETE / PUT | 100 / 97 / 19 / 2 / 1 |
| Additional non-APIRoute HTTP entries | 6 |
| StaticFiles mounts | 2 |
| Direct dependency edges in route manifest | 0 |
| Global FastAPI dependencies | 0 |
| Duplicate method/path IDs | 0 |
| Routes with reviewed authorization policy | 0 |
| Routes still marked UNCLASSIFIED | 219 |

The six additional HTTP entries are `/docs`, `/docs/oauth2-redirect`, `/openapi.json`, `/redoc`, and the `/public` and `/storage` mounts. Both StaticFiles mounts were registered in the isolated CI app with `authorization_verified: false`; the artifact deliberately omits filesystem paths and does not inspect production files.

The app registers one CORS middleware with wildcard origins, credentials, methods and headers. This is a configuration finding from the imported CI app, not a live browser exploit test.

## Candidate triage groups — not authorization decisions

The following counts group runtime entries by their route-module names to order manual review. They do **not** establish that every handler in a group needs the same role, nor do they prove its transitive service/data effects.

| Review order | Candidate family | Routes | Initial review focus |
|---|---|---:|---|
| P0 first | Identity, secrets, system control, updater, publication, assets/storage, persistent memory and Website control | 53 | Owner boundary, credential leakage, machine-vs-human principal, filesystem access, destructive side effects and cross-project/IP scope |
| P1 next | Projects, IP/canon, editorial, translation, story layout, media, audio/voice, generation, saga, production pipeline and distribution | 133 | Authenticated editor/creator permissions, immutable versioning, resource ownership, child supervision, consent and asset rights |
| P2 after | Health/readiness, smoke checks, storefront, branding, contract/reconciliation and sponsorship/reporting surfaces | 33 | Keep private by default; expose only minimal health data locally; verify no private project, commercial or memory data leaks |

P0 module counts:
- `users` 5; `secret_control` 6; `db_control` 2; `deploy_control` 2; `settings` 2; `updater` 3; `diagnostics` 1.
- `website_admin` 2; `publishing` 2; `website_publisher` 5; `assets` 7; `persistent_memory` 10; `website_control` 6.

P1 includes 133 candidate routes across 46 modules, including `projects` (3), `ip_creator` (9), `story_source` (4), `story_layout` (9), `editorial_engine` (5), `illustration_generation` (5), `voice_profiles` (4), `production_pipeline` (2) and the other project-scoped creative/media families.

P2 includes 33 candidate routes across 15 modules, including `health` (1), readiness/smoke, storefront (4), Website contract/reconciliation, bundles/visual sets, sponsorship scopes and sponsor views.

## Mandatory boundary

- **No Studio API is public merely because it is GET or has a storefront/health name.** The Studio remains a private household application and must not be exposed directly to the Internet.
- All 219 API routes remain `UNCLASSIFIED` in the generated manifest. Treat them as denied until a route-specific server-side policy is reviewed and implemented.
- `/storage` is private by default. Do not remove or replace it piecemeal until React, Tauri/desktop and Capacitor/mobile consumers have a coordinated asset migration and rollback plan.
- `/public` requires a separate allowlist and content review; directory naming alone is not authorization.
- `/docs`, `/redoc` and `/openapi.json` are part of the HTTP surface and need an explicit local/private policy.
- Website customer JWTs/cookies must never be accepted by Studio. Studio family sessions and Studio→Website machine credentials remain distinct.

## Required manual evidence for each route

Before assigning a final policy, record:

1. Exact method/path and handler module/function from the current runtime manifest.
2. Transitive service calls, database reads/writes, file access and external side effects.
3. Trusted principal source (verified server session or narrowly scoped machine credential); never client-supplied identity/role.
4. Required action permission and resource/IP/project scope.
5. Public/private classification with a written reason. Default is private/deny.
6. Negative HTTP tests for anonymous, expired/revoked session, disabled user, insufficient role, forged identity/role and cross-project access.
7. Desktop/mobile compatibility and rollback evidence where a route or asset contract changes.


## Source-handler trace — verified examples on main (20-21 Nov)

This is static source evidence, not a live HTTP exploit or middleware bypass test. The route handlers below have no visible route-level dependencies in the inspected modules; the generated CI inventory also reports zero global dependencies.

### `users` (5 routes; P0 identity)

- `GET /users`: returns records from `data/users.json` after default-owner bootstrap.
- `POST /users`: caller-supplied name, role, PIN and active flag are written to the user store.
- `PATCH /users/{user_id}`: updates name, role and active flag; no authenticated principal is visible in this handler.
- `PATCH /users/{user_id}/pin`: writes caller-supplied PIN directly.
- `POST /users/login`: compares plaintext PIN and returns the complete matching user record.
- Bootstrap creates owner with temporary PIN `1234` when the user store is empty.

**Policy:** private/deny until server-authenticated family session; owner-only lifecycle and reset; hash credentials; response DTO must exclude credential material; bootstrap/reset must force PIN replacement. Add negative tests for anonymous, forged role, inactive user, owner/non-owner and revoked session.

### `projects` (3 routes; project ownership/editorial)

- `GET /projects` accepts `user_id`, `user_name`, and `user_role` as query parameters; visibility logic uses the supplied user ID/name.
- `POST /projects` accepts `created_by` and `created_by_name` in the create payload.
- `PATCH /projects/{project_id}` accepts user name/role query parameters and checks editorial permission from those values; helper includes hardcoded trusted names.

**Policy:** all identities and roles must derive from a server-verified principal. Resource ownership must be evaluated against canonical IDs, never caller-supplied display names. Test forged owner/admin, cross-project access, inactive/revoked session, and children attempting editorial operations.

### `publishing` (2 routes; publication authority)

- `GET /publishing` reads and returns publication records.
- `POST /publishing/publish` accepts user name/role and requested-by values from request/query context; it invokes package publication and writes publication/project state.

**Policy:** private owner/editor action, with explicit per-project approval and publication readiness. Caller identity must not be accepted as authority. Test unauthenticated and forged role/name, unapproved projects, replay, integrity failures and publication side-effect rollback.

### `website-publisher` (5 routes; machine boundary)

The inspected route module delegates envelope, publish, unpublish, revalidate and status to service functions without visible authentication dependencies. This is not proof the transitive service layer is unauthenticated; inspect each service's credential validation, network target, filesystem and website side effects before final policy.

**Policy:** private owner action for humans plus a separate scoped machine credential for Studio→Website. Never accept Website customer sessions as Studio authority. Require replay/idempotency and audit logs for publication operations.

### Evidence boundary

These findings are scoped to the source files inspected on `main` and are not a complete endpoint matrix. Keep the other P0 families unclassified until each handler and service chain has been traced. No runtime code, credentials, storage, data, schema or deployment was changed by this follow-up.

## Next implementation sequence

1. Finish P0 route-to-service tracing, starting with `users`, `secret_control`, `db_control`, `deploy_control`, `updater`, `publishing`, `website_publisher` and `/storage`.
2. Reconcile the 219 runtime entries with the separate 233 static handler candidates; do not assume a one-to-one relationship.
3. Build the owner-managed family session foundation and coordinated React/Tauri/Capacitor migration plan.
4. Add a route-policy manifest test that fails on unknown/new routes; only then implement the central deny-by-default gate.
5. Validate all behavior in isolated CI and rehearse rollback before any production or household-data change.

This triage document changes no runtime behavior, credentials, CORS, storage, data, schema, migration, infrastructure or deployment. It does not prove that authorization has been implemented.


## Clarification: target policy register versus runtime enforcement — 21 Nov 2026

The earlier `docs/security/2026-11-17-runtime-route-policy-register.md` contains a **proposed tag-level policy** (for example, `secret-control → owner · secrets.read/manage/export`). Its own evidence section states that 219/219 runtime routes remain UNCLASSIFIED, with zero global dependencies and `runtime_protection_verified=false`. The table is a target design, not an implemented dependency or proof of authorization. This triage therefore continues to treat all 219 runtime routes as unprotected until each handler/service chain has a verified server-side policy and negative HTTP tests.

A focused source map for the six `secret-control` routes, shared mobile/Tauri/Capacitor client, plaintext JSON persistence, static `/storage` mount and seven `resolve_credential()` consumer modules is in [2026-11-21-secret-control-route-map.md](2026-11-21-secret-control-route-map.md). It records a conditional static exposure path for `storage/data/secret_vaults.json` if a vault file exists; no production file or secret value was read.
