import { useEffect, useMemo, useState } from "react"
import { buildCover, listIps, listProjects, uploadIllustrationForCover } from "../api.js"

const LANGUAGES = [
  { value: "pt-PT", label: "Português (PT-PT)" },
  { value: "pt-BR", label: "Português (PT-BR)" },
  { value: "en", label: "English" },
  { value: "es", label: "Español" },
  { value: "fr", label: "Français" },
  { value: "de", label: "Deutsch" },
  { value: "it", label: "Italiano" },
  { value: "nl", label: "Nederlands" },
  { value: "zh", label: "中文" },
  { value: "ja", label: "日本語" }
]

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

function readFileAsObjectUrl(file) {
  return URL.createObjectURL(file)
}

export default function IpCoverBuilderPanel({ user, onCoverBuilt }) {
  const [ips, setIps] = useState([])
  const [projects, setProjects] = useState([])
  const [selectedIp, setSelectedIp] = useState("")
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [title, setTitle] = useState("")
  const [language, setLanguage] = useState("pt-PT")
  const [ageRange, setAgeRange] = useState("4-10")
  const [illustrationPath, setIllustrationPath] = useState("")
  const [illustrationPreview, setIllustrationPreview] = useState("")
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    const [ipsRes, projectsRes] = await Promise.all([
      listIps(user),
      listProjects(user)
    ])

    const ipList = ipsRes?.ips || []
    const projectList = projectsRes?.projects || []

    setIps(ipList)
    setProjects(projectList)

    if (ipList.length && !selectedIp) {
      setSelectedIp(ipList[0].slug)
    }

    if (projectList.length && !selectedProjectId) {
      const first = projectList[0]
      setSelectedProjectId(first.id)
      setTitle(first.title || "")
      setSelectedIp(first.saga_slug || ipList[0]?.slug || "")
      setLanguage(first.language || "pt-PT")
    }
  }

  const filteredProjects = useMemo(() => {
    if (!selectedIp) return projects
    return projects.filter((item) => String(item.saga_slug || "") === String(selectedIp))
  }, [projects, selectedIp])

  function handleProjectChange(projectId) {
    setSelectedProjectId(projectId)
    const project = projects.find((item) => item.id === projectId)
    if (project) {
      setTitle(project.title || "")
      setSelectedIp(project.saga_slug || selectedIp)
      setLanguage(project.language || "pt-PT")
    }
  }

  async function handleIllustrationFile(file) {
    if (!file || !selectedIp || !selectedProjectId) {
      alert("Seleciona primeiro a IP e o projeto.")
      return
    }

    const preview = readFileAsObjectUrl(file)
    setIllustrationPreview(preview)

    try {
      setUploading(true)
      const res = await uploadIllustrationForCover({
        sagaId: selectedIp,
        projectId: selectedProjectId,
        file
      })
      const uploadedPath = res?.result?.file_path || ""
      setIllustrationPath(uploadedPath)
    } catch (error) {
      alert(error?.message || "Erro no upload da ilustração.")
    } finally {
      setUploading(false)
    }
  }

  async function handleBuild() {
    if (!selectedIp || !selectedProjectId || !title.trim() || !illustrationPath.trim()) {
      alert("Preenche IP, projeto, título e ilustração.")
      return
    }

    try {
      const res = await buildCover({
        saga_id: selectedIp,
        project_id: selectedProjectId,
        title,
        age_range: ageRange,
        language,
        illustration_path: illustrationPath,
        output_name: `${title.toLowerCase().replace(/[^a-z0-9]+/gi, "_")}_cover.png`
      })
      const built = res?.result || null
      setResult(built)
      onCoverBuilt?.(selectedProjectId, built)
      alert("Capa gerada com sucesso.")
    } catch (error) {
      alert(error?.message || "Erro ao gerar capa.")
    }
  }

  return (
    <Card title="Gerador de Capas por IP">
      <label>IP / Saga</label>
      <select
        value={selectedIp}
        onChange={(e) => setSelectedIp(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="">Selecionar IP</option>
        {ips.map((item) => (
          <option key={item.id} value={item.slug}>
            {item.name}
          </option>
        ))}
      </select>

      <label>Projeto</label>
      <select
        value={selectedProjectId}
        onChange={(e) => handleProjectChange(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="">Selecionar projeto</option>
        {filteredProjects.map((item) => (
          <option key={item.id} value={item.id}>
            {item.title}
          </option>
        ))}
      </select>

      <label>Título da capa</label>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Título do livro"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Língua</label>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        {LANGUAGES.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>

      <label>Faixa etária</label>
      <input
        value={ageRange}
        onChange={(e) => setAgeRange(e.target.value)}
        placeholder="Ex.: 4-10"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Ilustração base</label>
      <input
        type="file"
        accept=".png,.jpg,.jpeg,.webp"
        onChange={(e) => handleIllustrationFile(e.target.files?.[0])}
      />

      {uploading ? <div>A fazer upload da ilustração...</div> : null}

      {illustrationPreview ? (
        <img
          src={illustrationPreview}
          alt="Preview ilustração"
          style={{ maxWidth: "100%", borderRadius: 12, border: "1px solid #e5e7eb" }}
        />
      ) : null}

      <label>Caminho da ilustração carregada</label>
      <input
        value={illustrationPath}
        onChange={(e) => setIllustrationPath(e.target.value)}
        placeholder="Será preenchido após upload"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <button
        onClick={handleBuild}
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
        Gerar capa final
      </button>

      {result ? (
        <div
          style={{
            display: "grid",
            gap: 8,
            padding: 12,
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            background: "rgba(255,255,255,0.55)"
          }}
        >
          <strong>Resultado</strong>
          <div><strong>Ficheiro:</strong> {result.file_name}</div>
          <div><strong>Capa:</strong> {result.file_path}</div>
          <div><strong>Badge:</strong> {result.badge_file_path}</div>
        </div>
      ) : null}
    </Card>
  )
  }
