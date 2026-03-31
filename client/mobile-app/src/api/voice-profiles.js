import { getApiBase, get, patch, post, qs } from "./core.js"

export async function listVoiceProfiles() {
  return get(`${getApiBase()}/voice-profiles`)
}

export async function createVoiceProfile(payload = {}) {
  return post(`${getApiBase()}/voice-profiles`, payload)
}

export async function updateVoiceProfile(voiceProfileId, payload = {}) {
  return patch(`${getApiBase()}/voice-profiles/${encodeURIComponent(String(voiceProfileId || "").trim())}`, payload)
}

export async function validateVoiceProfile(voiceProfileId, context = {}) {
  return get(`${getApiBase()}/voice-profiles/${encodeURIComponent(String(voiceProfileId || "").trim())}/validate${qs({
    ip_slug: context?.ip_slug || "",
    saga_slug: context?.saga_slug || "",
    role: context?.role || "",
  })}`)
}
