import { useEffect, useState } from "react"
import {
  ensureLocalAudioProvider,
  getLocalAudioEngineManagerStatus,
  getLocalAudioStatus,
  setLocalAudioDefaultProvider,
  setupLocalAudio,
  stopLocalAudioProvider
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

export default function LocalAudioInstallerPanel() {
  const [status, setStatus] = useState(null)
  const [manager, setManager] = useState(null)
  const [installRoot, setInstallRoot] = useState("")
  const [defaultProvider, setDefaultProviderState] = useState("system_tts")

  useEffect(() => {
    loadAll()
  }, [])

  async function loadAll() {
    try {
      const [statusRes, managerRes] = await Promise.all([
        getLocalAudioStatus(),
        getLocalAudioEngineManagerStatus()
      ])

      const nextStatus = statusRes?.status || null
      setStatus(nextStatus)
      setManager(managerRes?.status || null)
      setInstallRoot(nextStatus?.paths?.root || "")
      setDefaultProviderState(nextStatus?.default_provider || "system_tts")
    } catch {
      setStatus(null)
      setManager(null)
    }
  }

  async function handleSetup() {
    try {
      await setupLocalAudio({
        install_root: installRoot || undefined
      })
      await loadAll()
      alert("Local Audio configurado.")
    } catch (error) {
      alert(error?.message || "Erro ao configurar Local Audio.")
    }
  }

  async function handleDefaultProvider() {
    try {
      await setLocalAudioDefaultProvider(defaultProvider)
      await loadAll()
      alert("Provider default de áudio guardada.")
    } catch (error) {
      alert(error?.message || "Erro ao guardar provider de áudio.")
    }
  }

  async function handleEnsure(provider) {
    try {
      await ensureLocalAudioProvider(provider)
      await loadAll()
      alert(`Provider de áudio ${provider} pronta ou já ativa.`)
    } catch (error) {
      alert(error?.message || `Erro ao garantir ${provider}.`)
    }
  }

  async function handleStop(provider) {
    try {
      await stopLocalAudioProvider(provider)
      await loadAll()
      alert(`Provider de áudio ${provider} parada.`)
    } catch (error) {
      alert(error?.message || `Erro ao parar ${provider}.`)
    }
  }

  return (
    <Card title="Local Audio Installer">
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
        Preparar áudio local
      </button>

      <label>Provider default</label>
      <select
        value={defaultProvider}
        onChange={(e) => setDefaultProviderState(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="system_tts">System TTS</option>
        <option value="coqui_tts">Coqui TTS</option>
        <option value="xtts">XTTS / clonagem</option>
      </select>

      <button
        onClick={handleDefaultProvider}
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
        Guardar provider áudio
      </button>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={() => handleEnsure("coqui_tts")}
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
          Garantir Coqui TTS
        </button>

        <button
          onClick={() => handleEnsure("xtts")}
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
          Garantir XTTS
        </button>

        <button
          onClick={() => handleStop("coqui_tts")}
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
          Parar Coqui
        </button>

        <button
          onClick={() => handleStop("xtts")}
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
          Parar XTTS
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
          <div><strong>Default provider:</strong> {status.default_provider || "-"}</div>
          <div><strong>Python encontrado:</strong> {status.requirements?.python ? "Sim" : "Não"}</div>
          <div><strong>Root:</strong> {status.paths?.root || "-"}</div>
          <div><strong>Voices:</strong> {status.paths?.voices_root || "-"}</div>
          <div><strong>Models:</strong> {status.paths?.models_root || "-"}</div>
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
          <div><strong>System TTS:</strong> {manager?.providers?.system_tts?.running ? "Disponível" : "Não"}</div>
          <div><strong>Coqui:</strong> {manager?.providers?.coqui_tts?.running ? "Ativo" : "Inativo"}</div>
          <div><strong>XTTS:</strong> {manager?.providers?.xtts?.running ? "Ativo" : "Inativo"}</div>

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
