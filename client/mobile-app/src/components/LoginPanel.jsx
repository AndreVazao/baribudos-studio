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
        border: "1px solid #ddd",
        borderRadius: 12,
        background: "#fff",
        padding: 16,
        display: "grid",
        gap: 12
      }}
    >
      <h3 style={{ margin: 0 }}>Login</h3>

      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Nome"
      />

      <input
        value={pin}
        onChange={(e) => setPin(e.target.value)}
        placeholder="PIN"
        type="password"
      />

      <button onClick={handleLogin} disabled={busy}>
        {busy ? "A entrar..." : "Entrar"}
      </button>
    </div>
  )
        }
