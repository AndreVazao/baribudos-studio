import { del, get, patch, post, getApiBase } from "./core.js"

export async function listVaults() {
  return get(`${getApiBase()}/secret-control/vaults`)
}

export async function getVault(vaultId, { revealValues = false } = {}) {
  const suffix = revealValues ? "?reveal_values=true" : ""
  return get(`${getApiBase()}/secret-control/vault/${encodeURIComponent(String(vaultId || "").trim())}${suffix}`)
}

export async function createVault(payload = {}) {
  return post(`${getApiBase()}/secret-control/vaults`, payload)
}

export async function updateVault(vaultId, payload = {}) {
  return patch(`${getApiBase()}/secret-control/vault/${encodeURIComponent(String(vaultId || "").trim())}`, payload)
}

export async function deleteVault(vaultId) {
  return del(`${getApiBase()}/secret-control/vault/${encodeURIComponent(String(vaultId || "").trim())}`)
}

export async function exportVault(vaultId) {
  return get(`${getApiBase()}/secret-control/export/${encodeURIComponent(String(vaultId || "").trim())}`)
}
