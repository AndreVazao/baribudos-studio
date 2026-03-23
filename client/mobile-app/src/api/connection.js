import {
  getApiBase,
  healthCheck,
  normalizeApiUrl,
  setApiBase
} from "./core.js"

const CONNECTION_PROFILE_KEY = "baribudos_connection_profile"
const CONNECTION_STATE_KEY = "baribudos_connection_state"

function safeJsonParse(value, fallback = null) {
  try {
    return JSON.parse(value)
  } catch {
    return fallback
  }
}

export function getConnectionProfile() {
  return (
    safeJsonParse(localStorage.getItem(CONNECTION_PROFILE_KEY), null) || {
      pcName: "",
      lanHost: "",
      remoteHost: "",
      pairCode: "",
      lastGoodHost: "",
      preferredMode: "auto"
    }
  )
}

export function saveConnectionProfile(profile = {}) {
  const current = getConnectionProfile()
  const next = {
    ...current,
    ...profile
  }
  localStorage.setItem(CONNECTION_PROFILE_KEY, JSON.stringify(next))
  return next
}

export function getConnectionState() {
  return (
    safeJsonParse(localStorage.getItem(CONNECTION_STATE_KEY), null) || {
      connected: false,
      mode: "offline",
      activeHost: "",
      activeApiBase: getApiBase(),
      checkedAt: "",
      label: "Sem ligação"
    }
  )
}

export function saveConnectionState(state = {}) {
  const current = getConnectionState()
  const next = {
    ...current,
    ...state
  }
  localStorage.setItem(CONNECTION_STATE_KEY, JSON.stringify(next))
  return next
}

function nowIso() {
  return new Date().toISOString()
}

function buildCandidates(profile) {
  const candidates = []
  const seen = new Set()

  function pushCandidate(host, mode) {
    const raw = String(host || "").trim()
    if (!raw) return

    const apiBase = normalizeApiUrl(raw)
    if (seen.has(apiBase)) return

    seen.add(apiBase)
    candidates.push({
      mode,
      host: raw,
      apiBase
    })
  }

  pushCandidate(profile?.lastGoodHost, "last_good")
  pushCandidate(profile?.lanHost, "lan")
  pushCandidate(profile?.remoteHost, "remote")
  pushCandidate(getApiBase(), "current")

  return candidates
}

function modeLabel(mode) {
  if (mode === "lan") return "Casa"
  if (mode === "remote") return "Remoto"
  if (mode === "last_good") return "Ligação guardada"
  if (mode === "current") return "Atual"
  return "Sem ligação"
}

export async function testApiCandidate(candidate) {
  try {
    const result = await healthCheck(candidate.apiBase)
    return {
      ok: true,
      candidate,
      result
    }
  } catch (error) {
    return {
      ok: false,
      candidate,
      error: error?.message || "Falha de ligação"
    }
  }
}

export async function autoConnect() {
  const profile = getConnectionProfile()
  const candidates = buildCandidates(profile)

  for (const candidate of candidates) {
    const tested = await testApiCandidate(candidate)

    if (!tested.ok) continue

    setApiBase(candidate.apiBase)

    saveConnectionProfile({
      lastGoodHost: candidate.host
    })

    const state = saveConnectionState({
      connected: true,
      mode: candidate.mode === "current" ? "manual" : candidate.mode,
      activeHost: candidate.host,
      activeApiBase: candidate.apiBase,
      checkedAt: nowIso(),
      label: modeLabel(candidate.mode)
    })

    return {
      ok: true,
      state,
      health: tested.result
    }
  }

  const offlineState = saveConnectionState({
    connected: false,
    mode: "offline",
    activeHost: "",
    activeApiBase: getApiBase(),
    checkedAt: nowIso(),
    label: "Sem ligação"
  })

  return {
    ok: false,
    state: offlineState
  }
}

export async function setManualConnection(host) {
  const apiBase = normalizeApiUrl(host)
  setApiBase(apiBase)

  saveConnectionProfile({
    lastGoodHost: host
  })

  const tested = await testApiCandidate({
    mode: "manual",
    host,
    apiBase
  })

  if (!tested.ok) {
    const state = saveConnectionState({
      connected: false,
      mode: "manual",
      activeHost: host,
      activeApiBase: apiBase,
      checkedAt: nowIso(),
      label: "Manual sem resposta"
    })

    return {
      ok: false,
      state,
      error: tested.error
    }
  }

  const state = saveConnectionState({
    connected: true,
    mode: "manual",
    activeHost: host,
    activeApiBase: apiBase,
    checkedAt: nowIso(),
    label: "Manual"
  })

  return {
    ok: true,
    state,
    health: tested.result
  }
}

export function getConnectionBadge() {
  const state = getConnectionState()

  if (!state?.connected) {
    return {
      text: "Sem ligação",
      color: "#991b1b"
    }
  }

  if (state.mode === "lan") {
    return {
      text: "Casa",
      color: "#2F5E2E"
    }
  }

  if (state.mode === "remote") {
    return {
      text: "Remoto",
      color: "#7c3aed"
    }
  }

  return {
    text: state.label || "Ligado",
    color: "#0369a1"
  }
}
