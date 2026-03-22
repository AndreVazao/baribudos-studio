import { useEffect, useState } from "react"
import {
  exportAudiobook,
  generateVoicePreview,
  listProjects,
  listVoiceSamples,
  uploadVoiceSample
} from "../api.js"
import { normalizeMediaUrl } from "../utils/media.js"

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

export default function VoiceCloningPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [voices, setVoices] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [selectedVoiceId, setSelectedVoiceId] = useState("")
  const [provider, setProvider] = useState("xtts")
  const [voiceName, setVoiceName] = useState("")
  const [voiceLanguage, setVoiceLanguage] = useState("pt-PT")
  const [voiceNotes, setVoiceNotes] = useState("")
  const [previewText, setPreviewText] = useState("Olá. Este é um teste de voz do Baribudos Studio.")
  const [previewResult, setPreviewResult] = useState(null)

  useEffect(() => {
    loadAll()
  }, [])

  async function loadAll() {
    const [projectsRes, voicesRes] = await Promise.all([
      listProjects(user),
      listVoiceSamples()
    ])

    const projectList = projectsRes?.projects || []
    const voiceList = voicesRes?.voices || []

    setProjects(projectList)
    setVoices(voiceList)

    if (!selectedProjectId && projectList.length) {
      setSelectedProjectId(projectList[0].id)
    }

    if (!selectedVoiceId && voiceList.length) {
      setSelectedVoiceId(voiceList[0].id)
    }
  }

  async function handleVoiceUpload(file) {
    if (!file) return
    try {
      await uploadVoiceSample({
        name: voiceName || "Nova voz",
        language: voiceLanguage,
        notes: voiceNotes,
        file
      })
      setVoiceName("")
      setVoiceNotes("")
      await loadAll()
      alert("Voice sample carregada.")
    } catch (error) {
      alert(error?.message || "Erro ao carregar voice sample.")
    }
  }

  async function handlePreview() {
    try {
      const res = await generateVoicePreview({
        provider,
        text: previewText,
        language: voiceLanguage,
        voice_sample_id: selectedVoiceId || "",
      })
      setPreviewResult(res?.preview || null)
      alert("Preview de voz gerado.")
    } catch (error) {
      alert(error?.message || "Erro ao gerar preview.")
    }
  }

  async function handleGenerateAudiobook() {
    if (!selectedProjectId) return
    try {
      await exportAudiobook(selectedProjectId, {
        provider,
        voice_sample_id: selectedVoiceId || "",
      })
      alert("Audiobook gerado com configuração de voz.")
    } catch (error) {
      alert(error?.message || "Erro ao gerar audiobook.")
    }
  }

  const previewUrl = normalizeMediaUrl(previewResult?.file_path)

  return (
    <Card title="Voice Cloning / Voice Library">
      <label>Projeto</label>
      <select
        value={selectedProjectId}
        onChange={(e) => setSelectedProjectId(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="">Selecionar projeto</option>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>
            {project.title} — {project.saga_name}
          </option>
        ))}
      </select>

      <label>Provider áudio</label>
      <select
        value={provider}
        onChange={(e) => setProvider(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="system_tts">System TTS</option>
        <option value="coqui_tts">Coqui TTS</option>
        <option value="xtts">XTTS / clonagem</option>
      </select>

      <label>Voice sample</label>
      <select
        value={selectedVoiceId}
        onChange={(e) => setSelectedVoiceId(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="">Sem voice sample</option>
        {voices.map((voice) => (
          <option key={voice.id} value={voice.id}>
            {voice.name} {voice.language ? `— ${voice.language}` : ""}
          </option>
        ))}
      </select>

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
        <strong>Adicionar nova voice sample</strong>

        <input
          value={voiceName}
          onChange={(e) => setVoiceName(e.target.value)}
          placeholder="Nome da voz"
          style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}
        />

        <input
          value={voiceLanguage}
          onChange={(e) => setVoiceLanguage(e.target.value)}
          placeholder="Língua"
          style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}
        />

        <textarea
          value={voiceNotes}
          onChange={(e) => setVoiceNotes(e.target.value)}
          placeholder="Notas"
          rows={3}
          style={{
            width: "100%",
            padding: 10,
            borderRadius: 10,
            border: "1px solid #d1d5db",
            outline: "none",
            resize: "vertical"
          }}
        />

        <label
          style={{
            padding: "10px 12px",
            borderRadius: 12,
            background: "#1d4ed8",
            color: "#fff",
            cursor: "pointer",
            display: "inline-block",
            width: "fit-content"
          }}
        >
          Carregar sample de voz
          <input
            type="file"
            accept="audio/*"
            style={{ display: "none" }}
            onChange={(e) => handleVoiceUpload(e.target.files?.[0] || null)}
          />
        </label>
      </div>

      <label>Texto de preview</label>
      <textarea
        value={previewText}
        onChange={(e) => setPreviewText(e.target.value)}
        rows={4}
        style={{
          width: "100%",
          padding: 10,
          borderRadius: 10,
          border: "1px solid #d1d5db",
          outline: "none",
          resize: "vertical"
        }}
      />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={handlePreview}
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
          Gerar preview de voz
        </button>

        <button
          onClick={handleGenerateAudiobook}
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
          Gerar audiobook com voz
        </button>
      </div>

      {previewResult ? (
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
          <div><strong>Provider:</strong> {previewResult.provider}</div>
          <div><strong>Ficheiro:</strong> {previewResult.file_path}</div>
          <div><strong>Fallback:</strong> {previewResult.fallback_used ? "Sim" : "Não"}</div>
          {previewUrl ? <audio controls src={previewUrl} style={{ width: "100%" }} /> : null}
        </div>
      ) : null}

      <div
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #e5e7eb",
          background: "rgba(255,255,255,0.55)",
          display: "grid",
          gap: 6
        }}
      >
        <strong>Biblioteca de vozes</strong>
        {voices.map((voice) => (
          <div key={voice.id}>
            {voice.name} — {voice.language || "-"} — {voice.file_path}
          </div>
        ))}
      </div>
    </Card>
  )
  }
