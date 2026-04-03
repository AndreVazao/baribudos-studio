import { getApiBase, get, post } from "./core.js"

export async function getStorySource(projectId) {
  return get(`${getApiBase()}/story-source/${encodeURIComponent(String(projectId || "").trim())}`)
}

export async function saveStorySource(projectId, payload = {}) {
  return post(`${getApiBase()}/story-source/${encodeURIComponent(String(projectId || "").trim())}`, payload)
}

export async function lockStorySource(projectId, approved = false) {
  const suffix = approved ? "?approved=true" : ""
  return post(`${getApiBase()}/story-source/${encodeURIComponent(String(projectId || "").trim())}/lock${suffix}`, {})
}

export async function getStorySourceGate(projectId) {
  return get(`${getApiBase()}/story-source/${encodeURIComponent(String(projectId || "").trim())}/gate`)
}
