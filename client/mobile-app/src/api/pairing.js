import { get, getApiBase, post } from "./core.js"

export async function listPairings() {
  return get(`${getApiBase()}/pairing`)
}

export async function createPairing(payload = {}) {
  return post(`${getApiBase()}/pairing/create`, payload)
}

export async function resolvePairingCode(pairCode) {
  return get(`${getApiBase()}/pairing/resolve/${encodeURIComponent(String(pairCode || "").trim())}`)
}

export async function revokePairing(pairCode) {
  return post(`${getApiBase()}/pairing/revoke/${encodeURIComponent(String(pairCode || "").trim())}`)
}
