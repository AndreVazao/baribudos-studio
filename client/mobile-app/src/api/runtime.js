import { get, getApiBase, post } from "./core.js"

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

export async function getLocalAudioEngineManagerStatus() {
  return get(`${getApiBase()}/local-audio-engine-manager/status`)
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
