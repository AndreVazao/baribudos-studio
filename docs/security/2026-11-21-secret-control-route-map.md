# Studio secret-control route-family map — 21 Nov 2026

**Scope:** static source review of `main` commit `cc7067695573792690e2321dffcfe8ca2f7743f8`, with response-redaction changes checked on Draft PR #63.  
**Status:** evidence map only. No authentication, credential, storage, data or runtime changes are made here.

## 1. Runtime routes and handlers

Router prefix: `/api/secret-control`. The six handlers in `studio_core/api/routes/secret_control.py` have no visible `Depends(...)`, principal argument or route-level authorization dependency. The generated runtime manifest also reports zero global dependencies and zero route dependency edges.

| Method | Path | Handler | Operation | Secret exposure / side effect |
|---|---|---|---|---|
| GET | `/vaults` | `secret_control_vaults` | List vaults | Returns metadata, masked rows and rendered environment text |
| GET | `/vault/{vault_id}` | `secret_control_vault` | Read one vault | `reveal_values=true` asks the service to return plaintext values |
| POST | `/vaults` | `secret_control_create` | Create vault | Accepts raw `.env` text and persists parsed values |
| PATCH | `/vault/{vault_id}` | `secret_control_patch` | Update vault | Replaces raw text or caller-supplied rows |
| DELETE | `/vault/{vault_id}` | `secret_control_delete` | Delete vault | Removes the persisted JSON item |
| GET | `/export/{vault_id}` | `secret_control_export` | Export vault | Returns the complete plaintext `.env` content |

The request models are Pydantic `SecretVaultCreatePayload` and `SecretVaultPatchPayload`. There is no typed response model; handlers return service dictionaries directly.

## 2. Persistence model and storage exposure

The service stores vaults in `data/secret_vaults.json` under `APP_CONFIG.storage_root`.

The current storage configuration establishes:

- `BARIBUDOS_STORAGE_ROOT` overrides the storage root; otherwise it defaults to `<current working directory>/storage`.
- `ensure_storage_structure()` creates the root's `data`, `uploads`, `exports`, `covers`, `assets`, `voices`, `audiobooks`, `videos`, `temp` and `logs` folders.
- `secret_control_service.py` writes `data/secret_vaults.json` through the shared JSON storage helpers.
- `studio_core/api/main.py` mounts the entire resolved storage root as unauthenticated `StaticFiles` at `/storage`.

**Conditional critical exposure:** if a vault file exists, its path is under the directory mounted at `/storage`; the code therefore creates a direct static path at `/storage/data/secret_vaults.json`. The file contains plaintext `value` and `raw` fields. This is a source-level exposure path, not proof that a production file currently exists or that a live request was made. No vault file, secret value or production storage content was read during this review.

The JSON helpers use direct `Path.write_text()` after read/modify/write. They do not provide an atomic replace or inter-process lock. Concurrent vault updates can therefore race or overwrite one another; this must be considered before using this file as a durable session or credential store.

## 3. Stored data shape

A vault is an untyped JSON dictionary containing:

- `id`, `name`, `target`, `environment`, `file_name`;
- `created_at`, `updated_at`, `source_of_truth`, `notes`;
- `rows`, an array of dictionaries.

An `entry` row contains `key`, plaintext `value`, `masked_value`, `quote_style`, `has_export`, original plaintext `raw` line and `position`. Blank/comment/raw lines are retained for round-trip `.env` serialization. There is no SQL model, encryption envelope, key version, typed persistence DTO or credential rotation record in this route family.

## 4. Existing client and trust boundary

The current shared client is `client/mobile-app`, used by the mobile/Capacitor and desktop/Tauri application.

### API wrapper

`client/mobile-app/src/api/vaults.js` exposes all six operations:

- `listVaults()`
- `getVault(vaultId, { revealValues })`
- `createVault(payload)`
- `updateVault(vaultId, payload)`
- `deleteVault(vaultId)`
- `exportVault(vaultId)`

A repository-wide search found no current UI call to `getVault()`; the wrapper nevertheless exposes the explicit reveal query. `VaultPanel.jsx` currently uses list/create/delete/export.

### UI

- `VaultPanel` calls `listVaults()` in `useEffect` on mount, without first checking the current user's permission.
- `canManageVaults(user)` trusts `user.role` or a hardcoded display-name list (owner/creator/admin and names such as André/esposa/mama). This is a client-side visibility guard, not server authorization.
- Create and delete call the client-side guard.
- Export does **not** call `canManageVaults`; its button is not disabled for a non-manager.
- The backend routes do not enforce the UI's role/name rule.

### Shared API transport

`client/mobile-app/src/api/core.js` stores the user profile in `localStorage` under `baribudos_python_user`. Its `get/post/patch/delete` wrappers call `fetch` without an Authorization bearer header. The persisted profile is not a server-verified principal. A future session migration must update the shared transport and bootstrap/logout flow; changing only this panel would leave the rest of the application inconsistent.

