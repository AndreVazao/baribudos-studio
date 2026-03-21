import { get, getApiBase, post } from "./core.js"

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

export async function uploadVoiceSample({ name, language = "", notes = "", file }) {
  const form = new FormData()
  form.append("name", name || "Nova voz")
  form.append("language", language || "")
  form.append("notes", notes || "")
  form.append("file", file)

  const { handle } = await import("./core.js")
  return handle(fetch(`${getApiBase()}/voice-library/upload`, {
    method: "POST",
    body: form
  }))
}

export async function generateVoicePreview(payload = {}) {
  return post(`${getApiBase()}/voice-preview`, payload)
              }
