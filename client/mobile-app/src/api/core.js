import { readStoredSessionToken, removeStoredSessionToken, writeStoredSessionToken } from "./native-session-storage.js"

const STORAGE_KEY = "baribudos_python_api"
const LEGACY_USER_KEY = "baribudos_python_user"

const ENV_API = import.meta.env?.VITE_BARIBUDOS_API || ""
const DEFAULT_API = ENV_API || "http://localhost:8787/api"

let authToken = ""
let savedUser = null

export function normalizeApiUrl(url) {
  let value = String(url || "").trim()
  if (!value) return DEFAULT_API
  if (!/^https?:\/\//i.test(value)) value = `http://${value}`
  value = value.replace(/\/+$/, "")
  if (!value.endsWith("/api")) value = `${value}/api`
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

export function getAuthToken() {
  return authToken
}

export function hasAuthToken() {
  return Boolean(authToken)
}

export function setAuthToken(token) {
  authToken = typeof token === "string" ? token.trim() : ""
  return Boolean(authToken)
}

export function clearAuthToken() {
  authToken = ""
}

export function getSavedUser() {
  return savedUser
}

export function setSavedUser(user) {
  savedUser = user && typeof user === "object" ? user : null
}

export function clearSavedUser() {
  savedUser = null
  try {
    localStorage.removeItem(LEGACY_USER_KEY)
  } catch {
    // Storage may be unavailable in a restricted webview.
  }
}

export function clearAuthSession() {
  clearAuthToken()
  clearSavedUser()
  void removeStoredSessionToken().catch(() => {})
}

export async function clearStoredAuthSession() {
  clearAuthToken()
  clearSavedUser()
  await removeStoredSessionToken()
}

export async function persistAuthToken(token) {
  const normalized = typeof token === "string" ? token.trim() : ""
  if (!normalized) throw new Error("Token de sessão inválido.")
  await writeStoredSessionToken(normalized)
  setAuthToken(normalized)
}

export async function restoreAuthToken() {
  const token = await readStoredSessionToken()
  if (!token) return false
  setAuthToken(token)
  return true
}

export function getApiOrigin() {
  return getApiBase().replace(/\/api$/, "")
}

export function resolveBackendFileUrl(filePath) {
  const path = String(filePath || "").trim()
  if (!path) return ""
  if (/^https?:\/\//i.test(path)) return path
  const marker = "/storage/"
  const normalized = path.replace(/\\/g, "/")
  const index = normalized.indexOf(marker)
  if (index >= 0) return `${getApiOrigin()}${normalized.slice(index)}`
  return ""
}

export const normalizeMediaUrl = resolveBackendFileUrl

function withAuthHeaders(options = {}) {
  const headers = new Headers(options.headers || {})
  if (authToken) headers.set("Authorization", `Bearer ${authToken}`)
  return { ...options, headers }
}

export async function handle(resPromise) {
  const res = await resPromise
  let data = null
  try {
    data = await res.json()
  } catch {
    data = null
  }
  if (!res.ok) {
    if (res.status === 401) {
      clearAuthSession()
      window.dispatchEvent(new CustomEvent("baribudos:auth-expired"))
    }
    throw new Error(data?.detail || data?.error || "Erro API")
  }
  return data
}

export function apiFetch(url, options = {}) {
  return fetch(url, withAuthHeaders(options))
}

export function get(url) {
  return handle(apiFetch(url))
}

export function post(url, payload = {}) {
  return handle(apiFetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export function put(url, payload = {}) {
  return handle(apiFetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export function patch(url, payload = {}) {
  return handle(apiFetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export function del(url) {
  return handle(apiFetch(url, { method: "DELETE" }))
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

export async function getCurrentUser() {
  const result = await get(`${getApiBase()}/users/me`)
  return result?.user || null
}

export async function logoutSession() {
  if (!authToken) {
    clearAuthSession()
    return
  }
  try {
    await post(`${getApiBase()}/users/logout`)
  } finally {
    await clearStoredAuthSession()
  }
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
