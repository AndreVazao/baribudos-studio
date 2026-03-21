const STORAGE_KEY = "baribudos_python_api"
const USER_KEY = "baribudos_python_user"

const ENV_API = import.meta.env.VITE_BARIBUDOS_API || ""
const DEFAULT_API = ENV_API || "http://localhost:8787/api"

export function normalizeApiUrl(url) {
  let value = String(url || "").trim()
  if (!value) return DEFAULT_API

  if (!/^https?:\/\//i.test(value)) {
    value = `http://${value}`
  }

  value = value.replace(/\/+$/, "")

  if (!value.endsWith("/api")) {
    value = `${value}/api`
  }

  return value
}

export function getApiBase() {
  return normalizeApiUrl(localStorage.getItem(STORAGE_KEY) || DEFAULT_API)
}

export function setApiBase(url) {
  const normalized = normalizeApiUrl(url)
  localStorage.setItem(STORAGE_KEY, normalized)
  return normalized
}

export function getSavedUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || "null")
  } catch {
    return null
  }
}

export function setSavedUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user || null))
}

export function clearSavedUser() {
  localStorage.removeItem(USER_KEY)
}

export function getApiOrigin() {
  return getApiBase().replace(/\/api$/, "")
}

export function resolveBackendFileUrl(filePath) {
  const path = String(filePath || "").trim()
  if (!path) return ""

  if (/^https?:\/\//i.test(path)) {
    return path
  }

  const marker = "/storage/"
  const normalized = path.replace(/\\/g, "/")
  const index = normalized.indexOf(marker)

  if (index >= 0) {
    return `${getApiOrigin()}${normalized.slice(index)}`
  }

  return ""
}

export const normalizeMediaUrl = resolveBackendFileUrl

export async function handle(resPromise) {
  const res = await resPromise
  let data = null

  try {
    data = await res.json()
  } catch {
    data = null
  }

  if (!res.ok) {
    throw new Error(data?.detail || data?.error || "Erro API")
  }

  return data
}

export function get(url) {
  return handle(fetch(url))
}

export function post(url, payload = {}) {
  return handle(fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export function patch(url, payload = {}) {
  return handle(fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export function del(url) {
  return handle(fetch(url, {
    method: "DELETE"
  }))
}

export function qs(params = {}) {
  const search = new URLSearchParams()

  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return
    search.set(key, String(value))
  })

  const built = search.toString()
  return built ? `?${built}` : ""
}

export async function healthCheck(customBase = "") {
  const base = customBase ? normalizeApiUrl(customBase) : getApiBase()
  return get(`${base}/health`)
}

export async function diagnostics(customBase = "") {
  const base = customBase ? normalizeApiUrl(customBase) : getApiBase()
  return get(`${base}/diagnostics`)
}

export async function listUsers() {
  return get(`${getApiBase()}/users`)
}

export async function login(name, pin) {
  return post(`${getApiBase()}/users/login`, { name, pin })
}

export async function getSettings() {
  return get(`${getApiBase()}/settings`)
}

export async function saveSettings(payload = {}) {
  return post(`${getApiBase()}/settings`, payload)
}

export async function listSagas() {
  return get(`${getApiBase()}/sagas`)
}

export async function createSaga(payload = {}) {
  return post(`${getApiBase()}/sagas`, payload)
}

export async function listSponsors() {
  return get(`${getApiBase()}/sponsors`)
}

export async function createSponsor(payload = {}) {
  return post(`${getApiBase()}/sponsors`, payload)
}

export async function listJobs() {
  return get(`${getApiBase()}/jobs`)
                     }
