import { del, get, getApiBase, patch, post } from "./core.js"

export async function listProjects() {
  return get(`${getApiBase()}/projects`)
}

export async function createProject(payload = {}) {
  return post(`${getApiBase()}/projects`, payload)
}

export async function updateProject(projectId, payload = {}) {
  return patch(`${getApiBase()}/projects/${encodeURIComponent(projectId)}`, payload)
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

export async function updateProjectCommercial(projectId, commercial = {}) {
  return patch(`${getApiBase()}/project-commercial/${encodeURIComponent(projectId)}`, { commercial })
}

export async function getPublicationPackage(projectId) {
  return get(`${getApiBase()}/publication-package/${projectId}`)
}

export async function freezePublicationPackage(projectId) {
  return post(`${getApiBase()}/publication-package/${encodeURIComponent(projectId)}/freeze`)
}

export async function getPublishReadiness(projectId) {
  return get(`${getApiBase()}/publish-readiness/${projectId}`)
}

export async function markProjectReady(projectId) {
  return post(`${getApiBase()}/publish-readiness/${encodeURIComponent(projectId)}/mark-ready`)
}

export async function unmarkProjectReady(projectId) {
  return post(`${getApiBase()}/publish-readiness/${encodeURIComponent(projectId)}/unmark-ready`)
}

export async function getProjectIntegrity(projectId) {
  return get(`${getApiBase()}/project-integrity/${projectId}`)
}

export async function repairProject(projectId) {
  return post(`${getApiBase()}/project-integrity/${encodeURIComponent(projectId)}/repair`)
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
