import { useEffect, useMemo, useState } from "react"
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

function countLines(text) {
  return String(text || "").split("\n").length
}

function countWords(text) {
  return String(text || "").trim().split(/\s+/).filter(Boolean).length
}

function pageScaleStyle() {
  return {
    width: 210,
    minHeight: 297,
    borderRadius: 10,
    border: "1px solid #d1d5db",
    background: "#fffef8",
    boxShadow: "0 10px 24px rgba(0,0,0,0.10)",
    padding: 16,
    display: "grid",
    alignContent: "start",
    gap: 8,
    transform: "scale(0.88)",
    transformOrigin: "top center",
    overflow: "hidden"
  }
}

export default function StoryLayoutPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [rawText, setRawText] = useState("")
  const [layout, setLayout] = useState(null)
  const [selectedPageId, setSelectedPageId] = useState("")

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadLayout(selectedProjectId)
    }
  }, [selectedProjectId])

  const pages = layout?.pages || []
  const selectedPage = useMemo(() => pages.find((page) => page.id === selectedPageId) || pages[0] || null, [pages, selectedPageId])

  useEffect(() => {
    if (selectedPage && selectedPage.id !== selectedPageId) {
      setSelectedPageId(selectedPage.id)
    }
  }, [selectedPage, selectedPageId])

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
      setSelectedPageId((nextLayout?.pages || [])[0]?.id || "")
    } catch {
      setLayout(null)
      setSelectedPageId("")
    }
  }

  async function handlePaginate() {
    if (!selectedProjectId) return
    try {
      const res = await paginateStoryLayout(selectedProjectId, { raw_text: rawText })
      const nextLayout = res?.layout || null
      setLayout(nextLayout)
      setSelectedPageId((nextLayout?.pages || [])[0]?.id || "")
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
      if (selectedPageId === pageId) {
        setSelectedPageId((res?.layout?.pages || [])[0]?.id || "")
      }
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

  const profile = layout?.profile || {}

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
        <button onClick={handlePaginate} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#2F5E2E", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Paginar automático</button>
        <button onClick={handleCreatePage} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#1d4ed8", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Nova página</button>
        <button onClick={handleApply} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#7c3aed", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Aplicar à história</button>
      </div>

      {layout ? (
        <>
          <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 8 }}>
            <div><strong>Perfil:</strong> {profile.profile || "-"}</div>
            <div><strong>Máx. linhas/página:</strong> {profile.max_lines_per_page || "-"}</div>
            <div><strong>Máx. palavras/linha:</strong> {profile.max_words_per_line || "-"}</div>
            <div><strong>Ilustração recomendada:</strong> {profile.illustration_recommended ? "Sim" : "Não"}</div>
            <div><strong>Edição manual:</strong> ativa e obrigatoriamente disponível para afinação final.</div>
          </div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {pages.map((page) => (
              <button
                key={page.id}
                onClick={() => setSelectedPageId(page.id)}
                style={{
                  padding: "8px 10px",
                  borderRadius: 10,
                  border: page.id === selectedPage?.id ? "2px solid #2F5E2E" : "1px solid #cbd5e1",
                  background: page.id === selectedPage?.id ? "rgba(47,94,46,0.12)" : "#fff",
                  cursor: "pointer"
                }}
              >
                Página {page.pageNumber}
              </button>
            ))}
          </div>

          {selectedPage ? (
            <div style={{ display: "grid", gridTemplateColumns: "minmax(340px, 1.1fr) minmax(260px, 0.9fr)", gap: 16, alignItems: "start" }}>
              <div style={{ border: "1px solid #d1d5db", borderRadius: 12, padding: 12, background: "rgba(255,255,255,0.7)", display: "grid", gap: 10 }}>
                <div><strong>Editor manual — Página {selectedPage.pageNumber}</strong></div>

                <input
                  value={selectedPage.title || ""}
                  onChange={(e) => handleUpdatePage(selectedPage.id, { title: e.target.value, text: selectedPage.text, illustration_requested: selectedPage.illustration_requested, scene_requested: selectedPage.scene_requested })}
                  style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}
                />

                <textarea
                  value={selectedPage.text || ""}
                  onChange={(e) => handleUpdatePage(selectedPage.id, { title: selectedPage.title, text: e.target.value, illustration_requested: selectedPage.illustration_requested, scene_requested: selectedPage.scene_requested })}
                  rows={14}
                  style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none", resize: "vertical", fontFamily: "Arial, sans-serif", lineHeight: 1.5 }}
                />

                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0,1fr))", gap: 8 }}>
                  <div style={{ padding: 8, borderRadius: 10, background: "#fff" }}><strong>Linhas</strong><div>{countLines(selectedPage.text)}</div></div>
                  <div style={{ padding: 8, borderRadius: 10, background: "#fff" }}><strong>Palavras</strong><div>{countWords(selectedPage.text)}</div></div>
                  <div style={{ padding: 8, borderRadius: 10, background: "#fff" }}><strong>Nº página</strong><div>{selectedPage.pageNumber}</div></div>
                </div>

                <label><input type="checkbox" checked={!!selectedPage.illustration_requested} onChange={(e) => handleUpdatePage(selectedPage.id, { title: selectedPage.title, text: selectedPage.text, illustration_requested: e.target.checked, scene_requested: selectedPage.scene_requested })} /> Ilustração pedida</label>
                <label><input type="checkbox" checked={!!selectedPage.scene_requested} onChange={(e) => handleUpdatePage(selectedPage.id, { title: selectedPage.title, text: selectedPage.text, illustration_requested: selectedPage.illustration_requested, scene_requested: e.target.checked })} /> Cena para série</label>

                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <button onClick={() => handleMovePage(selectedPage.id, "up")} style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#0f766e", color: "#fff", cursor: "pointer" }}>Subir</button>
                  <button onClick={() => handleMovePage(selectedPage.id, "down")} style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#0f766e", color: "#fff", cursor: "pointer" }}>Descer</button>
                  <button onClick={() => handleSplitPage(selectedPage.id)} style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#92400e", color: "#fff", cursor: "pointer" }}>Dividir página</button>
                  <button onClick={() => handleMoveParagraph(selectedPage.id, "prev")} style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#1d4ed8", color: "#fff", cursor: "pointer" }}>Enviar texto para anterior</button>
                  <button onClick={() => handleMoveParagraph(selectedPage.id, "next")} style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#1d4ed8", color: "#fff", cursor: "pointer" }}>Enviar texto para seguinte</button>
                  <button onClick={() => handleDeletePage(selectedPage.id)} style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#b91c1c", color: "#fff", cursor: "pointer" }}>Apagar página</button>
                </div>
              </div>

              <div style={{ border: "1px solid #d1d5db", borderRadius: 12, padding: 12, background: "rgba(255,255,255,0.7)", display: "grid", gap: 10, justifyItems: "center" }}>
                <div><strong>Preview visual da página</strong></div>
                <div style={pageScaleStyle()}>
                  <div style={{ fontSize: 10, color: "#6b7280", textAlign: "right" }}>Página {selectedPage.pageNumber}</div>
                  <div style={{ fontSize: 13, fontWeight: 700, textAlign: "center", color: "#1f2937" }}>{selectedPage.title || `Página ${selectedPage.pageNumber}`}</div>
                  <div style={{ fontSize: 10.5, lineHeight: 1.45, whiteSpace: "pre-wrap", color: "#111827" }}>{selectedPage.text || "(sem texto nesta página)"}</div>
                  <div style={{ marginTop: "auto", fontSize: 9, color: "#6b7280", display: "flex", justifyContent: "space-between" }}>
                    <span>{selectedPage.illustration_requested ? "Ilustração pedida" : "Sem ilustração"}</span>
                    <span>{selectedPage.scene_requested ? "Cena pedida" : "Sem cena"}</span>
                  </div>
                </div>
                <div style={{ fontSize: 12, color: "#6b7280", textAlign: "center" }}>Preview em escala reduzida. A edição manual continua a mandar no resultado final.</div>
              </div>
            </div>
          ) : null}
        </>
      ) : null}
    </Card>
  )
}
