const STORAGE_KEY = "baribudos_python_api"
const USER_KEY = "baribudos_python_user"
const ENV_API = import.meta.env.VITE_BARIBUDOS_API || ""
const DEFAULT_API = ENV_API || "http://localhost:8787/api"

function normalizeApiUrl(url) {
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

async function handle(resPromise) {
  const res = await resPromise
  const data = await res.json()

  if (!res.ok) {
    throw new Error(data?.detail || data?.error || "Erro API")
  }

  return data
}

export async function healthCheck(customBase = "") {
  const base = customBase ? normalizeApiUrl(customBase) : getApiBase()
  return handle(fetch(`${base}/health`))
}

export async function diagnostics(customBase = "") {
  const base = customBase ? normalizeApiUrl(customBase) : getApiBase()
  return handle(fetch(`${base}/diagnostics`))
}

export async function listUsers() {
  return handle(fetch(`${getApiBase()}/users`))
}

export async function login(name, pin) {
  return handle(fetch(`${getApiBase()}/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, pin })
  }))
}

export async function createUser(payload) {
  return handle(fetch(`${getApiBase()}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: payload?.name || "",
      role: payload?.role || "editor",
      pin: payload?.pin || "",
      is_active: payload?.is_active ?? true
    })
  }))
}

export async function updateUser(userId, payload) {
  return handle(fetch(`${getApiBase()}/users/${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: payload?.name,
      role: payload?.role,
      is_active: payload?.is_active
    })
  }))
}

export async function updateUserPin(userId, pin) {
  return handle(fetch(`${getApiBase()}/users/${userId}/pin`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin })
  }))
}

export async function getSettings() {
  return handle(fetch(`${getApiBase()}/settings`))
}

export async function saveSettings(payload) {
  return handle(fetch(`${getApiBase()}/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
}

export async function listSagas() {
  return handle(fetch(`${getApiBase()}/sagas`))
}

export async function createSaga(payload) {
  return handle(fetch(`${getApiBase()}/sagas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
}

export async function listSponsors() {
  return handle(fetch(`${getApiBase()}/sponsors`))
}

export async function createSponsor(payload) {
  return handle(fetch(`${getApiBase()}/sponsors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
}

export async function listProjects(user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/projects?${query}`))
}

export async function createProject(payload) {
  return handle(fetch(`${getApiBase()}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: payload?.title || "",
      saga_slug: payload?.saga_slug || "baribudos",
      saga_name: payload?.saga_name || "Baribudos",
      language: payload?.language || "pt-PT",
      output_languages: payload?.output_languages || ["pt-PT"],
      created_by: payload?.created_by || "",
      created_by_name: payload?.created_by_name || "",
      visible_to_owner_only: payload?.visible_to_owner_only ?? true
    })
  }))
}

export async function updateProject(projectId, payload, user) {
  const query = new URLSearchParams({
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/projects/${projectId}?${query}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
}

export async function listJobs() {
  return handle(fetch(`${getApiBase()}/jobs`))
}

export async function createJob(payload) {
  return handle(fetch(`${getApiBase()}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
}

export async function getFactoryCapabilities() {
  return handle(fetch(`${getApiBase()}/factory/capabilities`))
}

export async function runFactory(projectId, payload) {
  return handle(fetch(`${getApiBase()}/factory/run/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
}

export async function listPublications() {
  return handle(fetch(`${getApiBase()}/publishing`))
}

export async function publishProject(payload) {
  return handle(fetch(`${getApiBase()}/publishing/publish`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
}

export async function exportEbook(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/ebooks/export/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function exportAudiobook(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/audiobooks/export/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function exportVideo(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/videos/export/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function listIps(user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/ip-creator?${query}`))
}

export async function createIp(payload) {
  return handle(fetch(`${getApiBase()}/ip-creator`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
}

export async function getIpBySlug(slug, user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/ip-creator/${slug}?${query}`))
}

export async function getIpPermissions(slug, user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/ip-creator/${slug}/permissions?${query}`))
}

export async function getIpPalette(slug, user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/ip-palette/${slug}?${query}`))
}

export async function updateIpPalette(slug, palette, user) {
  return handle(fetch(`${getApiBase()}/ip-palette/${slug}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      palette,
      user_id: user?.id || "",
      user_name: user?.name || "",
      user_role: user?.role || ""
    })
  }))
      }
