import { get, getApiBase, handle, post } from "./core.js"

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
