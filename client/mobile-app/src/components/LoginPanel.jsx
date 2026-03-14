import { useState } from "react"
import { login, setSavedUser } from "../api.js"

export default function LoginPanel({ onLoggedIn }) {
  const [name, setName] = useState("André")
  const [pin, setPin] = useState("1234")
  const [busy, setBusy] = useState(false)

  async function handleLogin() {
    try {
      setBusy(true)
      const result = await login(name, pin)
      const user = result?.user || null
      if (!user) throw new Error("Login inválido.")
      setSavedUser(user)
      onLoggedIn?.(user)
    } catch (error) {
      alert(error?.message || "Falha no login.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div
      style={{
        position: "relative",
        zIndex: 2,
        border: "1px solid rgba(255,255,255,0.25)",
        borderRadius: 16,
        background: "rgba(255,255,255,0.84)",
        backdropFilter: "blur(8px)",
        padding: 16,
        display: "grid",
        gap: 12,
        boxShadow: "0 10px 24px rgba(0,0,0,0.10)"
      }}
    >
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>Login</h3>

      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Nome"
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none"
        }}
      />

      <input
        value={pin}
        onChange={(e) => setPin(e.target.value)}
        placeholder="PIN"
        type="password"
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none"
        }}
      />

      <button
        onClick={handleLogin}
        disabled={busy}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "none",
          background: "#2F5E2E",
          color: "#fff",
          fontWeight: 700,
          cursor: "pointer"
        }}
      >
        {busy ? "A entrar..." : "Entrar"}
      </button>
    </div>
  )
}
