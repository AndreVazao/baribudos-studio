import { useEffect, useState } from "react"
import { freezePublicationPackage, getPublicationPackage, listProjects } from "../api.js"

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

export default function PublicationPackagePanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [pkg, setPkg] = useState(null)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadPackage(selectedProjectId)
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

  async function loadPackage(projectId) {
    try {
      const res = await getPublicationPackage(projectId)
      setPkg(res?.package || null)
    } catch (error) {
      alert(error?.message || "Erro ao carregar pacote final.")
    }
  }

  async function handleFreeze() {
    if (!selectedProjectId) return

    try {
      const res = await freezePublicationPackage(selectedProjectId, user)
      setPkg(res?.publication_package || null)
      alert("Pacote final congelado.")
    } catch (error) {
      alert(error?.message || "Erro ao congelar pacote.")
    }
  }

  return (
    <Card title="Pacote Final de Publicação">
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
        onClick={handleFreeze}
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
        Congelar pacote final
      </button>

      {pkg ? (
        <div style={{ display: "grid", gap: 12 }}>
          <div
            style={{
              padding: 12,
              borderRadius: 12,
              border: "1px solid #e5e7eb",
              background: "rgba(255,255,255,0.55)"
            }}
          >
            <div><strong>Projeto:</strong> {pkg?.project?.title}</div>
            <div><strong>Saga:</strong> {pkg?.project?.saga_name}</div>
            <div><strong>Autor:</strong> {pkg?.editorial?.author_default || "-"}</div>
            <div><strong>Producer:</strong> {pkg?.editorial?.producer || "-"}</div>
            <div><strong>ISBN:</strong> {pkg?.commercial?.isbn || "-"}</div>
            <div><strong>ASIN:</strong> {pkg?.commercial?.asin || "-"}</div>
            <div><strong>Preço:</strong> {pkg?.commercial?.price || "-"} {pkg?.commercial?.currency || ""}</div>
          </div>

          <div
            style={{
              padding: 12,
              borderRadius: 12,
              border: "1px solid #e5e7eb",
              background: "rgba(255,255,255,0.55)"
            }}
          >
            <div><strong>Ready:</strong> {pkg?.checks?.readiness?.ready ? "Sim" : "Não"}</div>
            <div><strong>Campos obrigatórios em falta:</strong> {(pkg?.checks?.readiness?.missing_required_fields || []).join(", ") || "-"}</div>
            <div><strong>Outputs obrigatórios em falta:</strong> {(pkg?.checks?.readiness?.missing_required_outputs || []).join(", ") || "-"}</div>
          </div>

          <textarea
            readOnly
            value={JSON.stringify(pkg, null, 2)}
            rows={24}
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
    </Card>
  )
      }
