import { getApiBase, get, patch, post } from "./core.js"

export async function getDistributionHub(projectId) {
  return get(`${getApiBase()}/distribution-hub/${encodeURIComponent(String(projectId || "").trim())}`)
}

export async function refreshDistributionHub(projectId, user = {}) {
  const userName = String(user?.name || "")
  const userRole = String(user?.role || "")
  const base = `${getApiBase()}/distribution-hub/${encodeURIComponent(String(projectId || "").trim())}/refresh`
  const query = new URLSearchParams()
  if (userName) query.set("user_name", userName)
  if (userRole) query.set("user_role", userRole)
  return post(query.toString() ? `${base}?${query.toString()}` : base, {})
}

export async function updateDistributionHub(projectId, payload = {}, user = {}) {
  const userName = String(user?.name || "")
  const userRole = String(user?.role || "")
  const base = `${getApiBase()}/distribution-hub/${encodeURIComponent(String(projectId || "").trim())}`
  const query = new URLSearchParams()
  if (userName) query.set("user_name", userName)
  if (userRole) query.set("user_role", userRole)
  return patch(query.toString() ? `${base}?${query.toString()}` : base, payload)
}
