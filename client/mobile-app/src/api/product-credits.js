import { getApiBase, get, patch, post } from "./core.js"

export async function getProductCredits(projectId) {
  return get(`${getApiBase()}/product-credits/${encodeURIComponent(String(projectId || "").trim())}`)
}

export async function rebuildProductCredits(projectId) {
  return post(`${getApiBase()}/product-credits/${encodeURIComponent(String(projectId || "").trim())}/rebuild`, {})
}

export async function updateProductCredits(projectId, payload = {}) {
  return patch(`${getApiBase()}/product-credits/${encodeURIComponent(String(projectId || "").trim())}`, payload)
}
