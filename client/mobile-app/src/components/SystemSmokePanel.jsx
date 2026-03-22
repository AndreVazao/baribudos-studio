import { useEffect, useState } from "react"
import { listProjects, listSystemSmokeResults, runSystemSmoke } from "../api.js"

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

export default function SystemSmokePanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [latestResult, setLatestResult] = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => {
    loadAll()
  }, [])

  async function loadAll() {
    const [projectsRes, smokeRes] = await Promise.all([
      listProjects(user),
      listSystemSmokeResults()
    ])

    const projectList = projectsRes?.projects || []
    const smokeList = smokeRes?.results || []

    setProjects(projectList)
    setHistory(smokeList)

    if (!selectedProjectId && projectList.length) {
      setSelectedProjectId(projectList[0].id)
    }

    if (smokeList.length) {
      setLatestResult(smokeList[smokeList.length - 1])
    }
  }

  async function handleRunSmoke() {
    if (!selectedProjectId) return
    try {
      const res = await runSystemSmoke(selectedProjectId)
      setLatestResult(res?.result || null)
      await loadAll()
      alert("Smoke test concluído.")
    } catch (error) {
      alert(error?.message || "Erro no smoke test.")
    }
  }

  return (
    <Card title="Smoke Test Final">
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
        onClick={handleRunSmoke}
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
        Executar smoke test
      </button>

      {latestResult ? (
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
          <div><strong>Projeto:</strong> {latestResult.project_id}</div>
          <div><strong>Runtime:</strong> {latestResult.runtime_name} ({latestResult.runtime_slug})</div>
          <div><strong>OK:</strong> {latestResult.ok ? "Sim" : "Não"}</div>
          <div><strong>Readiness:</strong> {latestResult.publication_readiness?.status || "-"}</div>
          <div><strong>Integrity OK:</strong> {latestResult.integrity?.integrity_ok ? "Sim" : "Não"}</div>
          <div><strong>Publishability OK:</strong> {latestResult.publishability?.ok ? "Sim" : "Não"}</div>

          <textarea
            readOnly
            value={JSON.stringify(latestResult, null, 2)}
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

      <div style={{ display: "grid", gap: 6 }}>
        <strong>Histórico</strong>
        {history.slice().reverse().slice(0, 5).map((item) => (
          <div key={item.id}>
            {item.created_at} — {item.project_id} — {item.ok ? "OK" : "FAIL"}
          </div>
        ))}
      </div>
    </Card>
  )
  }
