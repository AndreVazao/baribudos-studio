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

function patch(url, payload = {}) {
  return handle(fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

function del(url) {
  return handle(fetch(url, {
    method: "DELETE"
  }))
}

function qs(params = {}) {
  const search = new URLSearchParams()

  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return
    search.set(key, String(value))
  })

  const built = search.toString()
  return built ? `?${built}` : ""
}

function getApiOrigin() {
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

export async function healthCheck() {
  return get(`${getApiBase()}/health`)
}

export async function diagnostics() {
  return get(`${getApiBase()}/diagnostics`)
}

export async function listUsers() {
  return get(`${getApiBase()}/users`)
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

export async function listProjects(user = {}) {
  return get(`${getApiBase()}/projects${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function createProject(payload = {}) {
  return post(`${getApiBase()}/projects`, payload)
}

export async function listJobs() {
  return get(`${getApiBase()}/jobs`)
}

export async function listPublications() {
  return get(`${getApiBase()}/publishing`)
}

export async function getFactoryCapabilities() {
  return get(`${getApiBase()}/factory/capabilities`)
}

export async function runFactory(projectId, payload = {}) {
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

export async function listIps(user = {}) {
  return get(`${getApiBase()}/ip-creator${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
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

export async function createStoryLayoutPage(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/page/${projectId}`, payload)
}

export async function deleteStoryLayoutPage(projectId, pageId) {
  return del(`${getApiBase()}/story-layout/page/${projectId}/${pageId}`)
}

export async function applyStoryLayout(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/apply/${projectId}`, payload)
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

export async function listVoiceSamples() {
  return get(`${getApiBase()}/voice-library/samples`)
}

export async function getIllustrationPipeline(projectId) {
  return get(`${getApiBase()}/illustration-pipeline/${projectId}`)
}

export async function getIllustrationPromptPackage(projectId) {
  return get(`${getApiBase()}/illustration-generation/package/${projectId}`)
}

export async function getStoryboardManifest(projectId) {
  return get(`${getApiBase()}/illustration-assets/storyboard/${projectId}`)
}

export async function listIllustrationJobs(projectId = "") {
  return get(`${getApiBase()}/illustration-generation${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`)
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

export async function uploadIllustrationFrameAsset({ projectId, frameId, file }) {
  const form = new FormData()
  form.append("project_id", projectId)
  form.append("frame_id", frameId)
  form.append("file", file)

  return handle(fetch(`${getApiBase()}/illustration-assets/upload`, {
    method: "POST",
    body: form
  }))
}

export async function importGeneratedIllustrationFrame({ projectId, frameId, file, approve = true }) {
  const form = new FormData()
  form.append("project_id", projectId)
  form.append("frame_id", frameId)
  form.append("approve", String(approve))
  form.append("file", file)

  return handle(fetch(`${getApiBase()}/illustration-generation/import`, {
    method: "POST",
    body: form
  }))
}

export async function setupLocalAi(payload = {}) {
  return post(`${getApiBase()}/local-ai-installer/setup`, payload)
}

export async function ensureLocalProvider(provider) {
  return post(`${getApiBase()}/local-engine-manager/ensure`, { provider })
}

export async function stopLocalProvider(provider) {
  return post(`${getApiBase()}/local-engine-manager/stop`, { provider })
}

export async function setLocalAiDefaultProvider(provider) {
  return post(`${getApiBase()}/local-engine-manager/default-provider`, { provider })
}

export async function getLocalAiRuntimeStatus() {
  return get(`${getApiBase()}/local-ai-runtime/status`)
}

export async function getLocalEngineManagerStatus() {
  return get(`${getApiBase()}/local-engine-manager/status`)
}

export async function buildEditorialEngine(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-engine/build/${projectId}`, payload)
}

export async function previewEditorialEngine(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-engine/preview/${projectId}`, payload)
}

export async function repaginateEditorialEngine(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-engine/repaginate/${projectId}`, payload)
}

export async function mergeEditorialPages(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-engine/merge-pages/${projectId}`, payload)
}

export async function splitEditorialPage(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-engine/split-page/${projectId}`, payload)
}

export async function editorialToStory(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-production/story/${projectId}`, payload)
}

export async function editorialToIllustrations(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-production/illustrations/${projectId}`, payload)
}

export async function editorialToStoryboard(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-production/storyboard/${projectId}`, payload)
}

export async function generateEditorialIllustrations(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-media/generate-illustrations/${projectId}`, payload)
}

export async function buildEditorialVideoPackage(projectId, payload = {}) {
  return post(`${getApiBase()}/editorial-media/build-video-package/${projectId}`, payload)
}

export async function renderFinalVideo(projectId, payload = {}) {
  return post(`${getApiBase()}/final-media/render-video/${projectId}`, payload)
}

export async function exportEditorialEpub(projectId, payload = {}) {
  return post(`${getApiBase()}/final-media/export-epub/${projectId}`, payload)
}

export async function getLocalVersionInfo() {
  return get(`${getApiBase()}/updater/local-version`)
}

export async function checkForUpdates(payload = {}) {
  return post(`${getApiBase()}/updater/check`, payload)
}

export async function downloadUpdate(payload = {}) {
  return post(`${getApiBase()}/updater/download`, payload)
}

export async function runSystemSmokeV1() {
  return get(`${getApiBase()}/system-smoke-v1`)
}

export async function getV1Readiness(projectId) {
  return get(`${getApiBase()}/v1-readiness/${projectId}`)
    }

