import { useEffect, useState } from "react"
import { checkForUpdates, getLocalVersionInfo } from "../api.js"

function Card({ title, children }) {
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
      <h3 style={{ margin: 0 }}>{title}</h3>
      {children}
    </div>
  )
}

export default function UpdaterPanel() {
  const [localVersion, setLocalVersion] = useState(null)
  const [channel, setChannel] = useState("stable")
  const [updateUrl, setUpdateUrl] = useState("")
  const [result, setResult] = useState(null)

  useEffect(() => {
    loadLocal()
  }, [])

  async function loadLocal() {
    try {
      const res = await getLocalVersionInfo()
      const info = res?.version || null
      setLocalVersion(info)
      setChannel(info?.channel || "stable")
    } catch {
      setLocalVersion(null)
    }
  }

  async function handleCheck() {
    try {
      const res = await checkForUpdates({
        channel,
        update_url: updateUrl || undefined
      })
      setResult(res || null)
      if (res?.update_available) {
        alert("Nova versão disponível.")
      } else {
        alert("Sem atualização disponível.")
      }
    } catch (error) {
      alert(error?.message || "Erro ao verificar updates.")
    }
  }

  function handleOpenDownload() {
    const url = String(result?.download_url || "").trim()
    if (!url) {
      alert("Sem link de download.")
      return
    }
    window.open(url, "_blank", "noopener,noreferrer")
  }

  return (
    <Card title="Updater">
      <div><strong>Versão local:</strong> {localVersion?.version || "-"}</div>
      <div><strong>Canal local:</strong> {localVersion?.channel || "-"}</div>

      <label>Canal</label>
      <select
        value={channel}
        onChange={(e) => setChannel(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="stable">stable</option>
        <option value="beta">beta</option>
      </select>

      <label>Update URL remota</label>
      <input
        value={updateUrl}
        onChange={(e) => setUpdateUrl(e.target.value)}
        placeholder="Opcional. Se vazio usa a default."
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={handleCheck}
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
          Verificar updates
        </button>

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
          Abrir download
        </button>
      </div>

      {result ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            border: "1px solid #e5e7eb",
            background: "rgba(255,255,255,0.55)",
            display: "grid",
            gap: 8
          }}
        >
          <div><strong>Plataforma:</strong> {result.platform || "-"}</div>
          <div><strong>Versão remota:</strong> {result?.remote?.version || "-"}</div>
          <div><strong>Update disponível:</strong> {result.update_available ? "Sim" : "Não"}</div>
          <div><strong>Download:</strong> {result.download_url || "-"}</div>
          <div><strong>Notas:</strong> {result?.remote?.notes || "-"}</div>
        </div>
      ) : null}
    </Card>
  )
}
