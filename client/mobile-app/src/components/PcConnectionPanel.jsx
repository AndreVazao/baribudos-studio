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
        border: "1px solid #ddd",
        borderRadius: 12,
        background: "#fff",
        padding: 16,
        display: "grid",
        gap: 12
      }}
    >
      <h3 style={{ margin: 0 }}>Ligação ao PC</h3>

      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ex.: 192.168.1.50:8787 ou localhost:8787"
      />

      <button onClick={handleConnect} disabled={busy}>
        {busy ? "A ligar..." : "Ligar ao backend Python"}
      </button>

      {status ? (
        <div
          style={{
            background: "#f7f7f7",
            border: "1px solid #eee",
            borderRadius: 10,
            padding: 12
          }}
        >
          {status}
        </div>
      ) : null}
    </div>
  )
        }
