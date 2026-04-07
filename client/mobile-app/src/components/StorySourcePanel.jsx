import { useEffect, useMemo, useState } from "react"
import { getStorySource, getStorySourceGate, listProjects, lockStorySource, saveStorySource } from "../api.js"
import StoryFlowGuidanceCard from "./StoryFlowGuidanceCard.jsx"

function Card({ title, children }) {
  return (
    <div style={{ border: "1px solid rgba(255,255,255,0.25)", borderRadius: 16, background: "rgba(255,255,255,0.84)", backdropFilter: "blur(8px)", padding: 16, display: "grid", gap: 12, boxShadow: "0 10px 24px rgba(0,0,0,0.10)" }}>
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>{title}</h3>
      {children}
    </div>
  )
}

const EMPTY_SOURCE = {
  story_source_text: "",
  story_source_language: "pt-PT",
  story_source_type: "pasted_text",
  story_source_notes: "",
  text_locked: false,
  text_approved: false,
}

const MODE_HELP = {
  manual: "Entrada manual livre. Escreve ou cola o texto final à mão.",
  paste: "Fluxo orientado a cópia/cola. Ideal para textos vindos de outro chat ou rascunho externo.",
  local_first: "Preferência por ferramentas locais simples para tratamento/geração do texto.",
  free_api: "Preferência por API grátis quando existir, com fallback humano/local.",
  assisted: "Fluxo assistido: tu introduces a base e o Studio ajuda a estruturar e validar.",
  auto: "Fluxo automático: o Studio deve tentar fechar esta etapa com mínima intervenção.",
}

const SOURCE_TYPE_BY_MODE = {
  manual: ["pasted_text", "imported_text"],
  paste: ["pasted_text", "external_chat_origin", "imported_text"],
  local_first: ["imported_text", "pasted_text"],
  free_api: ["external_chat_origin", "pasted_text"],
  assisted: ["pasted_text", "imported_text", "external_chat_origin"],
  auto: ["external_chat_origin", "imported_text", "pasted_text"],
}

function labelForSourceType(value) {
  return value === "pasted_text" ? "Texto colado" : value === "imported_text" ? "Texto importado" : value === "external_chat_origin" ? "Origem externa / outro chat" : value
}

export default function StorySourcePanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [storySource, setStorySource] = useState(EMPTY_SOURCE)
  const [gate, setGate] = useState(null)

  useEffect(() => { loadProjects() }, [])
  useEffect(() => { if (selectedProjectId) refresh(selectedProjectId) }, [selectedProjectId])

  const selectedProject = useMemo(() => projects.find((project) => project.id === selectedProjectId) || null, [projects, selectedProjectId])
  const storyInputMode = selectedProject?.stage_modes?.story_input_mode || "manual"
  const allowedSourceTypes = SOURCE_TYPE_BY_MODE[storyInputMode] || SOURCE_TYPE_BY_MODE.manual

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) setSelectedProjectId(list[0].id)
  }

  async function refresh(projectId) {
    const [sourceRes, gateRes] = await Promise.all([
      getStorySource(projectId).catch(() => ({ story_source: {} })),
      getStorySourceGate(projectId).catch(() => ({ story_source_gate: null })),
    ])
    setStorySource({ ...EMPTY_SOURCE, ...(sourceRes?.story_source || {}) })
    setGate(gateRes?.story_source_gate || null)
  }

  async function handleSave() {
    if (!selectedProjectId) return
    try {
      const res = await saveStorySource(selectedProjectId, storySource)
      setStorySource({ ...EMPTY_SOURCE, ...(res?.story_source || {}) })
      await refresh(selectedProjectId)
      alert("Story source guardado.")
    } catch (error) {
      alert(error?.message || "Erro ao guardar story source.")
    }
  }

  async function handleLock(approved = false) {
    if (!selectedProjectId) return
    try {
      const res = await lockStorySource(selectedProjectId, approved)
      setStorySource({ ...EMPTY_SOURCE, ...(res?.story_source || {}) })
      await refresh(selectedProjectId)
      alert(approved ? "Texto bloqueado e aprovado." : "Texto bloqueado.")
    } catch (error) {
      alert(error?.message || "Erro ao bloquear texto.")
    }
  }

  return (
    <Card title="Story Source / Text-First Gate">
      <label>Projeto</label>
      <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
        <option value="">Selecionar projeto</option>
        {projects.map((project) => <option key={project.id} value={project.id}>{project.title} — {project.saga_name}</option>)}
      </select>

      {selectedProject ? (
        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
          <div><strong>Modo de texto desta etapa:</strong> {storyInputMode}</div>
          <div style={{ color: "#475569" }}>{MODE_HELP[storyInputMode] || MODE_HELP.manual}</div>
          <div><strong>Modo estrutural:</strong> {selectedProject.project_mode || "official"}</div>
        </div>
      ) : null}

      {gate ? (
        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: gate.ready_for_text_first_pipeline ? "rgba(220,252,231,0.65)" : "rgba(254,243,199,0.8)", display: "grid", gap: 6 }}>
          <div><strong>{gate.label}</strong></div>
          <div>Tem texto: {gate.has_text ? "Sim" : "Não"}</div>
          <div>Texto bloqueado: {gate.text_locked ? "Sim" : "Não"}</div>
          <div>Texto aprovado: {gate.text_approved ? "Sim" : "Não"}</div>
        </div>
      ) : null}

      <StoryFlowGuidanceCard
        storyText={storySource.story_source_text || ""}
        layoutInfo={null}
        lastAction={storySource.text_locked || storySource.text_approved ? "updated" : ""}
        stageMode={storyInputMode}
      />

      <label>Origem do texto</label>
      <select value={storySource.story_source_type || allowedSourceTypes[0]} onChange={(e) => setStorySource((current) => ({ ...current, story_source_type: e.target.value }))} style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
        {allowedSourceTypes.map((option) => <option key={option} value={option}>{labelForSourceType(option)}</option>)}
      </select>

      <input value={storySource.story_source_language || "pt-PT"} onChange={(e) => setStorySource((current) => ({ ...current, story_source_language: e.target.value }))} placeholder="Língua do texto base" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <textarea value={storySource.story_source_text || ""} onChange={(e) => setStorySource((current) => ({ ...current, story_source_text: e.target.value }))} rows={12} placeholder={storyInputMode === "manual" ? "Escreve ou cola aqui o texto base da história" : storyInputMode === "paste" ? "Cola aqui o texto vindo do outro chat ou origem externa" : storyInputMode === "local_first" ? "Cola ou prepara aqui o texto que será trabalhado localmente" : storyInputMode === "free_api" ? "Descreve/cola aqui a base que a API grátis deverá usar" : storyInputMode === "assisted" ? "Cola aqui o rascunho para o Studio te ajudar a estruturar" : "Texto base para pipeline automática"} style={{ width: "100%", padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />

      <textarea value={storySource.story_source_notes || ""} onChange={(e) => setStorySource((current) => ({ ...current, story_source_notes: e.target.value }))} rows={3} placeholder="Notas sobre a origem do texto, prompt usado, referência externa ou instruções" style={{ width: "100%", padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button onClick={handleSave} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#2F5E2E", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Guardar texto base</button>
        <button onClick={() => handleLock(false)} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#7c3aed", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Bloquear texto</button>
        <button onClick={() => handleLock(true)} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#0f766e", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Bloquear e aprovar</button>
      </div>
    </Card>
  )
}
