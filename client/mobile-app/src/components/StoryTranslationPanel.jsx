import { useEffect, useState } from "react"
import { generateStoryTranslations, getStoryTranslations, listProjects } from "../api.js"

function Card({ title, children }) {
  return (
    <div style={{ border: "1px solid rgba(255,255,255,0.25)", borderRadius: 16, background: "rgba(255,255,255,0.84)", backdropFilter: "blur(8px)", padding: 16, display: "grid", gap: 12, boxShadow: "0 10px 24px rgba(0,0,0,0.10)" }}>
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>{title}</h3>
      {children}
    </div>
  )
}

function parseCsv(value) {
  return String(value || "").split(",").map((item) => item.trim()).filter(Boolean)
}

export default function StoryTranslationPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [languagesCsv, setLanguagesCsv] = useState("pt-PT, pt-BR, en, es, fr, de, it, nl, zh, ja")
  const [variants, setVariants] = useState({})

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadTranslations(selectedProjectId)
    }
  }, [selectedProjectId])

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) setSelectedProjectId(list[0].id)
  }

  async function loadTranslations(projectId) {
    try {
      const res = await getStoryTranslations(projectId)
      setVariants(res?.language_variants || {})
    } catch {
      setVariants({})
    }
  }

  async function handleGenerate() {
    if (!selectedProjectId) return
    try {
      const res = await generateStoryTranslations(selectedProjectId, {
        languages: parseCsv(languagesCsv),
      })
      setVariants(res?.language_variants || {})
      alert("Traduções geradas a partir do texto oficial.")
    } catch (error) {
      alert(error?.message || "Erro ao gerar traduções.")
    }
  }

  const entries = Object.entries(variants || {})

  return (
    <Card title="Story Translation / Multi-Língua">
      <label>Projeto</label>
      <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
        <option value="">Selecionar projeto</option>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>{project.title} — {project.saga_name}</option>
        ))}
      </select>

      <input value={languagesCsv} onChange={(e) => setLanguagesCsv(e.target.value)} placeholder="Idiomas separados por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <button onClick={handleGenerate} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#2F5E2E", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
        Gerar traduções a partir do story source
      </button>

      <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 8 }}>
        <strong>Variantes geradas</strong>
        {entries.map(([language, item]) => (
          <div key={language} style={{ border: "1px solid #d1d5db", borderRadius: 12, padding: 10, background: "#fff", display: "grid", gap: 6 }}>
            <div><strong>{language}</strong> — {item?.translation_status || "-"}</div>
            <div>Engine: {item?.translation_engine || "-"}</div>
            <div>Língua origem: {item?.source_language || "-"}</div>
            <textarea readOnly value={item?.raw_text || ""} rows={6} style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />
          </div>
        ))}
        {!entries.length ? <div>Sem traduções ainda.</div> : null}
      </div>

      <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(254,243,199,0.85)" }}>
        <strong>Paginação manual continua disponível.</strong> A geração automática de traduções não elimina a edição manual da paginação nem a afinação página a página no story layout.
      </div>
    </Card>
  )
}
