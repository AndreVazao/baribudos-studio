import { useState } from "react"
import { getApiBase, healthCheck, setApiBase } from "../api.js"

export default function PcConnectionPanel({ onConnected }) {
  const [value, setValue] = useState(getApiBase())
  const [status, setStatus] = useState("")
  const [busy, setBusy] = useState(false)

  async function handleConnect() {
    try {
      setBusy(true)
      setStatus("A testar ligação...")
      const normalized = setApiBase(value)
      const health = await healthCheck(normalized)
      setStatus(`Ligado a ${normalized}`)
      onConnected?.(normalized, health)
    } catch (error) {
      setStatus(error?.message || "Falha ao ligar ao PC.")
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
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>Ligação ao PC</h3>

      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ex.: 192.168.1.50:8787 ou localhost:8787"
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none"
        }}
      />

      <button
        onClick={handleConnect}
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
        {busy ? "A ligar..." : "Ligar ao backend Python"}
      </button>

      {status ? (
        <div
          style={{
            background: "#f7f7f7",
            border: "1px solid #eee",
            borderRadius: 12,
            padding: 12,
            color: "#374151"
          }}
        >
          {status}
        </div>
      ) : null}
    </div>
  )
  }
