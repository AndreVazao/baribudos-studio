import { useState } from "react"
import DashboardPanel from "./components/DashboardPanel.jsx"
import LoginPanel from "./components/LoginPanel.jsx"
import PcConnectionPanel from "./components/PcConnectionPanel.jsx"
import { clearSavedUser, getSavedUser } from "./api.js"

export default function App() {
  const [connected, setConnected] = useState(false)
  const [user, setUser] = useState(getSavedUser())

  function handleLogout() {
    clearSavedUser()
    setUser(null)
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f3f4f6",
        padding: 16,
        display: "grid",
        gap: 16
      }}
    >
      <PcConnectionPanel onConnected={() => setConnected(true)} />

      {connected && !user ? (
        <LoginPanel onLoggedIn={setUser} />
      ) : null}

      {connected && user ? (
        <>
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              background: "#fff",
              padding: 16,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}
          >
            <div>
              <strong>{user.name}</strong> — {user.role}
            </div>
            <button onClick={handleLogout}>Sair</button>
          </div>

          <DashboardPanel user={user} />
        </>
      ) : null}
    </div>
  )
}
