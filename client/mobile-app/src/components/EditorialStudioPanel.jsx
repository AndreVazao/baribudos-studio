import { useEffect, useMemo, useState } from "react"
import {
  buildEditorialEngine,
  buildEditorialVideoPackage,
  editorialToIllustrations,
  editorialToStoryboard,
  editorialToStory,
  exportEditorialEpub,
  generateEditorialIllustrations,
  listProjects,
  mergeEditorialPages,
  previewEditorialEngine,
  renderFinalVideo,
  repaginateEditorialEngine,
  splitEditorialPage
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

function BookPage({ page }) {
  return (
    <div
      style={{
        minHeight: 260,
        borderRadius: 18,
        border: "1px solid #e5e7eb",
        background: "#fffef8",
        padding: 18,
        display: "grid",
        gridTemplateRows: "auto 1fr auto",
        gap: 12,
        boxShadow: "0 8px 20px rgba(0,0,0,0.06)"
      }}
    >
      <div style={{ fontWeight: 700 }}>Página {page.page_number}</div>
      <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.65, fontSize: 15 }}>{page.text || ""}</div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 12, color: "#6b7280" }}>
        <span>{page.layout?.show_illustration_slot ? "Ilustração" : "Texto"}</span>
        <span>{page.title || ""}</span>
      </div>
    </div>
  )
}

