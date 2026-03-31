import { getApiBase, get, post } from "./core.js"

export async function getStoryTranslations(projectId) {
  return get(`${getApiBase()}/story-translation/${encodeURIComponent(String(projectId || "").trim())}`)
}

export async function generateStoryTranslations(projectId, payload = {}) {
  return post(`${getApiBase()}/story-translation/${encodeURIComponent(String(projectId || "").trim())}/generate`, payload)
}
