const TOKEN_KEY = "session-token"
const STORAGE_PREFIX = "baribudos-studio-"

let adapterPromise

function isTauriRuntime() {
  return typeof window !== "undefined" && Boolean(window.__TAURI_INTERNALS__)
}

async function getNativeAdapter() {
  if (isTauriRuntime()) {
    const { invoke } = await import("@tauri-apps/api/core")
    return {
      get: () => invoke("secure_session_get"),
      set: (token) => invoke("secure_session_set", { token }),
      clear: () => invoke("secure_session_clear")
    }
  }

  if (typeof window === "undefined") return null

  const { Capacitor } = await import("@capacitor/core")
  if (!Capacitor.isNativePlatform()) return null

  const { SecureStorage, KeychainAccess } = await import("@aparajita/capacitor-secure-storage")
  await SecureStorage.setKeyPrefix(STORAGE_PREFIX)

  return {
    get: async () => {
      const value = await SecureStorage.get(TOKEN_KEY, false, false)
      return typeof value === "string" ? value : null
    },
    set: (token) => SecureStorage.set(
      TOKEN_KEY,
      token,
      false,
      false,
      KeychainAccess.whenUnlockedThisDeviceOnly
    ),
    clear: () => SecureStorage.remove(TOKEN_KEY, false)
  }
}

async function nativeAdapter() {
  if (!adapterPromise) {
    adapterPromise = getNativeAdapter().catch((error) => {
      adapterPromise = undefined
      throw error
    })
  }
  return adapterPromise
}

export async function readStoredSessionToken() {
  const adapter = await nativeAdapter()
  if (!adapter) return null
  const token = await adapter.get()
  return typeof token === "string" && token.trim() ? token.trim() : null
}

export async function writeStoredSessionToken(token) {
  const normalized = typeof token === "string" ? token.trim() : ""
  if (!normalized || normalized.length > 4096) {
    throw new Error("Token de sessão inválido.")
  }
  const adapter = await nativeAdapter()
  if (!adapter) return false
  await adapter.set(normalized)
  return true
}

export async function removeStoredSessionToken() {
  const adapter = await nativeAdapter()
  if (!adapter) return
  await adapter.clear()
}
