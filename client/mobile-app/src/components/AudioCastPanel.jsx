import { useEffect, useState } from "react"
import {
  getAudioCast,
  listProjects,
  listVoiceSamples,
  previewAudioCast,
  saveAudioCast
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

export default function AudioCastPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [voices, setVoices] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [characterNames, setCharacterNames] = useState([])
  const [narratorVoiceId, setNarratorVoiceId] = useState("")
  const [rows, setRows] = useState([])
  const [previewText, setPreviewText] = useState("Olá. Este é um teste de personagem.")
  const [previewProvider, setPreviewProvider] = useState("xtts")
  const [previewResult, setPreviewResult] = useState(null)

  useEffect(() => {
    loadProjectsAndVoices()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadCast(selectedProjectId)
    }
  }, [selectedProjectId])

  async function loadProjectsAndVoices() {
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
  }

  async function loadCast(projectId) {
    try {
      const res = await getAudioCast(projectId)
      const cast = res?.audio_cast || {}
      const names = res?.character_names || []

      setCharacterNames(names)
      setNarratorVoiceId(cast?.narrator?.voice_sample_id || "")
      setRows(
        names.map((name) => {
          const found = (cast?.characters || []).find((item) => item.name === name)
          return {
            name,
            voice_sample_id: found?.voice_sample_id || "",
            provider: found?.provider || "xtts",
            notes: found?.notes || ""
          }
        })
      )
    } catch {
      setCharacterNames([])
      setNarratorVoiceId("")
      setRows([])
    }
  }

  function updateRow(index, patch) {
    setRows((current) =>
      current.map((row, i) => (i === index ? { ...row, ...patch } : row))
    )
  }

  async function handleSave() {
    if (!selectedProjectId) return
    try {
      await saveAudioCast(selectedProjectId, {
        narrator: {
          voice_sample_id: narratorVoiceId,
          provider: "xtts"
        },
        characters: rows
      })
      alert("Casting de vozes guardado.")
    } catch (error) {
      alert(error?.message || "Erro ao guardar casting.")
    }
  }

  async function handlePreview(characterName) {
    if (!selectedProjectId) return
    try {
      const res = await previewAudioCast(selectedProjectId, {
        character_name: characterName,
        provider: previewProvider,
        text: previewText || `Olá. Este é um teste da personagem ${characterName}.`
      })
      setPreviewResult(res?.preview || null)
      alert(`Preview de ${characterName} gerado.`)
    } catch (error) {
      alert(error?.message || "Erro ao gerar preview da personagem.")
    }
  }

  const previewUrl = normalizeMediaUrl(previewResult?.file_path)

  return (
    <Card title="Audio Cast por Personagem">
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

      <label>Provider preview</label>
      <select
        value={previewProvider}
        onChange={(e) => setPreviewProvider(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="system_tts">System TTS</option>
        <option value="coqui_tts">Coqui TTS</option>
        <option value="xtts">XTTS</option>
      </select>

      <label>Texto de preview</label>
      <textarea
        value={previewText}
        onChange={(e) => setPreviewText(e.target.value)}
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

      <label>Voz do narrador</label>
      <select
        value={narratorVoiceId}
        onChange={(e) => setNarratorVoiceId(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="">Sem voz fixa</option>
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
          gap: 10
        }}
      >
        <strong>Personagens detetadas</strong>

        {rows.map((row, index) => (
          <div
            key={`${row.name}-${index}`}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: 12,
              padding: 10,
              display: "grid",
              gap: 8,
              background: "#fff"
            }}
          >
            <div><strong>{row.name}</strong></div>

            <select
              value={row.voice_sample_id}
              onChange={(e) => updateRow(index, { voice_sample_id: e.target.value })}
              style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}
            >
              <option value="">Usar narrador/default</option>
              {voices.map((voice) => (
                <option key={voice.id} value={voice.id}>
                  {voice.name} {voice.language ? `— ${voice.language}` : ""}
                </option>
              ))}
            </select>

            <textarea
              value={row.notes || ""}
              onChange={(e) => updateRow(index, { notes: e.target.value })}
              rows={2}
              placeholder="Notas"
              style={{
                width: "100%",
                padding: 10,
                borderRadius: 10,
                border: "1px solid #d1d5db",
                outline: "none",
                resize: "vertical"
              }}
            />

            <button
              onClick={() => handlePreview(row.name)}
              style={{
                padding: "8px 10px",
                borderRadius: 10,
                border: "none",
                background: "#0369a1",
                color: "#fff",
                cursor: "pointer"
              }}
            >
              Ouvir preview
            </button>
          </div>
        ))}

        {!rows.length ? <div>Sem personagens detetadas ainda.</div> : null}
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={() => handlePreview("Narrador")}
          style={{
            padding: "10px 12px",
            borderRadius: 12,
            border: "none",
            background: "#0f766e",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          Ouvir narrador
        </button>

        <button
          onClick={handleSave}
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
          Guardar casting
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
          <div><strong>Preview:</strong> {previewResult.provider}</div>
          <div><strong>Ficheiro:</strong> {previewResult.file_path}</div>
          {previewUrl ? <audio controls src={previewUrl} style={{ width: "100%" }} /> : null}
        </div>
      ) : null}
    </Card>
  )
}
