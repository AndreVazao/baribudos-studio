import { getApiBase, get, patch, post, put } from "./core.js"

export async function listSagaVisualSets() {
  return get(`${getApiBase()}/saga-visual-sets`)
}

export async function replaceSagaVisualSets(payload = {}) {
  return put(`${getApiBase()}/saga-visual-sets`, payload)
}

export async function updateSagaVisualSet(itemId, payload = {}) {
  return patch(`${getApiBase()}/saga-visual-sets/${encodeURIComponent(String(itemId || "").trim())}`, payload)
}

export async function exportWebsiteVisualSets() {
  return get(`${getApiBase()}/website-visual-sets/export`)
}

export async function getWebsiteVisualSetsStatus() {
  return get(`${getApiBase()}/website-visual-sets/status`)
}

export async function getWebsiteVisualSetsSummary() {
  return get(`${getApiBase()}/website-visual-sets/summary`)
}

export async function publishSagaVisualSetToWebsite(itemId) {
  return post(`${getApiBase()}/website-visual-sets/publish/${encodeURIComponent(String(itemId || "").trim())}`, {})
}

export async function publishAllSagaVisualSetsToWebsite() {
  return post(`${getApiBase()}/website-visual-sets/publish-all`, {})
}

export async function getWebsiteVisualSetReconcile() {
  return get(`${getApiBase()}/website-visual-sets-reconcile`)
}
