import { useMemo } from "react"

const PROJECT_MODES = [
  { id: "official", label: "Official", description: "Projeto já nasce ligado a IP/Saga oficial." },
  { id: "standalone", label: "Standalone", description: "Livro isolado, sem compromisso imediato com IP/Saga oficial." },
  { id: "hidden_continuity", label: "Hidden continuity", description: "Continuação discreta baseada em outro projeto, ainda sem oficialização pública." },
  { id: "hidden_ip", label: "Hidden IP", description: "Nasce como universo oculto que pode virar IP oficial mais tarde." },
  { id: "hidden_saga", label: "Hidden Saga", description: "Nasce como saga oculta dentro de um universo ainda não oficial." },
]

const STAGE_MODE_OPTIONS = [
  { id: "manual", label: "Manual" },
  { id: "paste", label: "Cópia / cola" },
  { id: "local_first", label: "Local-first" },
  { id: "free_api", label: "API grátis" },
  { id: "assisted", label: "Assistido" },
  { id: "auto", label: "Automático" },
]

function StageModeSelect({ label, value, onChange }) {
  return (
    <div style={{ display: "grid", gap: 6 }}>
      <label>{label}</label>
      <select value={value || "manual"} onChange={(e) => onChange(e.target.value)} style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }}>
        {STAGE_MODE_OPTIONS.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
      </select>
    </div>
  )
}

export default function ProjectCreationModePanel({ value, onChange }) {
  const projectMode = value?.project_mode || "official"
  const stageModes = value?.stage_modes || {}
  const activeMode = useMemo(() => PROJECT_MODES.find((item) => item.id === projectMode) || PROJECT_MODES[0], [projectMode])
  const isHidden = ["standalone", "hidden_continuity", "hidden_ip", "hidden_saga"].includes(projectMode)

  function patch(next) {
    onChange?.({ ...(value || {}), ...next })
  }

  function patchStageMode(key, nextValue) {
    patch({ stage_modes: { ...(value?.stage_modes || {}), [key]: nextValue } })
  }

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 16, background: "rgba(255,255,255,0.55)", padding: 14, display: "grid", gap: 12 }}>
      <div>
        <strong>Modo estrutural do projeto</strong>
        <div style={{ marginTop: 4, color: "#475569", fontSize: 13 }}>Define se o livro nasce oficial ou como continuidade/universo oculto promotável.</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
        {PROJECT_MODES.map((mode) => (
          <button key={mode.id} onClick={() => patch({ project_mode: mode.id })} style={{ textAlign: "left", padding: 12, borderRadius: 12, border: mode.id === projectMode ? "2px solid #2F5E2E" : "1px solid #cbd5e1", background: mode.id === projectMode ? "rgba(47,94,46,0.12)" : "#fff", cursor: "pointer" }}>
            <div style={{ fontWeight: 700 }}>{mode.label}</div>
            <div style={{ marginTop: 4, fontSize: 12, color: "#475569" }}>{mode.description}</div>
          </button>
        ))}
      </div>

      <div style={{ padding: 12, borderRadius: 12, border: "1px solid #dbe4d8", background: "rgba(240,253,244,0.85)" }}>
        <strong>{activeMode.label}</strong>
        <div style={{ marginTop: 4, color: "#475569" }}>{activeMode.description}</div>
      </div>

      {isHidden ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
          <div style={{ display: "grid", gap: 6 }}>
            <label>Universo oculto</label>
            <input value={value?.hidden_universe_name || ""} onChange={(e) => patch({ hidden_universe_name: e.target.value })} placeholder="Ex.: Contos da Floresta" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
          </div>
          <div style={{ display: "grid", gap: 6 }}>
            <label>Saga oculta</label>
            <input value={value?.hidden_saga_name || ""} onChange={(e) => patch({ hidden_saga_name: e.target.value })} placeholder="Ex.: Temporada de Outono" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
          </div>
          <div style={{ display: "grid", gap: 6 }}>
            <label>Projeto fonte de continuidade</label>
            <input value={value?.continuity_source_project_id || ""} onChange={(e) => patch({ continuity_source_project_id: e.target.value })} placeholder="ID do projeto fonte (opcional)" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
          </div>
        </div>
      ) : null}

      <div>
        <strong>Submodos por etapa</strong>
        <div style={{ marginTop: 4, color: "#475569", fontSize: 13 }}>Permite, por exemplo: texto manual, imagens automáticas, áudio híbrido e vídeo assistido.</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
        <StageModeSelect label="Texto" value={stageModes.story_input_mode} onChange={(v) => patchStageMode("story_input_mode", v)} />
        <StageModeSelect label="Imagens" value={stageModes.illustration_mode} onChange={(v) => patchStageMode("illustration_mode", v)} />
        <StageModeSelect label="Áudio" value={stageModes.audio_mode} onChange={(v) => patchStageMode("audio_mode", v)} />
        <StageModeSelect label="Vídeo" value={stageModes.video_mode} onChange={(v) => patchStageMode("video_mode", v)} />
      </div>
    </div>
  )
}
