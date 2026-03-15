import { useEffect, useState } from "react"
import {
  getIllustrationPipeline,
  getStoryboardManifest,
  listProjects,
  setupIllustrationPipeline,
  updateIllustrationFrame,
  uploadIllustrationFrameAsset
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

export default function IllustrationPipelinePanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [mode, setMode] = useState("approval")
  const [pipeline, setPipeline] = useState(null)
  const [manifest, setManifest] = useState(null)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadPipeline(selectedProjectId)
      loadManifest(selectedProjectId)
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

  async function loadPipeline(projectId) {
    try {
      const res = await getIllustrationPipeline(projectId)
      setPipeline(res?.pipeline || null)
    } catch {
      setPipeline(null)
    }
  }

  async function loadManifest(projectId) {
    try {
      const res = await getStoryboardManifest(projectId)
      setManifest(res?.manifest || null)
    } catch {
      setManifest(null)
    }
  }

  async function handleSetup() {
    if (!selectedProjectId) return
    try {
      const res = await setupIllustrationPipeline(selectedProjectId, {
        mode
      })
      setPipeline(res?.pipeline || null)
      await loadManifest(selectedProjectId)
      alert("Pipeline de ilustração preparada.")
    } catch (error) {
      alert(error?.message || "Erro ao preparar pipeline de ilustração.")
    }
  }

  async function handleApprove(frameId) {
    if (!selectedProjectId || !frameId) return
    try {
      const res = await updateIllustrationFrame(selectedProjectId, frameId, {
        status: "approved",
        approved: true
      })
      setPipeline(res?.illustration_pipeline || null)
      await loadManifest(selectedProjectId)
    } catch (error) {
      alert(error?.message || "Erro ao aprovar frame.")
    }
  }

  async function handleFileUpload(frameId, file) {
    if (!selectedProjectId || !frameId || !file) return
    try {
      await uploadIllustrationFrameAsset({
        projectId: selectedProjectId,
        frameId,
        file
      })
      await loadPipeline(selectedProjectId)
      await loadManifest(selectedProjectId)
      alert("Imagem associada ao frame.")
    } catch (error) {
      alert(error?.message || "Erro ao carregar imagem para o frame.")
    }
  }

  return (
    <Card title="Illustration Pipeline">
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

      <label>Modo de ilustração</label>
      <select
        value={mode}
        onChange={(e) => setMode(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="auto">Full automático</option>
        <option value="approval">Automático + aprovação</option>
        <option value="manual">Manual upload</option>
        <option value="hybrid">Híbrido livro + série</option>
      </select>

      <button
        onClick={handleSetup}
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
        Preparar pipeline de ilustração
      </button>

      {pipeline ? (
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
          <div><strong>Modo:</strong> {pipeline.mode}</div>
          <div><strong>Língua:</strong> {pipeline.language}</div>
          <div><strong>Frames:</strong> {(pipeline.frames || []).length}</div>

          {(pipeline.frames || []).slice(0, 12).map((frame) => (
            <div
              key={frame.id}
              style={{
                border: "1px solid #d1d5db",
                borderRadius: 12,
                padding: 10,
                display: "grid",
                gap: 6,
                background: "#fff"
              }}
            >
              <div><strong>Página:</strong> {frame.page_number}</div>
              <div><strong>Título:</strong> {frame.page_title}</div>
              <div><strong>Tipo:</strong> {frame.frame_type}</div>
              <div><strong>Status:</strong> {frame.status}</div>
              <div><strong>Aprovado:</strong> {frame.approved ? "Sim" : "Não"}</div>
              <div><strong>Imagem:</strong> {frame.image_path || "-"}</div>

              <textarea
                readOnly
                value={frame.prompt || ""}
                rows={4}
                style={{
                  width: "100%",
                  padding: 10,
                  borderRadius: 10,
                  border: "1px solid #d1d5db",
                  outline: "none",
                  fontSize: 12,
                  resize: "vertical"
                }}
              />

              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                <button
                  onClick={() => handleApprove(frame.id)}
                  style={{
                    padding: "8px 10px",
                    borderRadius: 10,
                    border: "none",
                    background: "#166534",
                    color: "#fff",
                    cursor: "pointer"
                  }}
                >
                  Aprovar
                </button>

                <label
                  style={{
                    padding: "8px 10px",
                    borderRadius: 10,
                    background: "#1d4ed8",
                    color: "#fff",
                    cursor: "pointer"
                  }}
                >
                  Upload manual
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    style={{ display: "none" }}
                    onChange={(e) => handleFileUpload(frame.id, e.target.files?.[0] || null)}
                  />
                </label>
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {manifest ? (
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
          <div><strong>Storyboard frames aprovados:</strong> {manifest.frames_count}</div>
          <textarea
            readOnly
            value={JSON.stringify(manifest, null, 2)}
            rows={12}
            style={{
              width: "100%",
              padding: 10,
              borderRadius: 10,
              border: "1px solid #d1d5db",
              outline: "none",
              fontSize: 12,
              fontFamily: "monospace",
              resize: "vertical"
            }}
          />
        </div>
      ) : null}
    </Card>
  )
    }
