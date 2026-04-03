import { getApiBase, get, patch, post, qs } from "./core.js"

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

export async function getWebsiteControlDivergence(publicationId, expectedChecksum = "", expectedProjectVersion = "") {
  return get(`${getApiBase()}/website-control/divergence/${encodeURIComponent(String(publicationId || "").trim())}${qs({ expected_checksum: expectedChecksum, expected_project_version: expectedProjectVersion })}`)
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

export async function unpublishProjectOnWebsite(projectId) {
  return post(`${getApiBase()}/website-publisher/unpublish/${projectId}`, {})
}

export async function revalidateProjectOnWebsite(projectId) {
  return post(`${getApiBase()}/website-publisher/revalidate/${projectId}`, {})
}

export async function getDeployControlVercelSummary() {
  return get(`${getApiBase()}/deploy-control/vercel/summary`)
}

export async function getDeployControlVercelDeployments({ limit = 10 } = {}) {
  return get(`${getApiBase()}/deploy-control/vercel/deployments${qs({ limit })}`)
}

export async function getDbControlStatus() {
  return get(`${getApiBase()}/db-control/status`)
}

export async function getDbControlReadiness() {
  return get(`${getApiBase()}/db-control/readiness`)
}

export async function updateWebsiteProductVisibility(productId, payload = {}) {
  return patch(`${getApiBase()}/website-admin/products/${encodeURIComponent(String(productId || "").trim())}/visibility`, payload)
}

export async function updateWebsiteProductPricing(productId, payload = {}) {
  return patch(`${getApiBase()}/website-admin/products/${encodeURIComponent(String(productId || "").trim())}/pricing`, payload)
}
