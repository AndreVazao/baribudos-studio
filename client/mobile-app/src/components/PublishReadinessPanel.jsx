import { useEffect, useState } from "react"
import {
  getPublishReadiness,
  listProjects,
  markProjectReady,
  unmarkProjectReady
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

function statusColors(status) {
  if (status === "green") {
    return { bg: "#dcfce7", border: "#16a34a", text: "#166534" }
  }
  if (status === "yellow") {
    return { bg: "#fef9c3", border: "#ca8a04", text: "#854d0e" }
  }
  return { bg: "#fee2e2", border: "#dc2626", text: "#991b1b" }
}

export default function PublishReadinessPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [readiness, setReadiness] = useState(null)
  const [readyForPublish, setReadyForPublish] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadReadiness(selectedProjectId)
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

  async function loadReadiness(projectId) {
    try {
      const res = await getPublishReadiness(projectId)
      setReadiness(res?.readiness || null)
      setReadyForPublish(Boolean(res?.ready_for_publish))
    } catch (error) {
      alert(error?.message || "Erro ao carregar checklist final.")
    }
  }

  async function handleMarkReady() {
    if (!selectedProjectId) return
    try {
      await markProjectReady(selectedProjectId, user)
      alert("Projeto marcado como pronto para publicar.")
      await loadReadiness(selectedProjectId)
    } catch (error) {
      alert(error?.message || "Erro ao marcar como pronto.")
    }
  }

  async function handleUnmarkReady() {
    if (!selectedProjectId) return
    try {
      await unmarkProjectReady(selectedProjectId, user)
      alert("Projeto removido de pronto para publicar.")
      await loadReadiness(selectedProjectId)
    } catch (error) {
      alert(error?.message || "Erro ao remover prontidão.")
    }
  }

  const palette = statusColors(readiness?.status)

  return (
    <Card title="Checklist Final Automática">
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

      {readiness ? (
        <div
          style={{
            padding: 14,
            borderRadius: 14,
            border: `2px solid ${palette.border}`,
            background: palette.bg,
            color: palette.text,
            display: "grid",
            gap: 8
          }}
        >
          <div><strong>Semáforo:</strong> {readiness.label}</div>
          <div><strong>Estado:</strong> {readiness.status}</div>
          <div><strong>Score:</strong> {readiness.score_percent}%</div>
          <div><strong>Ready:</strong> {readiness.ready ? "Sim" : "Não"}</div>
          <div><strong>Marcado como pronto:</strong> {readyForPublish ? "Sim" : "Não"}</div>
          <div><strong>Campos obrigatórios em falta:</strong> {(readiness.missing_required_fields || []).join(", ") || "-"}</div>
          <div><strong>Outputs obrigatórios em falta:</strong> {(readiness.missing_required_outputs || []).join(", ") || "-"}</div>
          <div><strong>Campos recomendados em falta:</strong> {(readiness.missing_recommended_fields || []).join(", ") || "-"}</div>
        </div>
      ) : null}

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={handleMarkReady}
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
          Marcar pronto para publicar
        </button>

        <button
          onClick={handleUnmarkReady}
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
          Remover prontidão
        </button>
      </div>
    </Card>
  )
  }
