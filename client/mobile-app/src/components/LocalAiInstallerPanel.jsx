import { useEffect, useState } from "react"
import {
  ensureLocalProvider,
  getLocalAiRuntimeStatus,
  getLocalEngineManagerStatus,
  setLocalAiDefaultProvider,
  setupLocalAi,
  stopLocalProvider
} from "../api.js"

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
  const [runtime, setRuntime] = useState(null)
  const [manager, setManager] = useState(null)
  const [installRoot, setInstallRoot] = useState("")
  const [defaultProvider, setDefaultProviderState] = useState("stable_diffusion")

  useEffect(() => {
    loadAll()
  }, [])

  async function loadAll() {
    try {
      const [runtimeRes, managerRes] = await Promise.all([
        getLocalAiRuntimeStatus(),
        getLocalEngineManagerStatus()
      ])

      const nextRuntime = runtimeRes?.runtime || runtimeRes || null
      const nextManager = managerRes?.status || managerRes || null

      setRuntime(nextRuntime)
      setManager(nextManager)
      setStatus({
        os: nextManager?.os || runtimeRes?.os || "-",
        default_provider: nextManager?.default_provider || "stable_diffusion",
        requirements: {
          python: true,
          git: true
        },
        paths: {
          root: nextManager?.root_path || ""
        }
      })
      setDefaultProviderState(nextManager?.default_provider || "stable_diffusion")
      setInstallRoot(nextManager?.root_path || "")
    } catch {
      setStatus(null)
      setRuntime(null)
      setManager(null)
    }
  }

  async function handleSetup() {
    try {
      await setupLocalAi({
        install_root: installRoot || undefined
      })
      await loadAll()
      alert("Local AI configurada.")
    } catch (error) {
      alert(error?.message || "Erro ao configurar Local AI.")
    }
  }

  async function handleSetProvider() {
    try {
      await setLocalAiDefaultProvider(defaultProvider)
      await loadAll()
      alert("Provider default atualizada.")
    } catch (error) {
      alert(error?.message || "Erro ao atualizar provider default.")
    }
  }

  async function handleEnsure(provider) {
    try {
      await ensureLocalProvider(provider)
      await loadAll()
      alert(`Provider ${provider} pronta ou já ativa.`)
    } catch (error) {
      alert(error?.message || `Erro ao garantir provider ${provider}.`)
    }
  }

  async function handleStop(provider) {
    try {
      await stopLocalProvider(provider)
      await loadAll()
      alert(`Provider ${provider} parada.`)
    } catch (error) {
      alert(error?.message || `Erro ao parar provider ${provider}.`)
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

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={() => handleEnsure("stable_diffusion")}
          style={{
            padding: "10px 12px",
            borderRadius: 12,
            border: "none",
            background: "#b45309",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          Garantir ComfyUI
        </button>

        <button
          onClick={() => handleEnsure("automatic1111")}
          style={{
            padding: "10px 12px",
            borderRadius: 12,
            border: "none",
            background: "#0369a1",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          Garantir Automatic1111
        </button>

        <button
          onClick={() => handleStop("stable_diffusion")}
          style={{
            padding: "10px 12px",
            borderRadius: 12,
            border: "none",
            background: "#991b1b",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          Parar ComfyUI
        </button>

        <button
          onClick={() => handleStop("automatic1111")}
          style={{
            padding: "10px 12px",
            borderRadius: 12,
            border: "none",
            background: "#7f1d1d",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          Parar Automatic1111
        </button>
      </div>

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
        </div>
      ) : null}

      {runtime ? (
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
          <div><strong>ComfyUI ativo:</strong> {runtime?.comfyui?.ok ? "Sim" : "Não"}</div>
          <div><strong>Automatic1111 ativo:</strong> {runtime?.automatic1111?.ok ? "Sim" : "Não"}</div>
        </div>
      ) : null}

      {manager ? (
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
          <div><strong>Manager default:</strong> {manager.default_provider || "-"}</div>
          <div><strong>ComfyUI running:</strong> {manager?.providers?.stable_diffusion?.running ? "Sim" : "Não"}</div>
          <div><strong>Automatic1111 running:</strong> {manager?.providers?.automatic1111?.running ? "Sim" : "Não"}</div>

          <textarea
            readOnly
            value={JSON.stringify(manager, null, 2)}
            rows={12}
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
