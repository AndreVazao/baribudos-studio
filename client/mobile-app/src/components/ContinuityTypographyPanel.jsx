import { useEffect, useMemo, useState } from "react"
import { listProjects, listSagas, updateProject, updateSaga } from "../api.js"

function Card({ title, children }) {
  return <div style={{ border:"1px solid rgba(255,255,255,0.25)", borderRadius:16, background:"rgba(255,255,255,0.84)", backdropFilter:"blur(8px)", padding:16, display:"grid", gap:12, boxShadow:"0 10px 24px rgba(0,0,0,0.10)" }}><h3 style={{ margin:0, color:"#2F5E2E" }}>{title}</h3>{children}</div>
}

const FONT_OPTIONS = ["Georgia", "Times New Roman", "Garamond", "Palatino Linotype", "Trebuchet MS", "Verdana", "Arial", "Courier New", "Cinzel", "Papyrus"]
const DEFAULT_PREVIEW = "Os Baribudos na floresta encantada"

function parseCsv(value) {
  return String(value || "").split(",").map((item) => item.trim()).filter(Boolean)
}

export default function ContinuityTypographyPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [sagas, setSagas] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [selectedSagaSlug, setSelectedSagaSlug] = useState("")
  const [busy, setBusy] = useState(false)

  const selectedProject = useMemo(() => projects.find((item) => item.id === selectedProjectId) || null, [projects, selectedProjectId])
  const selectedSaga = useMemo(() => sagas.find((item) => item.slug === selectedSagaSlug) || null, [sagas, selectedSagaSlug])
  const continuity = selectedProject?.continuity || {}
  const story = selectedProject?.story || {}
  const frontMatter = selectedProject?.front_matter || {}
  const projectTypography = frontMatter.typography || {}
  const sagaTypography = selectedSaga?.typography || {}

  useEffect(() => { loadAll() }, [])

  async function loadAll() {
    const [projectsRes, sagasRes] = await Promise.all([listProjects(user), listSagas()])
    const nextProjects = projectsRes?.projects || []
    const nextSagas = sagasRes || []
    setProjects(nextProjects)
    setSagas(nextSagas)
    if (!selectedProjectId && nextProjects.length) setSelectedProjectId(nextProjects[0].id)
    if (!selectedSagaSlug && nextSagas.length) setSelectedSagaSlug(nextSagas[0].slug)
  }

  useEffect(() => {
    if (selectedProject?.saga_slug) setSelectedSagaSlug(selectedProject.saga_slug)
  }, [selectedProject?.saga_slug])

  async function saveProjectPatch(patch) {
    if (!selectedProjectId) return
    setBusy(true)
    try {
      await updateProject(selectedProjectId, patch, user)
      await loadAll()
    } catch (error) {
      alert(error?.message || "Erro ao guardar projeto.")
    } finally {
      setBusy(false)
    }
  }

  async function saveSagaTypography(patch) {
    if (!selectedSagaSlug) return
    setBusy(true)
    try {
      await updateSaga(selectedSagaSlug, { typography: patch })
      await loadAll()
    } catch (error) {
      alert(error?.message || "Erro ao guardar tipografia da saga.")
    } finally {
      setBusy(false)
    }
  }

  const sourceProject = useMemo(() => projects.find((item) => item.id === selectedProject?.continuity_source_project_id) || null, [projects, selectedProject])
  const inheritedFont = projectTypography.use_inherited !== false ? (sagaTypography.font_family || "Georgia") : (projectTypography.font_family || sagaTypography.font_family || "Georgia")
  const previewText = projectTypography.preview_text || sagaTypography.preview_text || continuity.preview_text || story.title || DEFAULT_PREVIEW

  return (
    <Card title="Continuity & Typography Studio">
      <label>Projeto</label>
      <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }}>
        <option value="">Selecionar projeto</option>
        {projects.map((project) => <option key={project.id} value={project.id}>{project.title} · {project.project_mode || "official"}</option>)}
      </select>

      {selectedProject ? <div style={{ padding:12, borderRadius:12, border:"1px solid #e5e7eb", background:"rgba(255,255,255,0.55)", display:"grid", gap:6 }}>
        <div><strong>{selectedProject.title}</strong></div>
        <div>Modo: {selectedProject.project_mode || "official"}</div>
        <div>Universe oculto: {selectedProject.hidden_universe_name || "-"}</div>
        <div>Saga oculta: {selectedProject.hidden_saga_name || "-"}</div>
        <div>Fonte herdada da saga: {sagaTypography.font_family || "-"}</div>
      </div> : null}

      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px,1fr))", gap:16 }}>
        <div style={{ display:"grid", gap:10, padding:12, borderRadius:12, border:"1px solid #e5e7eb", background:"rgba(255,255,255,0.55)" }}>
          <div><strong>Continuidade oculta / promovível</strong></div>
          <label>Modo do projeto</label>
          <select value={selectedProject?.project_mode || "official"} onChange={(e) => saveProjectPatch({ project_mode: e.target.value })} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }}>
            <option value="official">Official</option>
            <option value="standalone">Standalone</option>
            <option value="hidden_continuity">Hidden continuity</option>
            <option value="hidden_ip">Hidden IP</option>
            <option value="hidden_saga">Hidden Saga</option>
          </select>
          <label>Projeto fonte da continuidade</label>
          <select value={selectedProject?.continuity_source_project_id || ""} onChange={(e) => saveProjectPatch({ continuity_source_project_id: e.target.value })} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }}>
            <option value="">Sem projeto fonte</option>
            {projects.filter((project) => project.id !== selectedProjectId).map((project) => <option key={project.id} value={project.id}>{project.title}</option>)}
          </select>
          <label>Nome do universo oculto</label>
          <input value={selectedProject?.hidden_universe_name || ""} onChange={(e) => saveProjectPatch({ hidden_universe_name: e.target.value })} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }} />
          <label>Nome da saga oculta</label>
          <input value={selectedProject?.hidden_saga_name || ""} onChange={(e) => saveProjectPatch({ hidden_saga_name: e.target.value })} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }} />
          <label>Nomes de personagens de continuidade</label>
          <input value={(continuity.continuity_character_names || []).join(", ")} onChange={(e) => saveProjectPatch({ continuity: { continuity_character_names: parseCsv(e.target.value) } })} placeholder="Pai Baribudo, Mãe Baribuda, ..." style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }} />
          <label>Status de oficialização</label>
          <select value={continuity.officialization_status || "hidden"} onChange={(e) => saveProjectPatch({ continuity: { officialization_status: e.target.value } })} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }}>
            <option value="hidden">Hidden</option>
            <option value="candidate">Candidate</option>
            <option value="official">Official</option>
          </select>
          <label>Notas de continuidade</label>
          <textarea value={continuity.continuity_notes || ""} onChange={(e) => saveProjectPatch({ continuity: { continuity_notes: e.target.value } })} rows={4} style={{ width:"100%", padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none", resize:"vertical" }} />
          <div style={{ fontSize:12, color:"#475569" }}>Projeto fonte: {sourceProject?.title || "-"}</div>
        </div>

        <div style={{ display:"grid", gap:10, padding:12, borderRadius:12, border:"1px solid #e5e7eb", background:"rgba(255,255,255,0.55)" }}>
          <div><strong>Tipografia por herança</strong></div>
          <label>Saga a controlar</label>
          <select value={selectedSagaSlug} onChange={(e) => setSelectedSagaSlug(e.target.value)} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }}>
            <option value="">Selecionar saga</option>
            {sagas.map((saga) => <option key={saga.slug} value={saga.slug}>{saga.name}</option>)}
          </select>
          <label>Fonte base da saga</label>
          <select value={sagaTypography.font_family || "Georgia"} onChange={(e) => saveSagaTypography({ font_family: e.target.value })} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }}>
            {FONT_OPTIONS.map((font) => <option key={font} value={font}>{font}</option>)}
          </select>
          <label>Preview da saga</label>
          <input value={sagaTypography.preview_text || DEFAULT_PREVIEW} onChange={(e) => saveSagaTypography({ preview_text: e.target.value })} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }} />
          <label><input type="checkbox" checked={projectTypography.use_inherited !== false} onChange={(e) => saveProjectPatch({ front_matter: { typography: { ...projectTypography, use_inherited: e.target.checked } } })} /> Usar fonte herdada da saga neste volume/projeto</label>
          <label>Fonte override do projeto/volume</label>
          <select value={projectTypography.font_family || sagaTypography.font_family || "Georgia"} onChange={(e) => saveProjectPatch({ front_matter: { typography: { ...projectTypography, font_family: e.target.value, use_inherited: false } } })} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }}>
            {FONT_OPTIONS.map((font) => <option key={font} value={font}>{font}</option>)}
          </select>
          <label>Preview do volume/projeto</label>
          <input value={projectTypography.preview_text || ""} onChange={(e) => saveProjectPatch({ front_matter: { typography: { ...projectTypography, preview_text: e.target.value } } })} placeholder="Especial de Halloween dos Baribudos" style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", outline:"none" }} />
          <div style={{ padding:16, borderRadius:12, border:"1px solid #d1d5db", background:"#fffdf7", display:"grid", gap:8 }}>
            <div style={{ fontSize:12, color:"#475569" }}>Herança: Studio → Saga → volume/projeto</div>
            <div style={{ fontFamily: inheritedFont, fontSize:28, lineHeight:1.2, color:"#1f2937" }}>{previewText}</div>
            <div style={{ fontSize:12, color:"#64748b" }}>Fonte aplicada agora: {inheritedFont}</div>
          </div>
        </div>
      </div>

      <div style={{ fontSize:12, color:"#475569" }}>{busy ? "A guardar alterações editoriais..." : "Continuidade oculta e tipografia por herança prontas para crescer para IP/Saga oficial mais tarde."}</div>
    </Card>
  )
}
