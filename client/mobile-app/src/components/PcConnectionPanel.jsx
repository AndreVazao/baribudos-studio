import { useEffect, useState } from "react"
import {
  autoConnect,
  createPairing,
  getConnectionProfile,
  getConnectionState,
  resolvePairingCode,
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
  const [pairCodeInput, setPairCodeInput] = useState("")
  const [generatedPairCode, setGeneratedPairCode] = useState("")

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

  function handleSaveProfile() {
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

  async function handleResolvePairCode() {
    if (!pairCodeInput.trim()) {
      alert("Indica um código de emparelhamento.")
      return
    }

    setBusy(true)
    try {
      const result = await resolvePairingCode(pairCodeInput)

      if (!result?.ok || !result?.pairing) {
        alert(result?.error || "Código não encontrado.")
        return
      }

      const pairing = result.pairing

      const nextProfile = saveConnectionProfile({
        pcName: pairing.pc_name || profile.pcName || "",
        lanHost: pairing.lan_host || "",
        remoteHost: pairing.remote_host || "",
        pairCode: pairing.pair_code || pairCodeInput
      })

      setProfile(nextProfile)
      setPairCodeInput(pairing.pair_code || pairCodeInput)

      await autoConnect()
      refreshState()
      onConnected?.()
      alert("Emparelhamento aplicado.")
    } catch (error) {
      alert(error?.message || "Falha ao resolver código.")
    } finally {
      setBusy(false)
    }
  }

  async function handleCreatePairing() {
    if (!profile.pcName?.trim()) {
      alert("Indica o nome do PC.")
      return
    }

    if (!profile.lanHost?.trim()) {
      alert("Indica o host LAN do PC.")
      return
    }

    setBusy(true)
    try {
      const result = await createPairing({
        pc_name: profile.pcName,
        lan_host: profile.lanHost,
        remote_host: profile.remoteHost || "",
        created_by: profile.pcName || ""
      })

      if (!result?.ok || !result?.pairing) {
        alert(result?.error || "Falha ao criar código.")
        return
      }

      const code = result.pairing.pair_code || ""
      setGeneratedPairCode(code)

      const nextProfile = saveConnectionProfile({
        ...profile,
        pairCode: code
      })

      setProfile(nextProfile)
      alert("Código de emparelhamento criado.")
    } catch (error) {
      alert(error?.message || "Falha ao criar pairing.")
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
        value={pairCodeInput || profile.pairCode || ""}
        onChange={(e) => setPairCodeInput(e.target.value)}
        placeholder="Ex: BARI-7K2P-91XM"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      {generatedPairCode ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            background: "rgba(220,252,231,0.8)",
            border: "1px solid rgba(34,197,94,0.25)"
          }}
        >
          <strong>Código gerado:</strong> {generatedPairCode}
        </div>
      ) : null}

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <ActionButton onClick={handleSaveProfile}>Guardar perfil</ActionButton>
        <ActionButton onClick={handleAutoConnect} color="#0369a1">
          {busy ? "A ligar..." : "Ligação automática"}
        </ActionButton>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <ActionButton onClick={handleResolvePairCode} color="#7c3aed">
          Emparelhar por código
        </ActionButton>
        <ActionButton onClick={handleCreatePairing} color="#0f766e">
          Gerar código neste PC
        </ActionButton>
      </div>

      <label>Ligação manual avançada</label>
      <input
        value={manualHost}
        onChange={(e) => setManualHost(e.target.value)}
        placeholder="Ex: 192.168.1.25:8787 ou host remoto"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <ActionButton onClick={handleManualConnect} color="#991b1b">
        Ligar manualmente
      </ActionButton>
    </div>
  )
}
