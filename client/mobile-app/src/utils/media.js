export function normalizeMediaUrl(input) {
  const value = String(input || "").trim()
  if (!value) return ""

  if (value.startsWith("http://") || value.startsWith("https://")) {
    return value
  }

  const normalized = value.replace(/\\/g, "/")
  const storageIndex = normalized.toLowerCase().lastIndexOf("/storage/")
  if (storageIndex >= 0) {
    return normalized.slice(storageIndex)
  }

  if (normalized.toLowerCase().startsWith("storage/")) {
    return `/${normalized}`
  }

  if (normalized.toLowerCase().startsWith("/storage/")) {
    return normalized
  }

  const publicIndex = normalized.toLowerCase().lastIndexOf("/public/")
  if (publicIndex >= 0) {
    return normalized.slice(publicIndex)
  }

  if (normalized.toLowerCase().startsWith("public/")) {
    return `/${normalized}`
  }

  if (normalized.toLowerCase().startsWith("/public/")) {
    return normalized
  }

  return normalized
    }
