import { useEffect, useState } from "react"
import {
  autoConnect,
  checkForUpdates,
  getConnectionBadge,
  getConnectionState,
  getCurrentUser,
  hasAuthToken,
  logoutSession,
  restoreAuthToken,
  setSavedUser
} from "./api.js"
import AppShell from "./components/AppShell.jsx"
import BrandHeader from "./components/BrandHeader.jsx"
import DashboardPanel from "./components/DashboardPanel.jsx"
import LoginPanel from "./components/LoginPanel.jsx"
import PcConnectionPanel from "./components/PcConnectionPanel.jsx"

function ConnectionBadge() {
  const [badge, setBadge] = useState(getConnectionBadge())

  useEffect(() => {
    const id = setInterval(() => {
      setBadge(getConnectionBadge())
    }, 1500)

    return () => clearInterval(id)
  }, [])

  return (
    <div
      style={{
        position: "fixed",
        top: 12,
        right: 12,
        zIndex: 9999,
        background: badge.color,
        color: "#fff",
        padding: "8px 12px",
        borderRadius: 999,
        fontWeight: 700,
        fontSize: 12,
        boxShadow: "0 8px 20px rgba(0,0,0,0.18)"
      }}
    >
      {badge.text}
    </div>
  )
}

export default function App() {
  const [connected, setConnected] = useState(false)
  const [checkingConnection, setCheckingConnection] = useState(true)
  const [user, setUser] = useState(null)
  const [updateInfo, setUpdateInfo] = useState(null)
  const [updateDismissed, setUpdateDismissed] = useState(false)

  useEffect(() => {
    boot()
    const handleExpired = () => setUser(null)
    window.addEventListener("baribudos:auth-expired", handleExpired)
    return () => window.removeEventListener("baribudos:auth-expired", handleExpired)
  }, [])

  useEffect(() => {
    if (!connected) return
    runStartupUpdateCheck()
  }, [connected])

  async function boot() {
    setCheckingConnection(true)

    try {
      await autoConnect()
      const state = getConnectionState()
      const isConnected = Boolean(state?.connected)
      setConnected(isConnected)
      if (isConnected) {
        try {
          await restoreAuthToken()
          if (!hasAuthToken()) {
            setUser(null)
          } else {
            const currentUser = await getCurrentUser()
            setSavedUser(currentUser)
            setUser(currentUser)
          }
        } catch {
          setUser(null)
        }
      }
    } catch {
      setConnected(false)
    }

    setCheckingConnection(false)
  }

  async function runStartupUpdateCheck() {
    try {
      const res = await checkForUpdates({ channel: "stable" })
      if (res?.update_available) {
        setUpdateInfo(res)
        setUpdateDismissed(false)
      }
    } catch {
      // silencioso no arranque
    }
  }

  async function handleConnected() {
    const state = getConnectionState()
    const isConnected = Boolean(state?.connected)
    setConnected(isConnected)
    if (!isConnected) return
    try {
      await restoreAuthToken()
      if (!hasAuthToken()) return
      const currentUser = await getCurrentUser()
      setSavedUser(currentUser)
      setUser(currentUser)
    } catch {
      setUser(null)
    }
  }

  function handleLogin(nextUser) {
    setUser(nextUser)
    setSavedUser(nextUser)
  }

  async function handleLogout() {
    try {
      await logoutSession()
    } catch (error) {
      alert(error?.message || "Sessão removida localmente; a revogação no servidor não foi confirmada.")
    } finally {
      setUser(null)
    }
  }

  function handleOpenDownload() {
    const url = String(updateInfo?.download_url || "").trim()
    if (!url) {
      alert("Sem link de download disponível.")
      return
    }
    window.open(url, "_blank", "noopener,noreferrer")
  }

  return (
    <AppShell>
      <ConnectionBadge />
      <BrandHeader />

      {updateInfo?.update_available && !updateDismissed ? (
        <div
          style={{
            marginBottom: 16,
            border: "1px solid rgba(29,78,216,0.25)",
            borderRadius: 16,
            background: "rgba(219,234,254,0.7)",
            padding: 16,
            display: "grid",
            gap: 10
          }}
        >
          <div><strong>Nova versão disponível:</strong> {updateInfo?.remote?.version || "-"}</div>
          <div>{updateInfo?.remote?.notes || "Foi encontrada uma atualização do Studio."}</div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              onClick={handleOpenDownload}
              style={{
                padding: "10px 12px",
                borderRadius: 12,
                border: "none",
                background: "#1d4ed8",
                color: "#fff",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              Atualizar
            </button>

            <button
              onClick={() => setUpdateDismissed(true)}
              style={{
                padding: "10px 12px",
                borderRadius: 12,
                border: "1px solid #cbd5e1",
                background: "#fff",
                color: "#111827",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              Agora não
            </button>
          </div>
        </div>
      ) : null}

      {!connected ? (
        <PcConnectionPanel
          connected={connected}
          checkingConnection={checkingConnection}
          onConnected={handleConnected}
        />
      ) : null}

      {connected && !user ? (
        <LoginPanel onLoggedIn={handleLogin} />
      ) : null}

      {connected && user ? (
        <>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 12,
              marginBottom: 16,
              padding: 12,
              borderRadius: 16,
              background: "rgba(255,255,255,0.75)",
              border: "1px solid rgba(255,255,255,0.3)"
            }}
          >
            <div>
              <strong>{user.name}</strong> — {user.role}
            </div>

            <button
              onClick={handleLogout}
              style={{
                padding: "10px 12px",
                borderRadius: 12,
                border: "none",
                background: "#2F5E2E",
                color: "#fff",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              Sair
            </button>
          </div>

          <DashboardPanel user={user} />
        </>
      ) : null}
    </AppShell>
  )
}
