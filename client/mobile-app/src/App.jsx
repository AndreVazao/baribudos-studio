import { useEffect, useState } from "react"
import {
  checkForUpdates,
  clearSavedUser,
  getSavedUser
} from "./api.js"
import AppShell from "./components/AppShell.jsx"
import BrandHeader from "./components/BrandHeader.jsx"
import DashboardPanel from "./components/DashboardPanel.jsx"
import LoginPanel from "./components/LoginPanel.jsx"
import PcConnectionPanel from "./components/PcConnectionPanel.jsx"

export default function App() {
  const [connected, setConnected] = useState(false)
  const [user, setUser] = useState(getSavedUser())
  const [updateInfo, setUpdateInfo] = useState(null)
  const [updateDismissed, setUpdateDismissed] = useState(false)

  useEffect(() => {
    if (!connected) return
    runStartupUpdateCheck()
  }, [connected])

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

  function handleLogout() {
    clearSavedUser()
    setUser(null)
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
        <PcConnectionPanel onConnected={() => setConnected(true)} />
      ) : null}

      {connected && !user ? (
        <LoginPanel onLogin={setUser} />
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
