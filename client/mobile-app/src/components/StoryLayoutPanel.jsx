import { useEffect, useState } from "react"
import {
  applyStoryLayout,
  createStoryLayoutPage,
  deleteStoryLayoutPage,
  getStoryLayout,
  listProjects,
  moveStoryLayoutPage,
  moveStoryLayoutText,
  paginateStoryLayout,
  splitStoryLayoutPage,
  updateStoryLayoutPage
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

export default function StoryLayoutPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [rawText, setRawText] = useState("")
  const [layout, setLayout] = useState(null)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadLayout(selectedProjectId)
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

  async function loadLayout(projectId) {
    try {
      const res = await getStoryLayout(projectId)
      const nextLayout = res?.layout || null
      setLayout(nextLayout)
      setRawText(nextLayout?.raw_text || "")
    } catch {
      setLayout(null)
    }
  }

  async function handlePaginate() {
    if (!selectedProjectId) return
    try {
      const res = await paginateStoryLayout(selectedProjectId, { raw_text: rawText })
      setLayout(res?.layout || null)
      alert("Paginação automática concluída.")
    } catch (error) {
      alert(error?.message || "Erro ao paginar texto.")
    }
  }

  async function handleApply() {
    if (!selectedProjectId) return
    try {
      await applyStoryLayout(selectedProjectId, {})
      alert("Layout aplicada à história.")
    } catch (error) {
      alert(error?.message || "Erro ao aplicar layout.")
    }
  }

  async function handleCreatePage() {
    if (!selectedProjectId) return
    try {
      const res = await createStoryLayoutPage(selectedProjectId, {
        title: "Nova página",
        text: "",
        illustration_requested: false,
        scene_requested: false
      })
      setLayout(res?.layout || null)
    } catch (error) {
      alert(error?.message || "Erro ao criar página.")
    }
  }

  async function handleUpdatePage(pageId, patch) {
    if (!selectedProjectId || !pageId) return
    try {
      const res = await updateStoryLayoutPage(selectedProjectId, pageId, patch)
      setLayout(res?.layout || null)
    } catch (error) {
      alert(error?.message || "Erro ao atualizar página.")
    }
  }

  async function handleDeletePage(pageId) {
    if (!selectedProjectId || !pageId) return
    try {
      const res = await deleteStoryLayoutPage(selectedProjectId, pageId)
      setLayout(res?.layout || null)
    } catch (error) {
      alert(error?.message || "Erro ao apagar página.")
    }
  }

  async function handleMovePage(pageId, direction) {
    if (!selectedProjectId || !pageId) return
    try {
      const res = await moveStoryLayoutPage(selectedProjectId, pageId, direction)
      setLayout(res?.layout || null)
    } catch (error) {
      alert(error?.message || "Erro ao mover página.")
    }
  }

  async function handleSplitPage(pageId) {
    if (!selectedProjectId || !pageId) return
    try {
      const res = await splitStoryLayoutPage(selectedProjectId, pageId, "half")
      setLayout(res?.layout || null)
    } catch (error) {
      alert(error?.message || "Erro ao dividir página.")
    }
  }

  async function handleMoveParagraph(pageId, direction) {
    if (!selectedProjectId || !pageId || !layout?.pages?.length) return
    const pages = layout.pages || []
    const index = pages.findIndex((page) => page.id === pageId)
    if (index < 0) return

    const targetIndex = direction === "prev" ? index - 1 : index + 1
    if (targetIndex < 0 || targetIndex >= pages.length) return

    try {
      const res = await moveStoryLayoutText(selectedProjectId, {
        from_page_id: pageId,
        to_page_id: pages[targetIndex].id,
        mode: direction === "prev" ? "first_paragraph" : "last_paragraph"
      })
      setLayout(res?.layout || null)
    } catch (error) {
      alert(error?.message || "Erro ao mover texto.")
    }
  }

  return (
    <Card title="Story Layout Editor">
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

      <label>Texto base</label>
      <textarea
        value={rawText}
        onChange={(e) => setRawText(e.target.value)}
        rows={8}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
          resize: "vertical"
        }}
      />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={handlePaginate}
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
          Paginar automático
        </button>

        <button
          onClick={handleCreatePage}
          style={{
            padding: "10px 12px",
            borderRadius: 12,
            border: "none",
            background: "#1d4ed8",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          Nova página
        </button>

        <button
          onClick={handleApply}
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
          Aplicar à história
        </button>
      </div>

      {layout ? (
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
          <div><strong>Perfil:</strong> {layout?.profile?.profile || "-"}</div>
          <div><strong>Máx. linhas/página:</strong> {layout?.profile?.max_lines_per_page || "-"}</div>
          <div><strong>Máx. palavras/linha:</strong> {layout?.profile?.max_words_per_line || "-"}</div>
          <div><strong>Ilustração recomendada:</strong> {layout?.profile?.illustration_recommended ? "Sim" : "Não"}</div>

          {(layout.pages || []).map((page) => (
            <div
              key={page.id}
              style={{
                border: "1px solid #d1d5db",
                borderRadius: 12,
                padding: 10,
                display: "grid",
                gap: 8,
                background: "#fff"
              }}
            >
              <div><strong>Página {page.pageNumber}</strong></div>

              <input
                value={page.title || ""}
                onChange={(e) => handleUpdatePage(page.id, { title: e.target.value, text: page.text, illustration_requested: page.illustration_requested, scene_requested: page.scene_requested })}
                style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}
              />

              <textarea
                value={page.text || ""}
                onChange={(e) => handleUpdatePage(page.id, { title: page.title, text: e.target.value, illustration_requested: page.illustration_requested, scene_requested: page.scene_requested })}
                rows={5}
                style={{
                  width: "100%",
                  padding: 10,
                  borderRadius: 10,
                  border: "1px solid #d1d5db",
                  outline: "none",
                  resize: "vertical"
                }}
              />

              <label>
                <input
                  type="checkbox"
                  checked={!!page.illustration_requested}
                  onChange={(e) => handleUpdatePage(page.id, { title: page.title, text: page.text, illustration_requested: e.target.checked, scene_requested: page.scene_requested })}
                /> Ilustração pedida
              </label>

              <label>
                <input
                  type="checkbox"
                  checked={!!page.scene_requested}
                  onChange={(e) => handleUpdatePage(page.id, { title: page.title, text: page.text, illustration_requested: page.illustration_requested, scene_requested: e.target.checked })}
                /> Cena para série
              </label>

              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <button
                  onClick={() => handleMovePage(page.id, "up")}
                  style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#0f766e", color: "#fff", cursor: "pointer" }}
                >
                  Subir
                </button>

                <button
                  onClick={() => handleMovePage(page.id, "down")}
                  style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#0f766e", color: "#fff", cursor: "pointer" }}
                >
                  Descer
                </button>

                <button
                  onClick={() => handleSplitPage(page.id)}
                  style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#92400e", color: "#fff", cursor: "pointer" }}
                >
                  Dividir página
                </button>

                <button
                  onClick={() => handleMoveParagraph(page.id, "prev")}
                  style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#1d4ed8", color: "#fff", cursor: "pointer" }}
                >
                  Enviar texto para anterior
                </button>

                <button
                  onClick={() => handleMoveParagraph(page.id, "next")}
                  style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#1d4ed8", color: "#fff", cursor: "pointer" }}
                >
                  Enviar texto para seguinte
                </button>

                <button
                  onClick={() => handleDeletePage(page.id)}
                  style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#b91c1c", color: "#fff", cursor: "pointer" }}
                >
                  Apagar página
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </Card>
  )
}
