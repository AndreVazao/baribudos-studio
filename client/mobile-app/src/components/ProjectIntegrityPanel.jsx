import { useEffect, useState } from "react"
import { getProjectIntegrity, listProjects, repairProject } from "../api.js"

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

export default function ProjectIntegrityPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [audit, setAudit] = useState(null)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadAudit(selectedProjectId)
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

  async function loadAudit(projectId) {
    try {
      const res = await getProjectIntegrity(projectId)
      setAudit(res?.audit || null)
    } catch (error) {
      alert(error?.message || "Erro ao carregar integridade.")
    }
  }

  async function handleRepair() {
    if (!selectedProjectId) return
    try {
      const res = await repairProject(selectedProjectId, user)
      setAudit(res?.audit || null)
      alert("Projeto reparado/normalizado.")
    } catch (error) {
      alert(error?.message || "Erro ao reparar projeto.")
    }
  }

  return (
    <Card title="Integridade do Projeto">
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

      {audit ? (
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
          <div><strong>Integrity OK:</strong> {audit.integrity_ok ? "Sim" : "Não"}</div>
          <div><strong>Missing files:</strong> {audit.missing_files_count}</div>
          <div><strong>Readiness:</strong> {audit.readiness_status}</div>
          <div><strong>Ready flag:</strong> {audit.ready_for_publish_flag ? "Sim" : "Não"}</div>
          <textarea
            readOnly
            value={JSON.stringify(audit, null, 2)}
            rows={18}
            style={{
              width: "100%",
              padding: 12,
              borderRadius: 12,
              border: "1px solid #d1d5db",
              outline: "none",
              fontFamily: "monospace",
              fontSize: 13,
              resize: "vertical"
            }}
          />
        </div>
      ) : null}

      <button
        onClick={handleRepair}
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
        Reparar / normalizar projeto
      </button>
    </Card>
  )
    }
