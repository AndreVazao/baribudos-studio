import { useState } from "react"
import { clearSavedUser, getSavedUser } from "./api.js"
import AppShell from "./components/AppShell.jsx"
import BrandHeader from "./components/BrandHeader.jsx"
import DashboardPanel from "./components/DashboardPanel.jsx"
import LoginPanel from "./components/LoginPanel.jsx"
import PcConnectionPanel from "./components/PcConnectionPanel.jsx"

export default function App() {
  const [connected, setConnected] = useState(false)
  const [user, setUser] = useState(getSavedUser())

  function handleLogout() {
    clearSavedUser()
    setUser(null)
  }

  return (
    <AppShell>
      <BrandHeader />

      <PcConnectionPanel onConnected={() => setConnected(true)} />

      {connected && !user ? (
        <LoginPanel onLoggedIn={setUser} />
      ) : null}

      {connected && user ? (
        <>
          <div
            style={{
              border: "1px solid rgba(255,255,255,0.25)",
              borderRadius: 16,
              background: "rgba(255,255,255,0.84)",
              backdropFilter: "blur(8px)",
              padding: 16,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              boxShadow: "0 10px 24px rgba(0,0,0,0.10)"
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
