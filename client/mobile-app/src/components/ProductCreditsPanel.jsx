import { useEffect, useState } from "react"
import { getProductCredits, listProjects, rebuildProductCredits, updateProductCredits } from "../api.js"

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

export default function ProductCreditsPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [credits, setCredits] = useState({})

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) loadCredits(selectedProjectId)
  }, [selectedProjectId])

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) setSelectedProjectId(list[0].id)
  }

  async function loadCredits(projectId) {
    try {
      const res = await getProductCredits(projectId)
      setCredits(res?.product_credits || {})
    } catch {
      setCredits({})
    }
  }

  async function handleRebuild() {
    if (!selectedProjectId) return
    try {
      const res = await rebuildProductCredits(selectedProjectId)
      setCredits(res?.product_credits || {})
      alert("Product credits reconstruídos.")
    } catch (error) {
      alert(error?.message || "Erro ao reconstruir credits.")
    }
  }

  async function handleSave() {
    if (!selectedProjectId) return
    try {
      const res = await updateProductCredits(selectedProjectId, credits)
      setCredits(res?.product_credits || {})
      alert("Product credits guardados.")
    } catch (error) {
      alert(error?.message || "Erro ao guardar credits.")
    }
  }

  function setList(field, value) {
    setCredits((current) => ({ ...current, [field]: parseCsv(value) }))
  }

  return (
    <Card title="Product Credits">
      <label>Projeto</label>
      <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
        <option value="">Selecionar projeto</option>
        {projects.map((project) => <option key={project.id} value={project.id}>{project.title} — {project.saga_name}</option>)}
      </select>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button onClick={handleRebuild} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#7c3aed", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Rebuild automático</button>
        <button onClick={handleSave} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#2F5E2E", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Guardar credits</button>
      </div>

      <input value={(credits.created_by || []).join(", ")} onChange={(e) => setList("created_by", e.target.value)} placeholder="Created by" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      <input value={(credits.written_by || []).join(", ")} onChange={(e) => setList("written_by", e.target.value)} placeholder="Written by" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      <input value={(credits.produced_by || []).join(", ")} onChange={(e) => setList("produced_by", e.target.value)} placeholder="Produced by" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      <input value={(credits.voices_by || []).join(", ")} onChange={(e) => setList("voices_by", e.target.value)} placeholder="Voices by" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      <input value={(credits.narration_by || []).join(", ")} onChange={(e) => setList("narration_by", e.target.value)} placeholder="Narration by" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      <input value={(credits.illustrations_by || []).join(", ")} onChange={(e) => setList("illustrations_by", e.target.value)} placeholder="Illustrations by" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      <input value={(credits.sound_design_by || []).join(", ")} onChange={(e) => setList("sound_design_by", e.target.value)} placeholder="Sound design by" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      <input value={(credits.editing_by || []).join(", ")} onChange={(e) => setList("editing_by", e.target.value)} placeholder="Editing by" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      <input value={(credits.special_thanks || []).join(", ")} onChange={(e) => setList("special_thanks", e.target.value)} placeholder="Special thanks" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
        <strong>Character voices</strong>
        {(credits.character_voices_by || []).map((item, index) => (
          <div key={`${item.character_name || "char"}-${index}`}>{item.character_name}: {item.credited_name}</div>
        ))}
        {!(credits.character_voices_by || []).length ? <div>Sem vozes de personagem ainda.</div> : null}
      </div>
    </Card>
  )
}
