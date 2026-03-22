import { getApiBase, handle } from "./core.js"

export async function listAssets(filters = {}) {
  const params = new URLSearchParams()

  Object.entries(filters || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return
    params.set(key, String(value))
  })

  const query = params.toString()
  return handle(fetch(`${getApiBase()}/assets${query ? `?${query}` : ""}`))
}

export async function getAsset(assetId) {
  return handle(fetch(`${getApiBase()}/assets/${assetId}`))
}

export async function registerAsset(payload = {}) {
  return handle(fetch(`${getApiBase()}/assets/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }))
}

export async function uploadAsset({
  file,
  ip_slug,
  asset_type,
  context,
  project_id = "",
  series_name = "",
  publication_id = "",
  variant_id = "",
  language = "",
  is_primary = false,
  priority = 0,
  width = "",
  height = "",
  status = "draft"
}) {
  const form = new FormData()
  form.append("file", file)
  form.append("ip_slug", ip_slug)
  form.append("asset_type", asset_type)
  form.append("context", context)
  form.append("project_id", project_id)
  form.append("series_name", series_name)
  form.append("publication_id", publication_id)
  form.append("variant_id", variant_id)
  form.append("language", language)
  form.append("is_primary", String(is_primary))
  form.append("priority", String(priority))
  form.append("width", String(width || ""))
  form.append("height", String(height || ""))
  form.append("status", status)

  return handle(fetch(`${getApiBase()}/assets/upload`, {
    method: "POST",
    body: form
  }))
}

export async function publishAsset(assetId) {
  return handle(fetch(`${getApiBase()}/assets/${assetId}/publish`, {
    method: "POST"
  }))
}

export async function archiveAsset(assetId) {
  return handle(fetch(`${getApiBase()}/assets/${assetId}/archive`, {
    method: "POST"
  }))
}

export async function rollbackAsset(assetId) {
  return handle(fetch(`${getApiBase()}/assets/${assetId}/rollback`, {
    method: "POST"
  }))
}
