import { getApiBase, del, get, patch, post } from "./core.js"

export async function listCommerceGroups() {
  return get(`${getApiBase()}/commerce-groups`)
}

export async function createCommerceGroup(payload = {}) {
  return post(`${getApiBase()}/commerce-groups`, payload)
}

export async function updateCommerceGroup(groupId, payload = {}) {
  return patch(`${getApiBase()}/commerce-groups/${encodeURIComponent(String(groupId || "").trim())}`, payload)
}

export async function deleteCommerceGroup(groupId) {
  return del(`${getApiBase()}/commerce-groups/${encodeURIComponent(String(groupId || "").trim())}`)
}

export async function publishCommerceGroupToWebsite(groupId) {
  return post(`${getApiBase()}/website-bundles/publish/${encodeURIComponent(String(groupId || "").trim())}`, {})
}

export async function getWebsiteBundlesStatus(limit = 20) {
  return get(`${getApiBase()}/website-bundles/status?limit=${Math.max(1, Math.min(Number(limit || 20), 100))}`)
}
