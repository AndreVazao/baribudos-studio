import { useEffect, useState } from "react"
import { getLocalAiStatus, setLocalAiDefaultProvider, setupLocalAi } from "../api.js"

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

export default function LocalAiInstallerPanel() {
  const [status, setStatus] = useState(null)
  const [installRoot, setInstallRoot] = useState("")
  const [defaultProvider, setDefaultProviderState] = useState("stable_diffusion")

  useEffect(() => {
    loadStatus()
  }, [])

  async function loadStatus() {
    try {
      const res = await getLocalAiStatus()
      const nextStatus = res?.status || null
      setStatus(nextStatus)
      setDefaultProviderState(nextStatus?.default_provider || "stable_diffusion")
      setInstallRoot(nextStatus?.paths?.root || "")
    } catch {
      setStatus(null)
    }
  }

  async function handleSetup() {
    try {
      await setupLocalAi({
        install_root: installRoot || undefined
      })
      await loadStatus()
      alert("Local AI configurada. Agora executa o script de setup no PC.")
    } catch (error) {
      alert(error?.message || "Erro ao configurar Local AI.")
    }
  }

  async function handleSetProvider() {
    try {
      await setLocalAiDefaultProvider(defaultProvider)
      await loadStatus()
      alert("Provider default atualizada.")
    } catch (error) {
      alert(error?.message || "Erro ao atualizar provider default.")
    }
  }

  return (
    <Card title="Local AI Installer">
      <label>Pasta de instalação</label>
      <input
        value={installRoot}
        onChange={(e) => setInstallRoot(e.target.value)}
        placeholder="Deixa vazio para default"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={handleSetup}
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
          Preparar instalação local
        </button>
      </div>

      <label>Provider default</label>
      <select
        value={defaultProvider}
        onChange={(e) => setDefaultProviderState(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="stable_diffusion">Stable Diffusion / ComfyUI</option>
        <option value="automatic1111">Automatic1111</option>
        <option value="local_basic">Local basic</option>
        <option value="openai">Cloud OpenAI</option>
      </select>

      <button
        onClick={handleSetProvider}
        style={{
          padding: "10px 12px",
          borderRadius: 12,
          border: "none",
          background: "#7c3aed",
          color: "#fff",
          fontWeight: 700,
          cursor: "pointer"
        }}
      >
        Guardar provider default
      </button>

      {status ? (
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
          <div><strong>OS:</strong> {status.os || "-"}</div>
          <div><strong>Default provider:</strong> {status.default_provider || "-"}</div>
          <div><strong>Python encontrado:</strong> {status.requirements?.python ? "Sim" : "Não"}</div>
          <div><strong>Git encontrado:</strong> {status.requirements?.git ? "Sim" : "Não"}</div>
          <div><strong>Root:</strong> {status.paths?.root || "-"}</div>
          <div><strong>ComfyUI:</strong> {status.paths?.comfyui_root || "-"}</div>
          <div><strong>Automatic1111:</strong> {status.paths?.automatic1111_root || "-"}</div>
          <div><strong>Models:</strong> {status.paths?.models_root || "-"}</div>

          <textarea
            readOnly
            value={JSON.stringify(status, null, 2)}
            rows={14}
            style={{
              width: "100%",
              padding: 12,
              borderRadius: 12,
              border: "1px solid #d1d5db",
              outline: "none",
              fontFamily: "monospace",
              fontSize: 12,
              resize: "vertical"
            }}
          />
        </div>
      ) : null}
    </Card>
  )
}
