import { useEffect, useState } from "react"
import {
  getLocalAudioStatus,
  listProjects,
  runFactory
} from "../api.js"

async function uploadVoiceProfile({ projectId, file, profileName = "", language = "", isDefault = true }) {
  const form = new FormData()
  form.append("project_id", projectId)
  form.append("profile_name", profileName)
  form.append("language", language)
  form.append("is_default", String(isDefault))
  form.append("file", file)

  const response = await fetch(`${window.__BARIBUDOS_API_BASE__ || ""}/api/voice-profiles/upload`, {
    method: "POST",
    body: form
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || "Erro ao carregar sample de voz.")
  }

  return response.json()
}

async function listVoiceProfiles(projectId) {
  const response = await fetch(`${window.__BARIBUDOS_API_BASE__ || ""}/api/voice-profiles/${projectId}`)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || "Erro ao obter perfis de voz.")
  }
  return response.json()
}

async function setDefaultVoiceProfile(projectId, profileId) {
  const response = await fetch(`${window.__BARIBUDOS_API_BASE__ || ""}/api/voice-profiles/default/${projectId}/${profileId}`, {
    method: "POST"
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || "Erro ao definir perfil default.")
  }
  return response.json()
}

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
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [profiles, setProfiles] = useState([])
  const [audioStatus, setAudioStatus] = useState(null)
  const [profileName, setProfileName] = useState("")
  const [language, setLanguage] = useState("pt-PT")

  useEffect(() => {
    loadProjects()
    loadAudioStatus()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadProfiles(selectedProjectId)
    }
  }, [selectedProjectId])

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) {
      setSelectedProjectId(list[0].id)
    }
  }

  async function loadAudioStatus() {
    try {
      const res = await getLocalAudioStatus()
      setAudioStatus(res?.status || null)
    } catch {
      setAudioStatus(null)
    }
  }

  async function loadProfiles(projectId) {
    try {
      const res = await listVoiceProfiles(projectId)
      setProfiles(res?.profiles || [])
    } catch {
      setProfiles([])
    }
  }

  async function handleUpload(file) {
    if (!selectedProjectId || !file) return
    try {
      await uploadVoiceProfile({
        projectId: selectedProjectId,
        file,
        profileName,
        language,
        isDefault: true
      })
      setProfileName("")
      await loadProfiles(selectedProjectId)
      alert("Sample de voz carregada.")
    } catch (error) {
      alert(error?.message || "Erro ao carregar sample de voz.")
    }
  }

  async function handleSetDefault(profileId) {
    if (!selectedProjectId || !profileId) return
    try {
      await setDefaultVoiceProfile(selectedProjectId, profileId)
      await loadProfiles(selectedProjectId)
      alert("Perfil default atualizado.")
    } catch (error) {
      alert(error?.message || "Erro ao atualizar perfil default.")
    }
  }

  async function handleGenerateWithXtts() {
    if (!selectedProjectId) return
    try {
      await runFactory(selectedProjectId, {
        createStory: false,
        createCover: false,
        createEpub: false,
        createAudiobook: true,
        createSeries: false,
        createGuide: false,
        provider: "xtts"
      })
      alert("Audiobook XTTS pedida.")
    } catch (error) {
      alert(error?.message || "Erro ao gerar audiobook com XTTS.")
    }
  }

  return (
    <Card title="Voice Cloning / Voice Profiles">
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

      <div><strong>Provider default áudio:</strong> {audioStatus?.default_provider || "-"}</div>

      <input
        value={profileName}
        onChange={(e) => setProfileName(e.target.value)}
        placeholder="Nome do perfil de voz"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <input
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        placeholder="Idioma"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
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
          accept=".wav,.mp3,.m4a,.flac,.ogg"
          style={{ display: "none" }}
          onChange={(e) => handleUpload(e.target.files?.[0] || null)}
        />
      </label>

      <button
        onClick={handleGenerateWithXtts}
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
        Gerar audiobook com XTTS
      </button>

      <div style={{ display: "grid", gap: 8 }}>
        <strong>Perfis de voz</strong>
        {profiles.map((profile) => (
          <div
            key={profile.id}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: 12,
              padding: 10,
              background: "#fff",
              display: "grid",
              gap: 6
            }}
          >
            <div><strong>{profile.name}</strong></div>
            <div>Idioma: {profile.language || "-"}</div>
            <div>Default: {profile.is_default ? "Sim" : "Não"}</div>
            <div>Ficheiro: {profile.file_path}</div>

            {!profile.is_default ? (
              <button
                onClick={() => handleSetDefault(profile.id)}
                style={{
                  padding: "8px 10px",
                  borderRadius: 10,
                  border: "none",
                  background: "#166534",
                  color: "#fff",
                  cursor: "pointer",
                  width: "fit-content"
                }}
              >
                Definir como default
              </button>
            ) : null}
          </div>
        ))}
      </div>
    </Card>
  )
}
