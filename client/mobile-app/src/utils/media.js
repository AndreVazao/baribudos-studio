export function normalizeMediaUrl(input) {
  const value = String(input || "").trim()
  if (!value) return ""

  if (value.startsWith("http://") || value.startsWith("https://")) {
    return value
  }

  const normalized = value.replace(/\\/g, "/")
  const lower = normalized.toLowerCase()
  if (lower.includes("/storage/") || lower.startsWith("storage/")) {
    return ""
  }

  const publicIndex = lower.lastIndexOf("/public/")
  if (publicIndex >= 0) return normalized.slice(publicIndex)
  if (lower.startsWith("public/")) return `/${normalized}`
  if (lower.startsWith("/public/")) return normalized

  return normalized
}
