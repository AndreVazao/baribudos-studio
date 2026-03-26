import { getApiBase, get, post, qs } from "./core.js"

export async function getWebsiteControlHealth() {
  return get(`${getApiBase()}/website-control/health`)
}

export async function getWebsiteControlSummary() {
  return get(`${getApiBase()}/website-control/summary`)
}

export async function getWebsiteControlCatalog({ limit = 25, activeOnly = false } = {}) {
  return get(`${getApiBase()}/website-control/catalog${qs({ limit, active_only: activeOnly })}`)
}

export async function getWebsiteControlPublication(publicationId) {
  return get(`${getApiBase()}/website-control/publication/${encodeURIComponent(String(publicationId || "").trim())}`)
}

export async function getWebsitePublishEnvelope(projectId) {
  return get(`${getApiBase()}/website-publisher/envelope/${projectId}`)
}

export async function getWebsitePublishStatus(projectId) {
  return get(`${getApiBase()}/website-publisher/status/${projectId}`)
}

export async function publishProjectToWebsite(projectId) {
  return post(`${getApiBase()}/website-publisher/publish/${projectId}`, {})
}
