import { getApiBase, get, patch, post } from "./core.js"

export async function getDistributionHub(projectId) {
  return get(`${getApiBase()}/distribution-hub/${encodeURIComponent(String(projectId || "").trim())}`)
}

export async function refreshDistributionHub(projectId) {
  const base = `${getApiBase()}/distribution-hub/${encodeURIComponent(String(projectId || "").trim())}/refresh`
  return post(base, {})
}

export async function updateDistributionHub(projectId, payload = {}) {
  const base = `${getApiBase()}/distribution-hub/${encodeURIComponent(String(projectId || "").trim())}`
  return patch(base, payload)
}
