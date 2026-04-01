import { useEffect, useMemo, useState } from "react"
import { listProductionRuns, listProjects, runProductionPipeline } from "../api.js"

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

const VIDEO_MODE_HELP = {
  manual: "Fluxo manual: vídeo/série só avançam quando tu pedes e controlas cada output.",
  paste: "Fluxo baseado em materiais externos/importados, com montagem no Studio.",
  local_first: "Preferência por render/montagem local-first no teu Studio/PC.",
  free_api: "Preferência por serviços grátis quando existirem, com fallback local/manual.",
  assisted: "Fluxo assistido: o Studio prepara o vídeo, tu validas os passos críticos.",
  auto: "Fluxo automático: o Studio tenta levar a série/mini filme até ao fim com mínima intervenção.",
}

function suggestedRunMode(stageMode) {
  return stageMode === "manual" ? "manual" : stageMode === "paste" ? "manual" : "auto"
}

export default function ProductionPipelinePanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [mode, setMode] = useState("auto")
  const [options, setOptions] = useState({
    createStory: true,
    createCover: true,
    createEpub: true,
    createAudiobook: true,
    createSeries: true,
    createGuide: true
  })
  const [latestResult, setLatestResult] = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => { loadAll() }, [])
  const selectedProject = useMemo(() => projects.find((project) => project.id === selectedProjectId) || null, [projects, selectedProjectId])
  const videoMode = selectedProject?.stage_modes?.video_mode || "manual"

  useEffect(() => {
    setMode(suggestedRunMode(videoMode))
  }, [videoMode, selectedProjectId])

  async function loadAll() {
    const [projectsRes, runsRes] = await Promise.all([listProjects(user), listProductionRuns()])
    const projectList = projectsRes?.projects || []
    const runs = runsRes?.runs || []
    setProjects(projectList)
    setHistory(runs)
    if (!selectedProjectId && projectList.length) setSelectedProjectId(projectList[0].id)
  }

  function setFlag(key, value) { setOptions((current) => ({ ...current, [key]: value })) }

  async function handleRun() {
    if (!selectedProjectId) return
    try {
      const payload = mode === "auto" ? { mode: "auto", ...options } : { mode: "manual", ...options }
      const res = await runProductionPipeline(selectedProjectId, payload)
      setLatestResult(res || null)
      await loadAll()
      alert("Pipeline concluída.")
    } catch (error) {
      alert(error?.message || "Erro na pipeline.")
    }
  }

  const autoVideoDisabled = videoMode === "manual" || videoMode === "paste"

  return (
    <Card title="Production Pipeline Engine">
      <label>Projeto</label>
      <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
        <option value="">Selecionar projeto</option>
        {projects.map((project) => <option key={project.id} value={project.id}>{project.title} — {project.saga_name}</option>)}
      </select>

      {selectedProject ? (
        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
          <div><strong>Modo de vídeo desta etapa:</strong> {videoMode}</div>
          <div style={{ color: "#475569" }}>{VIDEO_MODE_HELP[videoMode] || VIDEO_MODE_HELP.manual}</div>
          <div><strong>Modo sugerido de execução:</strong> {mode}</div>
        </div>
      ) : null}

      <label>Modo</label>
      <select value={mode} onChange={(e) => setMode(e.target.value)} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
        <option value="auto">Automático</option>
        <option value="manual">Manual</option>
      </select>

      <div style={{ display: "grid", gap: 8 }}>
        <label><input type="checkbox" checked={options.createStory} onChange={(e) => setFlag("createStory", e.target.checked)} /> Story</label>
        <label><input type="checkbox" checked={options.createCover} onChange={(e) => setFlag("createCover", e.target.checked)} /> Cover</label>
        <label><input type="checkbox" checked={options.createEpub} onChange={(e) => setFlag("createEpub", e.target.checked)} /> EPUB</label>
        <label><input type="checkbox" checked={options.createAudiobook} onChange={(e) => setFlag("createAudiobook", e.target.checked)} /> Audiobook</label>
        <label><input type="checkbox" checked={options.createSeries} onChange={(e) => setFlag("createSeries", e.target.checked)} /> Série / Vídeo</label>
        <label><input type="checkbox" checked={options.createGuide} onChange={(e) => setFlag("createGuide", e.target.checked)} /> Guide</label>
      </div>

      <button onClick={handleRun} disabled={autoVideoDisabled && mode === "auto"} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: autoVideoDisabled && mode === "auto" ? "#94a3b8" : "#2F5E2E", color: "#fff", fontWeight: 700, cursor: autoVideoDisabled && mode === "auto" ? "not-allowed" : "pointer" }}>
        Executar pipeline
      </button>

      {latestResult ? (
        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 8 }}>
          <div><strong>Run ID:</strong> {latestResult.run_id}</div>
          <div><strong>Modo:</strong> {latestResult.mode}</div>
          <div><strong>Estado:</strong> {latestResult.state}</div>
          <div><strong>Runtime:</strong> {latestResult.runtime?.name} ({latestResult.runtime?.slug})</div>
          <textarea readOnly value={JSON.stringify(latestResult, null, 2)} rows={18} style={{ width: "100%", padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", fontFamily: "monospace", fontSize: 13, resize: "vertical" }} />
        </div>
      ) : null}

      <div style={{ display: "grid", gap: 6 }}>
        <strong>Histórico</strong>
        {history.slice().reverse().slice(0, 6).map((item) => <div key={item.id}>{item.created_at} — {item.project_id} — {item.mode} — {item.state}</div>)}
      </div>
    </Card>
  )
}
