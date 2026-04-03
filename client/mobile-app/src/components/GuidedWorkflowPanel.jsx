import { useMemo } from "react"

const MODES = [
  { id: "manual", label: "Manual", summary: "Tu controlas quase tudo: texto, paginação, outputs e publish." },
  { id: "semi_assisted", label: "Semi assistido", summary: "O Studio sugere e tu validas ou afinas os pontos importantes." },
  { id: "full_assisted", label: "Full assistido", summary: "O Studio corre quase tudo e tu aprovas checkpoints de qualidade." },
  { id: "auto", label: "Automático total", summary: "Pipeline completa com mínimo atrito, ideal quando já há confiança no fluxo." },
]

const STEPS = [
  { id: "login", title: "Entrar no Studio", goal: "Entrar com o utilizador certo e confirmar ligação/backend.", manual: "Escolher utilizador, confirmar ligação e abrir dashboard.", semi_assisted: "O Studio recorda sessão e mostra logo o estado do sistema.", full_assisted: "Entrar e deixar o cockpit carregar tudo automaticamente.", auto: "Sessão e ligação retomadas automaticamente quando possível." },
  { id: "project", title: "Criar ou escolher projeto", goal: "Definir se é IP oficial, standalone ou continuidade oculta.", manual: "Escolher saga/IP, título e língua manualmente.", semi_assisted: "O Studio sugere tipo de projeto e ligações de continuidade.", full_assisted: "Criar projeto a partir de um briefing rápido.", auto: "Projeto nasce logo no modo certo a partir do fluxo base configurado." },
  { id: "story", title: "Texto e estrutura", goal: "Inserir texto, definir título e preparar a base editorial.", manual: "Colar/escrever texto no Story Source e decidir tudo à mão.", semi_assisted: "O Studio sugere título, resumo e continuidade com base no texto.", full_assisted: "O Studio organiza texto, prepara estrutura e variantes base.", auto: "O Studio gera a história completa a partir da instrução macro definida." },
  { id: "continuity", title: "Continuidade e tipografia", goal: "Definir universo/saga ocultos, personagens recorrentes e fonte editorial.", manual: "Escolher projeto fonte, personagens, universo oculto e fonte.", semi_assisted: "O Studio sugere nomes e herança tipográfica.", full_assisted: "O Studio propõe continuidade e tipografia coerentes com o conteúdo.", auto: "A continuidade e tipografia vêm do preset/editorial profile configurado." },
  { id: "translation", title: "Traduções e paginação", goal: "Gerar idiomas, paginar e afinar visualmente as páginas.", manual: "Traduzir/rever e paginar página a página.", semi_assisted: "O Studio gera tradução e paginação e tu corriges o necessário.", full_assisted: "O Studio traduz e pagina, ficando tu com validação final.", auto: "Idiomas e layout são gerados automaticamente pelo pipeline." },
  { id: "media", title: "Ilustração, vozes e créditos", goal: "Fechar capa, assets, casting e contributors.", manual: "Escolher tudo manualmente e rever um a um.", semi_assisted: "O Studio sugere visuais, vozes e créditos por contexto.", full_assisted: "O Studio prepara a frente multimédia quase toda.", auto: "Assets e casting seguem o preset de produção configurado." },
  { id: "outputs", title: "Outputs e publicação", goal: "Gerar outputs, validar readiness, congelar package e publicar.", manual: "Correr EPUB, audiobook, vídeo e publish passo a passo.", semi_assisted: "O Studio corre a pipeline e tu aprovas readiness e publish.", full_assisted: "O Studio gera, valida e deixa o publish pronto para um clique.", auto: "O Studio leva o projeto até Website Control com mínima intervenção." },
]

function ModePill({ active, label, onClick }) {
  return <button onClick={onClick} style={{ padding: "8px 12px", borderRadius: 999, border: active ? "2px solid #2F5E2E" : "1px solid #cbd5e1", background: active ? "rgba(47,94,46,0.12)" : "#fff", color: "#111827", fontWeight: 700, cursor: "pointer" }}>{label}</button>
}

export default function GuidedWorkflowPanel({ settings, onToggleGuidedMode, onChangeGuidedMode }) {
  const mode = settings?.guided_workflow_mode || "semi_assisted"
  const activeMode = useMemo(() => MODES.find((item) => item.id === mode) || MODES[1], [mode])

  return (
    <div style={{ border: "1px solid rgba(255,255,255,0.25)", borderRadius: 16, background: "rgba(255,255,255,0.84)", backdropFilter: "blur(8px)", padding: 16, display: "grid", gap: 12, boxShadow: "0 10px 24px rgba(0,0,0,0.10)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <h3 style={{ margin: 0, color: "#2F5E2E" }}>Fluxo guiado do Studio</h3>
          <div style={{ fontSize: 13, color: "#475569" }}>Modo opcional para quem quer seguir o processo passo a passo sem se perder.</div>
        </div>
        <button onClick={onToggleGuidedMode} style={{ padding: "10px 12px", borderRadius: 12, border: "1px solid #cbd5e1", background: "#fff", fontWeight: 700, cursor: "pointer" }}>Desligar modo guiado</button>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {MODES.map((item) => <ModePill key={item.id} label={item.label} active={item.id === activeMode.id} onClick={() => onChangeGuidedMode?.(item.id)} />)}
      </div>

      <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
        <strong>{activeMode.label}</strong>
        <div style={{ marginTop: 6, color: "#475569" }}>{activeMode.summary}</div>
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        {STEPS.map((step, index) => (
          <div key={step.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
            <div><strong>{index + 1}. {step.title}</strong></div>
            <div style={{ color: "#334155" }}>{step.goal}</div>
            <div style={{ fontSize: 13, color: "#475569" }}>{step[activeMode.id]}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
