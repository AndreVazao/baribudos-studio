import { useEffect, useState } from "react"
import { getV1Readiness, listProjects } from "../api.js"

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

export default function V1ReadinessPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [result, setResult] = useState(null)

  useEffect(() => {
    loadProjects()
  }, [])

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) {
      setSelectedProjectId(list[0].id)
    }
  }

  async function handleCheck() {
    if (!selectedProjectId) return
    try {
      const res = await getV1Readiness(selectedProjectId)
      setResult(res || null)
    } catch (error) {
      alert(error?.message || "Erro ao validar prontidão v1.")
    }
  }

  return (
    <Card title="V1 Readiness">
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

      <button
        onClick={handleCheck}
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
        Validar v1
      </button>

      {result ? (
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
          <div><strong>Projeto:</strong> {result.project_title || "-"}</div>
          <div><strong>Status:</strong> {result.status}</div>
          <div><strong>Score:</strong> {result.score?.passed || 0}/{result.score?.total || 0}</div>

          {(result.checks || []).map((check) => (
            <div key={check.key}>
              {check.ok ? "✅" : "❌"} {check.label}
              {typeof check.count !== "undefined" ? ` (${check.count})` : ""}
            </div>
          ))}
        </div>
      ) : null}
    </Card>
  )
    }
