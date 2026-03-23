import { useEffect, useState } from "react"
import {
  autoConnect,
  getConnectionProfile,
  getConnectionState,
  saveConnectionProfile,
  setManualConnection
} from "../api.js"

function ActionButton({ children, onClick, color = "#2F5E2E" }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "10px 12px",
        borderRadius: 12,
        border: "none",
        background: color,
        color: "#fff",
        fontWeight: 700,
        cursor: "pointer"
      }}
    >
      {children}
    </button>
  )
}

export default function PcConnectionPanel({ connected, checkingConnection, onConnected }) {
  const [profile, setProfile] = useState(getConnectionProfile())
  const [state, setState] = useState(getConnectionState())
  const [manualHost, setManualHost] = useState("")
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    setProfile(getConnectionProfile())
    setState(getConnectionState())
  }, [connected, checkingConnection])

  function refreshState() {
    setProfile(getConnectionProfile())
    setState(getConnectionState())
  }

  async function handleAutoConnect() {
    setBusy(true)
    try {
      await autoConnect()
      refreshState()
      onConnected?.()
    } finally {
      setBusy(false)
    }
  }

  async function handleSaveProfile() {
    saveConnectionProfile(profile)
    refreshState()
    alert("Perfil de ligação guardado.")
  }

  async function handleManualConnect() {
    if (!manualHost.trim()) {
      alert("Indica um host manual.")
      return
    }

    setBusy(true)
    try {
      const result = await setManualConnection(manualHost)
      refreshState()
      onConnected?.()

      if (!result.ok) {
        alert(result.error || "Ligação manual falhou.")
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <div
      style={{
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
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>Ligação ao PC</h3>

      <div><strong>Estado:</strong> {checkingConnection ? "A verificar..." : state?.label || "Sem ligação"}</div>
      <div><strong>Host ativo:</strong> {state?.activeHost || "-"}</div>
      <div><strong>API ativa:</strong> {state?.activeApiBase || "-"}</div>

      <label>Nome do PC</label>
      <input
        value={profile.pcName || ""}
        onChange={(e) => setProfile((current) => ({ ...current, pcName: e.target.value }))}
        placeholder="Ex: PC-André"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Host LAN (Casa)</label>
      <input
        value={profile.lanHost || ""}
        onChange={(e) => setProfile((current) => ({ ...current, lanHost: e.target.value }))}
        placeholder="Ex: 192.168.1.25:8787"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Host remoto privado</label>
      <input
        value={profile.remoteHost || ""}
        onChange={(e) => setProfile((current) => ({ ...current, remoteHost: e.target.value }))}
        placeholder="Ex: 100.x.y.z:8787"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Código de emparelhamento</label>
      <input
        value={profile.pairCode || ""}
        onChange={(e) => setProfile((current) => ({ ...current, pairCode: e.target.value }))}
        placeholder="Ex: BARI-7K2P-91XM"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <ActionButton onClick={handleSaveProfile}>Guardar perfil</ActionButton>
        <ActionButton onClick={handleAutoConnect} color="#0369a1">
          {busy ? "A ligar..." : "Ligação automática"}
        </ActionButton>
      </div>

      <label>Ligação manual avançada</label>
      <input
        value={manualHost}
        onChange={(e) => setManualHost(e.target.value)}
        placeholder="Ex: 192.168.1.25:8787 ou host remoto"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <ActionButton onClick={handleManualConnect} color="#7c3aed">
        Ligar manualmente
      </ActionButton>
    </div>
  )
      }
