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

async function handle(resPromise) {
  const res = await resPromise
  const data = await res.json()

  if (!res.ok) {
    throw new Error(data?.detail || data?.error || "Erro API")
  }

  return data
}

function get(url) {
  return handle(fetch(url))
}

function post(url, payload = {}) {
  return handle(fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function healthCheck() {
  return get(`${getApiBase()}/health`)
}

export async function diagnostics() {
  return get(`${getApiBase()}/diagnostics`)
    }

export async function listProjects() {
  return get(`${getApiBase()}/projects`)
}

export async function createProject(payload) {
  return post(`${getApiBase()}/projects`, payload)
}

export async function getFactoryCapabilities() {
  return get(`${getApiBase()}/factory/capabilities`)
}

export async function runFactory(projectId, payload) {
  return post(`${getApiBase()}/factory/run/${projectId}`, payload)
}

export async function exportEbook(projectId, payload = {}) {
  return post(`${getApiBase()}/ebooks/export/${projectId}`, payload)
}

export async function exportAudiobook(projectId, payload = {}) {
  return post(`${getApiBase()}/audiobooks/export/${projectId}`, payload)
}

export async function exportVideo(projectId, payload = {}) {
  return post(`${getApiBase()}/videos/export/${projectId}`, payload)
}

export async function getStoryLayout(projectId) {
  return get(`${getApiBase()}/story-layout/${projectId}`)
}

export async function paginateStoryLayout(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/paginate/${projectId}`, payload)
}

export async function updateStoryLayoutPage(projectId, pageId, payload = {}) {
  return post(`${getApiBase()}/story-layout/page/${projectId}/${pageId}`, payload)
  }

export async function listVoiceSamples() {
  return get(`${getApiBase()}/voice-library/samples`)
}

export async function getAudioCast(projectId) {
  return get(`${getApiBase()}/audio-cast/${projectId}`)
}

export async function saveAudioCast(projectId, payload = {}) {
  return post(`${getApiBase()}/audio-cast/${projectId}`, payload)
}

export async function previewAudioCast(projectId, payload = {}) {
  return post(`${getApiBase()}/audio-cast-preview/${projectId}`, payload)
}

export async function listIllustrationRuns() {
  return get(`${getApiBase()}/illustration-pipeline`)
}

export async function getIllustrationPipeline(projectId) {
  return get(`${getApiBase()}/illustration-pipeline/${projectId}`)
}

export async function setupIllustrationPipeline(projectId, payload = {}) {
  return post(`${getApiBase()}/illustration-pipeline/setup/${projectId}`, payload)
}

export async function updateIllustrationFrame(projectId, frameId, payload = {}) {
  return post(`${getApiBase()}/illustration-pipeline/${projectId}/frame/${frameId}`, payload)
}

export async function queueIllustrationGeneration(projectId, payload = {}) {
  return post(`${getApiBase()}/illustration-generation/queue/${projectId}`, payload)
}

export async function runIllustrationProvider(projectId, payload = {}) {
  return post(`${getApiBase()}/illustration-provider/run/${projectId}`, payload)
  }

