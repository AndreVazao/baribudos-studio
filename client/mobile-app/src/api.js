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

export async function updateProject(projectId, payload = {}, user = {}) {
  return patch(`${getApiBase()}/projects/${projectId}${qs({
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`, payload)
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

export async function createIp(payload = {}) {
  return post(`${getApiBase()}/ip-creator`, payload)
}

export async function getIpBySlug(slug, user = {}) {
  return get(`${getApiBase()}/ip-creator/${slug}${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function getIpPermissions(slug, user = {}) {
  return get(`${getApiBase()}/ip-creator/${slug}/permissions${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
                       }

export async function getIpBranding(slug, user = {}) {
  return get(`${getApiBase()}/ip-branding/${slug}${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function updateIpBranding(slug, brandAssets = {}, user = {}) {
  return patch(`${getApiBase()}/ip-branding/${slug}`, {
    brand_assets: brandAssets,
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })
}

export async function uploadIpBrandingAsset(slug, assetType, file, user = {}) {
  const form = new FormData()
  form.append("asset_type", assetType)
  form.append("user_id", user?.id || "")
  form.append("user_name", user?.name || "")
  form.append("user_role", user?.role || "")
  form.append("file", file)

  return handle(fetch(`${getApiBase()}/ip-branding/${slug}/upload`, {
    method: "POST",
    body: form
  }))
}

export async function getIpPalette(slug, user = {}) {
  return get(`${getApiBase()}/ip-palette/${slug}${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function updateIpPalette(slug, palette = {}, user = {}) {
  return patch(`${getApiBase()}/ip-palette/${slug}`, {
    palette,
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })
}

export async function getIpCharacters(slug, user = {}) {
  return get(`${getApiBase()}/ip-characters/${slug}${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function updateIpCharacters(slug, mainCharacters = [], user = {}) {
  return patch(`${getApiBase()}/ip-characters/${slug}`, {
    main_characters: mainCharacters,
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })
}

export async function getIpCanon(slug, canonType, user = {}) {
  return get(`${getApiBase()}/ip-canons/${slug}/${canonType}${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function updateIpCanon(slug, canonType, data = {}, user = {}) {
  return patch(`${getApiBase()}/ip-canons/${slug}/${canonType}`, {
    data,
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })
}

export async function getIpMetadata(slug, user = {}) {
  return get(`${getApiBase()}/ip-metadata/${slug}${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function updateIpMetadata(slug, payload = {}, user = {}) {
  return patch(`${getApiBase()}/ip-metadata/${slug}`, {
    metadata: payload?.metadata || {},
    default_language: payload?.default_language || "pt-PT",
    output_languages: payload?.output_languages || ["pt-PT"],
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })
}

export async function getSagaRuntime(slug) {
  return get(`${getApiBase()}/saga-runtime/${slug}`)
}

export async function buildCover(payload = {}) {
  return post(`${getApiBase()}/covers/build`, payload)
}

export async function uploadIllustrationForCover({ sagaId, projectId, file }) {
  const form = new FormData()
  form.append("saga_id", sagaId)
  form.append("project_id", projectId)
  form.append("file", file)

  return handle(fetch(`${getApiBase()}/illustrations/upload`, {
    method: "POST",
    body: form
  }))
}

export async function getProjectCommercial(projectId) {
  return get(`${getApiBase()}/project-commercial/${projectId}`)
}

export async function updateProjectCommercial(projectId, commercial = {}, user = {}) {
  return patch(`${getApiBase()}/project-commercial/${projectId}${qs({
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`, { commercial })
}

export async function getPublicationPackage(projectId) {
  return get(`${getApiBase()}/publication-package/${projectId}`)
}

export async function freezePublicationPackage(projectId, user = {}) {
  return post(`${getApiBase()}/publication-package/${projectId}/freeze${qs({
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function getPublishReadiness(projectId) {
  return get(`${getApiBase()}/publish-readiness/${projectId}`)
}

export async function markProjectReady(projectId, user = {}) {
  return post(`${getApiBase()}/publish-readiness/${projectId}/mark-ready${qs({
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function unmarkProjectReady(projectId, user = {}) {
  return post(`${getApiBase()}/publish-readiness/${projectId}/unmark-ready${qs({
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function getProjectIntegrity(projectId) {
  return get(`${getApiBase()}/project-integrity/${projectId}`)
}

export async function repairProject(projectId, user = {}) {
  return post(`${getApiBase()}/project-integrity/${projectId}/repair${qs({
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function listProductionRuns() {
  return get(`${getApiBase()}/production-pipeline`)
}

export async function runProductionPipeline(projectId, payload = {}) {
  return post(`${getApiBase()}/production-pipeline/run/${projectId}`, payload)
}

export async function listSystemSmokeResults() {
  return get(`${getApiBase()}/system-smoke`)
}

export async function runSystemSmoke(projectId) {
  return post(`${getApiBase()}/system-smoke/${projectId}`)
}

export async function runSystemSmokeV1() {
  return get(`${getApiBase()}/system-smoke-v1`)
}

export async function getV1Readiness(projectId) {
  return get(`${getApiBase()}/v1-readiness/${projectId}`)
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

export async function setupLocalAudio(payload = {}) {
  return post(`${getApiBase()}/local-audio-installer/setup`, payload)
}

export async function getLocalAudioEngineManagerStatus() {
  return get(`${getApiBase()}/local-audio-engine-manager/status`)
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

export async function listIllustrationRuns() {
  return get(`${getApiBase()}/illustration-pipeline`)
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

export async function getLocalAudioStatus() {
  return get(`${getApiBase()}/local-audio-installer/status`)
}

export async function ensureLocalAudioProvider(provider) {
  return post(`${getApiBase()}/local-audio-engine-manager/ensure`, { provider })
}

export async function stopLocalAudioProvider(provider) {
  return post(`${getApiBase()}/local-audio-engine-manager/stop`, { provider })
}

export async function setLocalAudioDefaultProvider(provider) {
  return post(`${getApiBase()}/local-audio-engine-manager/default-provider`, { provider })
    }

export async function moveStoryLayoutPage(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/move-page/${projectId}`, payload)
}

export async function moveStoryLayoutText(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/move-text/${projectId}`, payload)
}

export async function splitStoryLayoutPage(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/split-page/${projectId}`, payload)
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

export async function moveStoryLayoutPage(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/move-page/${projectId}`, payload)
}

export async function moveStoryLayoutText(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/move-text/${projectId}`, payload)
}

export async function splitStoryLayoutPage(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/split-page/${projectId}`, payload)
                                       }

