import { useEffect, useMemo, useState } from "react"
import {
  createProject,
  createSaga,
  createSponsor,
  diagnostics,
  exportAudiobook,
  exportEbook,
  exportVideo,
  getFactoryCapabilities,
  getSettings,
  listIps,
  listJobs,
  listProjects,
  listPublications,
  listSagas,
  listSponsors,
  listUsers,
  runFactory,
  saveSettings
} from "../api.js"
import IpBrandingEditorPanel from "./IpBrandingEditorPanel.jsx"
import IpCanonsEditorPanel from "./IpCanonsEditorPanel.jsx"
import IpCharactersEditorPanel from "./IpCharactersEditorPanel.jsx"
import IpCoverBuilderPanel from "./IpCoverBuilderPanel.jsx"
import IpCreatorPanel from "./IpCreatorPanel.jsx"
import IpPaletteEditorPanel from "./IpPaletteEditorPanel.jsx"
import OutputsPanel from "./OutputsPanel.jsx"

const DEFAULT_LANGUAGES = ["pt-PT", "pt-BR", "en", "es", "fr", "de", "it", "nl", "zh", "ja"]

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
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>{title}</h3>
      {children}
    </div>
  )
}

function ActionButton({ children, onClick }) {
  return (
    <button
      onClick={onClick}
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
      {children}
    </button>
  )
}

function canEditorial(user) {
  const role = String(user?.role || "").toLowerCase()
  const name = String(user?.name || "").toLowerCase()
  return ["owner", "creator", "admin"].includes(role) || ["andré", "andre", "esposa", "wife", "mama"].includes(name)
}