## 5. Credential-resolution dependencies

`credential_resolver_service.py` reads the same plaintext vault file. It checks process environment variables first, then vault rows ordered by target/environment and reverse vault order, and returns the plaintext value to its caller.

Static search found these consumers:

| Service | Credential names observed | Purpose |
|---|---|---|
| `db_control_service.py` | `BARIBUDOS_WEBSITE_DATABASE_URL` (alias `DATABASE_URL`), `BARIBUDOS_SUPABASE_URL`, `BARIBUDOS_SUPABASE_SERVICE_ROLE_KEY` | Website DB/Supabase readiness |
| `deploy_control_service.py` | `BARIBUDOS_VERCEL_API_TOKEN`, `BARIBUDOS_VERCEL_TEAM_ID`, `BARIBUDOS_VERCEL_PROJECT_ID_WEBSITE` | Vercel project/deployment reads |
| `website_admin_service.py` | `BARIBUDOS_WEBSITE_BASE_URL`, `BARIBUDOS_WEBSITE_PUBLISH_API_KEY` | Website commercial/admin calls |
| `website_bundle_service.py` | `BARIBUDOS_WEBSITE_BASE_URL`, `BARIBUDOS_WEBSITE_PUBLISH_API_KEY` | Bundle publication |
| `website_control_service.py` | `BARIBUDOS_WEBSITE_BASE_URL`, `BARIBUDOS_WEBSITE_PUBLISH_API_KEY` | Website control and reconciliation |
| `website_visual_set_service.py` | `BARIBUDOS_WEBSITE_BASE_URL`, `BARIBUDOS_WEBSITE_PUBLISH_API_KEY` | Visual-set publication/reconciliation |
| `website_publisher_service.py` | `BARIBUDOS_WEBSITE_PUBLISH_URL`, `BARIBUDOS_WEBSITE_PUBLISH_API_KEY` | Frozen publication envelope delivery |

This dependency graph means the vault cannot simply be deleted or made unreadable. A migration must preserve environment-variable precedence, target/environment selection, aliases, missing-credential errors and the existing Studio→Website machine-credential boundary. It must not expose resolved values to ordinary API responses.

## 6. What PR #63 currently improves — and what it does not

The Draft PR #63 changes the default vault response so that:

- entry `value` is blanked when reveal is not explicitly requested;
- entry `raw` is reduced to a key-only line;
- comment, unparsed and unknown row `raw` fields are blanked in masked responses because arbitrary pasted text can contain credentials;
- only an explicit allowlist of non-secret vault metadata is returned; unknown persisted top-level fields are omitted;
- `rendered_env` is serialized from the same sanitized row set, not from the persisted raw rows;
- regression tests assert that entry, comment, unparsed-row and unknown top-level secret material is absent from the default response representation.

The following remain unresolved on the branch and on current `main`:

1. All six route handlers still lack server-side authentication and authorization.
2. `GET /vault/{id}?reveal_values=true` deliberately returns plaintext values.
3. `GET /export/{id}` deliberately returns the complete plaintext file.
4. The static `/storage` mount can expose the persisted plaintext JSON file if it exists.
5. `VaultPanel` uses client-provided role/name checks and leaves export unguarded.
6. The JSON credential store has no at-rest encryption, atomic update/locking or key-rotation contract.

The policy-target register dated 17 Nov proposes `owner · secrets.read/manage/export` for this family. That is a **target policy only**; the same register explicitly records 219/219 runtime routes as unclassified and `runtime_protection_verified=false`. It is not implemented authorization.

## 7. Required migration sequence — no partial runtime patch

1. Inventory every `resolve_credential()` consumer and all environment aliases; add contract tests before changing the storage backend.
2. Select an at-rest design compatible with the private household Studio and existing OS capabilities. Prefer an OS-backed key store or a versioned authenticated-encryption envelope; do not put the encryption key beside the JSON file or in the frontend.
3. Migrate existing vault values without logging or returning them; verify a backup/restore path before changing the source of truth.
4. Move private credential data outside every StaticFiles root. Replace the broad `/storage` mount only after the React/Tauri/Capacitor media migration and public-asset allowlist are ready.
5. Apply owner-only server-side permissions to list/read/reveal/create/update/delete/export. Require explicit reveal/export intent, short-lived authorization, audit actor/session/vault/action and no-store responses.
6. Update the shared client transport to use the new server-issued session; remove local profile/name/role as authorization and guard every UI action as UX only.
7. Add 401/403 tests for anonymous, expired/revoked session, disabled user, non-owner, forged role/name, and cross-vault access. Add tests for static-path denial and secret-free logs/responses.
8. Preserve machine credential resolution for Studio→Website independently from family-user permissions. Do not use Website customer sessions to authorize Studio operations.

**No authentication, RBAC, CORS, static mount, credential format, storage file, user data, production deployment or infrastructure was changed by this route-family mapping.**
