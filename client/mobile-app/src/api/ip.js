import { apiFetch, get, getApiBase, handle, patch, post } from "./core.js"

export async function listIps() {
  return get(`${getApiBase()}/ip-creator`)
}

export async function createIp(payload = {}) {
  return post(`${getApiBase()}/ip-creator`, payload)
}

export async function getIpBySlug(slug) {
  return get(`${getApiBase()}/ip-creator/${encodeURIComponent(slug)}`)
}

export async function getIpPermissions(slug) {
  return get(`${getApiBase()}/ip-creator/${encodeURIComponent(slug)}/permissions`)
}

export async function getIpBranding(slug) {
  return get(`${getApiBase()}/ip-branding/${slug}`)
}

export async function updateIpBranding(slug, brandAssets = {}) {
  return patch(`${getApiBase()}/ip-branding/${slug}`, {
    brand_assets: brandAssets,
  })
}

export async function uploadIpBrandingAsset(slug, assetType, file) {
  const form = new FormData()
  form.append("asset_type", assetType)
  form.append("file", file)

  return handle(apiFetch(`${getApiBase()}/ip-branding/${slug}/upload`, {
    method: "POST",
    body: form
  }))
}

export async function getIpPalette(slug) {
  return get(`${getApiBase()}/ip-palette/${slug}`)
}

export async function updateIpPalette(slug, palette = {}) {
  return patch(`${getApiBase()}/ip-palette/${slug}`, {
    palette,
  })
}

export async function getIpCharacters(slug) {
  return get(`${getApiBase()}/ip-characters/${slug}`)
}

export async function getIpCharactersConsistencySummary(slug) {
  return get(`${getApiBase()}/ip-characters/${slug}/consistency-summary`)
}

export async function getIpCharacterLockStatus(slug) {
  return get(`${getApiBase()}/ip-characters/${slug}/character-lock-status`)
}

export async function updateIpCharacters(slug, mainCharacters = []) {
  return patch(`${getApiBase()}/ip-characters/${slug}`, {
    main_characters: mainCharacters,
  })
}

export async function getIpCanon(slug, canonType) {
  return get(`${getApiBase()}/ip-canons/${slug}/${canonType}`)
}

export async function updateIpCanon(slug, canonType, data = {}) {
  return patch(`${getApiBase()}/ip-canons/${slug}/${canonType}`, {
    data,
  })
}

export async function getIpMetadata(slug) {
  return get(`${getApiBase()}/ip-metadata/${slug}`)
}

export async function updateIpMetadata(slug, payload = {}) {
  return patch(`${getApiBase()}/ip-metadata/${slug}`, {
    metadata: payload?.metadata || {},
    default_language: payload?.default_language || "pt-PT",
    output_languages: payload?.output_languages || ["pt-PT"],
  })
}

export async function getSagaRuntime(slug) {
  return get(`${getApiBase()}/saga-runtime/${slug}`)
}