export default function DashboardPanel({ user }) {
  const [settings, setSettings] = useState(null)
  const [diagnostic, setDiagnostic] = useState(null)
  const [factoryCaps, setFactoryCaps] = useState(null)
  const [users, setUsers] = useState([])
  const [projects, setProjects] = useState([])
  const [ips, setIps] = useState([])
  const [sagas, setSagas] = useState([])
  const [sponsors, setSponsors] = useState([])
  const [jobs, setJobs] = useState([])
  const [publications, setPublications] = useState([])

  const [newProjectTitle, setNewProjectTitle] = useState("")
  const [newProjectIpSlug, setNewProjectIpSlug] = useState("")
  const [newProjectLanguage, setNewProjectLanguage] = useState("pt-PT")

  const [newSagaName, setNewSagaName] = useState("")
  const [newSponsorName, setNewSponsorName] = useState("")

  useEffect(() => {
    loadAll()
  }, [])

  const selectedProjectIp = useMemo(
    () => ips.find((item) => item.slug === newProjectIpSlug) || null,
    [ips, newProjectIpSlug]
  )

  async function loadAll() {
    const [
      settingsRes,
      diagnosticRes,
      factoryRes,
      usersRes,
      projectsRes,
      ipsRes,
      sagasRes,
      sponsorsRes,
      jobsRes,
      publicationsRes
    ] = await Promise.all([
      getSettings(),
      diagnostics(),
      getFactoryCapabilities(),
      listUsers(),
      listProjects(user),
      listIps(user),
      listSagas(),
      listSponsors(),
      listJobs(),
      listPublications()
    ])

    const ipsList = ipsRes?.ips || []

    setSettings(settingsRes || {})
    setDiagnostic(diagnosticRes?.diagnostics || diagnosticRes || null)
    setFactoryCaps(factoryRes?.capabilities || null)
    setUsers(usersRes?.users || [])
    setProjects(projectsRes?.projects || [])
    setIps(ipsList)
    setSagas(sagasRes || [])
    setSponsors(sponsorsRes || [])
    setJobs(jobsRes || [])
    setPublications(publicationsRes?.publications || [])

    if (!newProjectIpSlug && ipsList.length) {
      setNewProjectIpSlug(ipsList[0].slug)
    }
  }

  function handleCoverBuilt(projectId, coverResult) {
    setProjects((current) =>
      current.map((project) =>
        project.id === projectId
          ? {
              ...project,
              cover_image: coverResult?.file_path || project.cover_image,
              outputs: {
                ...(project.outputs || {}),
                covers: coverResult
              }
            }
          : project
      )
    )
  }

  async function handleCreateProject() {
    if (!newProjectTitle.trim()) return
    if (!selectedProjectIp) {
      alert("Seleciona uma IP para o projeto.")
      return
    }

    await createProject({
      title: newProjectTitle,
      saga_slug: selectedProjectIp.slug,
      saga_name: selectedProjectIp.name,
      language: newProjectLanguage,
      output_languages: DEFAULT_LANGUAGES,
      created_by: user?.id || "",
      created_by_name: user?.name || "",
      visible_to_owner_only: true
    })

    setNewProjectTitle("")
    await loadAll()
  }

  async function handleCreateSaga() {
    if (!canEditorial(user)) {
      alert("Sem permissão editorial.")
      return
    }

    if (!newSagaName.trim()) return

    await createSaga({
      slug: newSagaName.toLowerCase().replace(/\s+/g, "-"),
      name: newSagaName,
      exclusive_owner: user?.name || "",
      colors: {
        primary: "#2F5E2E",
        secondary: "#6FA86A",
        gold: "#D4A73C",
        cream: "#F5EED6",
        brown: "#8B5E3C"
      },
      characters_locked: false,
      sponsors: []
    })

    setNewSagaName("")
    await loadAll()
  }

  async function handleCreateSponsor() {
    if (!canEditorial(user)) {
      alert("Sem permissão editorial.")
      return
    }

    if (!newSponsorName.trim()) return

    await createSponsor({
      id: crypto.randomUUID(),
      name: newSponsorName,
      saga_slug: "baribudos"
    })

    setNewSponsorName("")
    await loadAll()
  }

  async function handleFactory(projectId) {
    if (!canEditorial(user)) {
      alert("Sem permissão editorial.")
      return
    }

    await runFactory(projectId, {
      userName: user?.name || "André",
      languages: ["pt-PT", "en"],
      createStory: true,
      createTranslations: true,
      createCover: true,
      createEpub: true,
      createAudiobook: true,
      createSeries: true,
      createGuide: true,
      publish: false,
      age_range: "4-10"
    })
    alert("Factory concluída.")
    await loadAll()
  }

  async function handleExportEpub(projectId) {
    if (!canEditorial(user)) {
      alert("Sem permissão editorial.")
      return
    }
    await exportEbook(projectId, { language: "pt-PT" })
    alert("EPUB exportado.")
    await loadAll()
  }

  async function handleExportAudio(projectId) {
    if (!canEditorial(user)) {
      alert("Sem permissão editorial.")
      return
    }
    await exportAudiobook(projectId, { language: "pt-PT" })
    alert("Audiobook exportado.")
    await loadAll()
  }

  async function handleExportVideo(projectId) {
    if (!canEditorial(user)) {
      alert("Sem permissão editorial.")
      return
    }
    await exportVideo(projectId, { language: "pt-PT" })
    alert("Vídeo exportado.")
    await loadAll()
  }

  async function handleSaveSettings() {
    if (!canEditorial(user)) {
      alert("Sem permissão editorial.")
      return
    }
    await saveSettings(settings || {})
    alert("Settings guardadas.")
    await loadAll()
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <Card title="Sistema">
        <div><strong>App:</strong> {diagnostic?.app_name || "-"}</div>
        <div><strong>Python:</strong> {diagnostic?.system?.python_version || "-"}</div>
        <div><strong>Storage:</strong> {diagnostic?.storage_root || "-"}</div>
        <div><strong>FFmpeg:</strong> {diagnostic?.commands?.ffmpeg?.ok ? "OK" : "FALTA"}</div>
        <div><strong>eSpeak:</strong> {diagnostic?.commands?.espeak?.ok ? "OK" : "FALTA"}</div>
      </Card>

      <Card title="Factory Capabilities">
        <div><strong>Engine:</strong> {factoryCaps?.engine || "-"}</div>
        <div><strong>Línguas:</strong> {(factoryCaps?.supported_languages || []).join(", ")}</div>
      </Card>

      <IpCreatorPanel user={user} />
      <IpPaletteEditorPanel user={user} />
      <IpBrandingEditorPanel user={user} />
      <IpCharactersEditorPanel user={user} />
      <IpCanonsEditorPanel user={user} />
      <IpCoverBuilderPanel user={user} onCoverBuilt={handleCoverBuilt} />
      <OutputsPanel projects={projects} />

      <Card title="Settings">
        <label>Língua default</label>
        <input
          value={settings?.default_language || ""}
          onChange={(e) =>
            setSettings((current) => ({
              ...(current || {}),
              default_language: e.target.value
            }))
          }
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />

        <label>Autor default</label>
        <input
          value={settings?.author_default || ""}
          onChange={(e) =>
            setSettings((current) => ({
              ...(current || {}),
              author_default: e.target.value
            }))
          }
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />

        <ActionButton onClick={handleSaveSettings}>Guardar settings</ActionButton>
      </Card>

      <Card title="Utilizadores">
        {users.map((item) => (
          <div key={item.id}>
            <strong>{item.name}</strong> — {item.role}
          </div>
        ))}
      </Card>

      <Card title="Criar Saga">
        <input
          value={newSagaName}
          onChange={(e) => setNewSagaName(e.target.value)}
          placeholder="Nome da saga"
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />
        <ActionButton onClick={handleCreateSaga}>Criar saga</ActionButton>

        {sagas.map((saga, index) => (
          <div key={saga.id || saga.slug || index}>
            <strong>{saga.name}</strong> ({saga.slug})
          </div>
        ))}
      </Card>

      <Card title="Criar Sponsor">
        <input
          value={newSponsorName}
          onChange={(e) => setNewSponsorName(e.target.value)}
          placeholder="Nome do patrocinador"
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />
        <ActionButton onClick={handleCreateSponsor}>Criar sponsor</ActionButton>

        {sponsors.map((sponsor, index) => (
          <div key={sponsor.id || index}>
            <strong>{sponsor.name}</strong>
          </div>
        ))}
      </Card>

      <Card title="Criar Projeto">
        <label>IP / Saga</label>
        <select
          value={newProjectIpSlug}
          onChange={(e) => setNewProjectIpSlug(e.target.value)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        >
          <option value="">Selecionar IP</option>
          {ips.map((ip) => (
            <option key={ip.id} value={ip.slug}>
              {ip.name}
            </option>
          ))}
        </select>

        <label>Língua base</label>
        <select
          value={newProjectLanguage}
          onChange={(e) => setNewProjectLanguage(e.target.value)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        >
          {DEFAULT_LANGUAGES.map((lang) => (
            <option key={lang} value={lang}>
              {lang}
            </option>
          ))}
        </select>

        <input
          value={newProjectTitle}
          onChange={(e) => setNewProjectTitle(e.target.value)}
          placeholder="Título do projeto"
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />

        {selectedProjectIp ? (
          <div
            style={{
              padding: 12,
              borderRadius: 12,
              border: "1px solid #e5e7eb",
              background: "rgba(255,255,255,0.55)"
            }}
          >
            <div><strong>IP selecionada:</strong> {selectedProjectIp.name}</div>
            <div><strong>Slug:</strong> {selectedProjectIp.slug}</div>
            <div><strong>Privada:</strong> {selectedProjectIp.visible_to_owner_only ? "Sim" : "Não"}</div>
          </div>
        ) : null}

        <ActionButton onClick={handleCreateProject}>Criar projeto</ActionButton>
      </Card>

      <Card title="Projetos visíveis para este user">
        {projects.map((project) => (
          <div
            key={project.id}
            style={{
              border: "1px solid #e5e7eb",
              borderRadius: 12,
              padding: 12,
              display: "grid",
              gap: 8,
              background: "rgba(255,255,255,0.55)"
            }}
          >
            <div><strong>{project.title}</strong></div>
            <div>Saga: {project.saga_name}</div>
            <div>Slug IP: {project.saga_slug}</div>
            <div>Língua: {project.language}</div>
            <div>Dono: {project.created_by_name || "-"}</div>
            <div>Ilustração base: {project.illustration_path || "-"}</div>
            <div>Capa: {project.cover_image || "-"}</div>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <ActionButton onClick={() => handleFactory(project.id)}>Factory</ActionButton>
              <ActionButton onClick={() => handleExportEpub(project.id)}>EPUB</ActionButton>
              <ActionButton onClick={() => handleExportAudio(project.id)}>Audiobook</ActionButton>
              <ActionButton onClick={() => handleExportVideo(project.id)}>Vídeo</ActionButton>
            </div>
          </div>
        ))}
      </Card>

      <Card title="Jobs">
        {jobs.map((job) => (
          <div key={job.id}>
            <strong>{job.type}</strong> — {job.status}
          </div>
        ))}
      </Card>

      <Card title="Publicações">
        {publications.map((item) => (
          <div key={item.id}>
            <strong>{item.project_id}</strong> — {item.language} — {item.channel} — {item.status}
          </div>
        ))}
      </Card>
    </div>
  )
                  }
