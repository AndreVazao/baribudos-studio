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

function getApiOrigin() {
  const base = getApiBase()
  return base.replace(/\/api$/, "")
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
    const relative = normalized.slice(index)
    return `${getApiOrigin()}${relative}`
  }

  return ""
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

export async function getProjectCommercial(projectId) {
  return handle(fetch(`${getApiBase()}/project-commercial/${projectId}`))
}

export async function updateProjectCommercial(projectId, commercial, user) {
  const query = new URLSearchParams({
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/project-commercial/${projectId}?${query}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ commercial: commercial || {} })
  }))
}

export async function getPublicationPackage(projectId) {
  return handle(fetch(`${getApiBase()}/publication-package/${projectId}`))
}

export async function freezePublicationPackage(projectId, user) {
  const query = new URLSearchParams({
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/publication-package/${projectId}/freeze?${query}`, {
    method: "POST"
  }))
}

export async function getPublishReadiness(projectId) {
  return handle(fetch(`${getApiBase()}/publish-readiness/${projectId}`))
}

export async function markProjectReady(projectId, user) {
  const query = new URLSearchParams({
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/publish-readiness/${projectId}/mark-ready?${query}`, {
    method: "POST"
  }))
}

export async function unmarkProjectReady(projectId, user) {
  const query = new URLSearchParams({
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/publish-readiness/${projectId}/unmark-ready?${query}`, {
    method: "POST"
  }))
}

export async function getProjectIntegrity(projectId) {
  return handle(fetch(`${getApiBase()}/project-integrity/${projectId}`))
}

export async function repairProject(projectId, user) {
  const query = new URLSearchParams({
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/project-integrity/${projectId}/repair?${query}`, {
    method: "POST"
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

export async function getFactoryContext(payload) {
  return handle(fetch(`${getApiBase()}/factory/context`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
    }
export async function listPublications() {
  return handle(fetch(`${getApiBase()}/publishing`))
}

export async function publishProject(payload, user) {
  const query = new URLSearchParams({
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/publishing/publish?${query}`, {
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

export async function getIpBranding(slug, user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/ip-branding/${slug}?${query}`))
}

export async function updateIpBranding(slug, brandAssets, user) {
  return handle(fetch(`${getApiBase()}/ip-branding/${slug}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      brand_assets: brandAssets,
      user_id: user?.id || "",
      user_name: user?.name || "",
      user_role: user?.role || ""
    })
  }))
}

export async function uploadIpBrandingAsset(slug, assetType, file, user) {
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

export async function getIpCharacters(slug, user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/ip-characters/${slug}?${query}`))
}

export async function updateIpCharacters(slug, mainCharacters, user) {
  return handle(fetch(`${getApiBase()}/ip-characters/${slug}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      main_characters: mainCharacters,
      user_id: user?.id || "",
      user_name: user?.name || "",
      user_role: user?.role || ""
    })
  }))
}

export async function getIpCanon(slug, canonType, user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/ip-canons/${slug}/${canonType}?${query}`))
}

export async function updateIpCanon(slug, canonType, data, user) {
  return handle(fetch(`${getApiBase()}/ip-canons/${slug}/${canonType}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      data,
      user_id: user?.id || "",
      user_name: user?.name || "",
      user_role: user?.role || ""
    })
  }))
}

export async function getIpMetadata(slug, user) {
  const query = new URLSearchParams({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  }).toString()

  return handle(fetch(`${getApiBase()}/ip-metadata/${slug}?${query}`))
}

export async function updateIpMetadata(slug, payload, user) {
  return handle(fetch(`${getApiBase()}/ip-metadata/${slug}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      metadata: payload?.metadata || {},
      default_language: payload?.default_language || "pt-PT",
      output_languages: payload?.output_languages || ["pt-PT"],
      user_id: user?.id || "",
      user_name: user?.name || "",
      user_role: user?.role || ""
    })
  }))
}

export async function getSagaRuntime(slug) {
  return handle(fetch(`${getApiBase()}/saga-runtime/${slug}`))
}

export async function buildCover(payload) {
  return handle(fetch(`${getApiBase()}/covers/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  }))
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

export async function listSystemSmokeResults() {
  return handle(fetch(`${getApiBase()}/system-smoke`))
}

export async function runSystemSmoke(projectId) {
  return handle(fetch(`${getApiBase()}/system-smoke/${projectId}`, {
    method: "POST"
  }))
      }

export async function listProductionRuns() {
  return handle(fetch(`${getApiBase()}/production-pipeline`))
}

export async function runProductionPipeline(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/production-pipeline/run/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
    }

export async function listIllustrationRuns() {
  return handle(fetch(`${getApiBase()}/illustration-pipeline`))
}

export async function getIllustrationPipeline(projectId) {
  return handle(fetch(`${getApiBase()}/illustration-pipeline/${projectId}`))
}

export async function setupIllustrationPipeline(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/illustration-pipeline/setup/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function updateIllustrationFrame(projectId, frameId, payload = {}) {
  return handle(fetch(`${getApiBase()}/illustration-pipeline/${projectId}/frame/${frameId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
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

export async function getStoryboardManifest(projectId) {
  return handle(fetch(`${getApiBase()}/illustration-assets/storyboard/${projectId}`))
}

export async function listIllustrationJobs(projectId = "") {
  const suffix = projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""
  return handle(fetch(`${getApiBase()}/illustration-generation${suffix}`))
}

export async function queueIllustrationGeneration(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/illustration-generation/queue/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function getIllustrationPromptPackage(projectId) {
  return handle(fetch(`${getApiBase()}/illustration-generation/package/${projectId}`))
}

export async function updateIllustrationJob(jobId, payload = {}) {
  return handle(fetch(`${getApiBase()}/illustration-generation/job/${jobId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
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

export async function getStoryLayout(projectId) {
  return handle(fetch(`${getApiBase()}/story-layout/${projectId}`))
}

export async function paginateStoryLayout(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/story-layout/paginate/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function updateStoryLayoutPage(projectId, pageId, payload = {}) {
  return handle(fetch(`${getApiBase()}/story-layout/page/${projectId}/${pageId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function createStoryLayoutPage(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/story-layout/page/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function deleteStoryLayoutPage(projectId, pageId) {
  return handle(fetch(`${getApiBase()}/story-layout/page/${projectId}/${pageId}`, {
    method: "DELETE"
  }))
}

export async function applyStoryLayout(projectId, payload = {}) {
  return handle(fetch(`${getApiBase()}/story-layout/apply/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

                      