export default function EditorialStudioPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [text, setText] = useState("")
  const [ageGroup, setAgeGroup] = useState("4-10")
  const [genre, setGenre] = useState("children")
  const [illustrationEvery, setIllustrationEvery] = useState(2)
  const [editorial, setEditorial] = useState(null)
  const [preview, setPreview] = useState(null)
  const [mergeA, setMergeA] = useState("")
  const [mergeB, setMergeB] = useState("")

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

  const pageOptions = useMemo(
    () => (editorial?.pages || []).map((page) => page.page_number),
    [editorial]
  )

  async function handleBuild() {
    if (!selectedProjectId) return
    try {
      const res = await buildEditorialEngine(selectedProjectId, {
        text,
        age_group: ageGroup,
        genre,
        illustration_every: illustrationEvery
      })
      setEditorial(res?.editorial || null)
      alert("Motor editorial construída.")
    } catch (error) {
      alert(error?.message || "Erro ao construir motor editorial.")
    }
  }

  async function handlePreview() {
    if (!selectedProjectId) return
    try {
      const res = await previewEditorialEngine(selectedProjectId, {
        text,
        age_group: ageGroup,
        genre,
        illustration_every: illustrationEvery
      })
      setPreview(res?.preview || null)
      alert("Preview editorial gerado.")
    } catch (error) {
      alert(error?.message || "Erro ao gerar preview.")
    }
  }

  async function handleRepaginate() {
    if (!selectedProjectId) return
    try {
      const res = await repaginateEditorialEngine(selectedProjectId, {
        age_group: ageGroup,
        genre,
        illustration_every: illustrationEvery
      })
      setEditorial(res?.editorial || null)
      alert("Repaginação concluída.")
    } catch (error) {
      alert(error?.message || "Erro ao repaginar.")
    }
  }

  async function handleMerge() {
    if (!selectedProjectId || !mergeA || !mergeB) return
    try {
      const res = await mergeEditorialPages(selectedProjectId, {
        first_page_number: Number(mergeA),
        second_page_number: Number(mergeB)
      })
      setEditorial(res?.editorial || null)
      alert("Páginas unidas.")
    } catch (error) {
      alert(error?.message || "Erro ao unir páginas.")
    }
  }

  async function handleSplit(pageNumber) {
    if (!selectedProjectId || !pageNumber) return
    try {
      const res = await splitEditorialPage(selectedProjectId, {
        page_number: Number(pageNumber),
        age_group: ageGroup,
        genre
      })
      setEditorial(res?.editorial || null)
      alert("Página dividida.")
    } catch (error) {
      alert(error?.message || "Erro ao dividir página.")
    }
  }

  async function handleApplyStory() {
    if (!selectedProjectId) return
    try {
      await editorialToStory(selectedProjectId, {})
      alert("Editorial aplicada à story.")
    } catch (error) {
      alert(error?.message || "Erro ao aplicar à story.")
    }
  }

  async function handleIllustrationQueue() {
    if (!selectedProjectId) return
    try {
      await editorialToIllustrations(selectedProjectId)
      alert("Fila de ilustrações criada.")
    } catch (error) {
      alert(error?.message || "Erro ao criar fila de ilustrações.")
    }
  }

  async function handleGenerateIllustrations() {
    if (!selectedProjectId) return
    try {
      await generateEditorialIllustrations(selectedProjectId, {})
      alert("Ilustrações geradas.")
    } catch (error) {
      alert(error?.message || "Erro ao gerar ilustrações.")
    }
  }

  async function handleStoryboard() {
    if (!selectedProjectId) return
    try {
      await editorialToStoryboard(selectedProjectId)
      alert("Storyboard criada.")
    } catch (error) {
      alert(error?.message || "Erro ao criar storyboard.")
    }
  }

  async function handleVideoPackage() {
    if (!selectedProjectId) return
    try {
      await buildEditorialVideoPackage(selectedProjectId)
      alert("Pacote de vídeo criado.")
    } catch (error) {
      alert(error?.message || "Erro ao criar pacote de vídeo.")
    }
  }

  async function handleRenderVideo() {
    if (!selectedProjectId) return
    try {
      await renderFinalVideo(selectedProjectId)
      alert("Vídeo final renderizado.")
    } catch (error) {
      alert(error?.message || "Erro ao renderizar vídeo.")
    }
  }

  async function handleExportEpub() {
    if (!selectedProjectId) return
    try {
      await exportEditorialEpub(selectedProjectId, {})
      alert("EPUB exportado.")
    } catch (error) {
      alert(error?.message || "Erro ao exportar EPUB.")
    }
  }

  const visiblePages = preview?.pages || editorial?.pages || []

  return (
    <Card title="Editorial Studio">
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

      <div style={{ display: "grid", gridTemplateColumns: "1fr 180px 180px 180px", gap: 10 }}>
        <div />
        <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)} style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}>
          <option value="3-5">3-5</option>
          <option value="4-10">4-10</option>
          <option value="8-12">8-12</option>
          <option value="adult">adult</option>
        </select>

        <select value={genre} onChange={(e) => setGenre(e.target.value)} style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}>
          <option value="children">children</option>
          <option value="adult">adult</option>
          <option value="poetry">poetry</option>
          <option value="technical">technical</option>
        </select>

        <input
          type="number"
          min="1"
          value={illustrationEvery}
          onChange={(e) => setIllustrationEvery(Number(e.target.value || 2))}
          placeholder="Ilustrar a cada"
          style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <div style={{ display: "grid", gap: 10 }}>
          <label>Texto</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={18}
            style={{
              width: "100%",
              padding: 12,
              borderRadius: 12,
              border: "1px solid #d1d5db",
              outline: "none",
              resize: "vertical"
            }}
          />
        </div>

        <div style={{ display: "grid", gap: 10 }}>
          <label>Preview livro</label>
          <div
            style={{
              minHeight: 360,
              borderRadius: 14,
              border: "1px solid #e5e7eb",
              background: "rgba(255,255,255,0.6)",
              padding: 12,
              overflow: "auto"
            }}
          >
            <div style={{ display: "grid", gap: 12 }}>
              {visiblePages.slice(0, 8).map((page) => (
                <BookPage key={page.id || page.page_number} page={page} />
              ))}
              {!visiblePages.length ? <div>Sem preview ainda.</div> : null}
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button onClick={handleBuild} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#2F5E2E", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Construir editorial
        </button>

        <button onClick={handlePreview} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#1d4ed8", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Gerar preview
        </button>

        <button onClick={handleRepaginate} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#7c3aed", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Repaginar
        </button>

        <button onClick={handleApplyStory} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#92400e", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Aplicar à story
        </button>

        <button onClick={handleExportEpub} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#6d28d9", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Exportar EPUB
        </button>

        <button onClick={handleIllustrationQueue} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#0f766e", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Criar fila ilustração
        </button>

        <button onClick={handleGenerateIllustrations} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#15803d", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Gerar ilustrações
        </button>

        <button onClick={handleStoryboard} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#be185d", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Criar storyboard
        </button>

        <button onClick={handleVideoPackage} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#374151", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Criar pacote vídeo
        </button>

        <button onClick={handleRenderVideo} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#111827", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
          Render vídeo final
        </button>
      </div>

      {editorial?.pages?.length ? (
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
          <div><strong>Páginas:</strong> {editorial.pages_count || editorial.pages.length}</div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <select value={mergeA} onChange={(e) => setMergeA(e.target.value)} style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}>
              <option value="">Página A</option>
              {pageOptions.map((number) => <option key={`a-${number}`} value={number}>{number}</option>)}
            </select>

            <select value={mergeB} onChange={(e) => setMergeB(e.target.value)} style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}>
              <option value="">Página B</option>
              {pageOptions.map((number) => <option key={`b-${number}`} value={number}>{number}</option>)}
            </select>

            <button onClick={handleMerge} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#92400e", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
              Unir páginas
            </button>
          </div>

          <div style={{ display: "grid", gap: 8 }}>
            {editorial.pages.map((page) => (
              <div
                key={page.id}
                style={{
                  border: "1px solid #d1d5db",
                  borderRadius: 12,
                  padding: 12,
                  background: "#fff",
                  display: "grid",
                  gap: 8
                }}
              >
                <div><strong>Página {page.page_number}</strong></div>
                <div style={{ whiteSpace: "pre-wrap" }}>{page.text}</div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <button onClick={() => handleSplit(page.page_number)} style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#0f766e", color: "#fff", cursor: "pointer" }}>
                    Dividir
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </Card>
  )
  }
