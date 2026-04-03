import { get, getApiBase, handle, patch, post, qs } from "./core.js"

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

export async function getIpCharactersConsistencySummary(slug, user = {}) {
  return get(`${getApiBase()}/ip-characters/${slug}/consistency-summary${qs({
    user_id: user?.id || "",
    user_name: user?.name || "",
    user_role: user?.role || ""
  })}`)
}

export async function getIpCharacterLockStatus(slug, user = {}) {
  return get(`${getApiBase()}/ip-characters/${slug}/character-lock-status${qs({
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
