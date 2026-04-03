import { del, get, getApiBase, patch, post, qs } from "./core.js"

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

export async function updateSaga(slug, payload = {}) {
  return patch(`${getApiBase()}/sagas/${encodeURIComponent(String(slug || "").trim())}`, payload)
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

export async function moveStoryLayoutPage(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/move-page/${projectId}`, payload)
}

export async function moveStoryLayoutText(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/move-text/${projectId}`, payload)
}

export async function splitStoryLayoutPage(projectId, payload = {}) {
  return post(`${getApiBase()}/story-layout/split-page/${projectId}`, payload)
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
