import { buildStoryFlowUiState } from "../utils/storyFlowUiState.js"

function toneStyles(tone) {
  if (tone === "positive") {
    return {
      border: "1px solid rgba(22,163,74,0.25)",
      background: "rgba(220,252,231,0.7)",
      color: "#166534",
    }
  }

  return {
    border: "1px solid rgba(245,158,11,0.35)",
    background: "rgba(255,247,237,0.9)",
    color: "#9a3412",
  }
}

function Box({ title, children, tone = "warning" }) {
  const styles = toneStyles(tone)
  return (
    <div style={{ padding: 12, borderRadius: 12, display: "grid", gap: 6, ...styles }}>
      <div><strong>{title}</strong></div>
      {children}
    </div>
  )
}

export default function StoryFlowGuidanceCard({
  storyText = "",
  layoutInfo = null,
  lastAction = "",
  stageMode = "",
}) {
  const ui = buildStoryFlowUiState({ storyText, layoutInfo, lastAction, stageMode })

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <Box title={`Estado atual: ${ui.state.label}`} tone={ui.state.tone}>
        <div><strong>Significado:</strong> {ui.state.meaning}</div>
        <div><strong>Modo atual:</strong> {ui.modeLabel}</div>
        <div><strong>Próximo passo recomendado:</strong> {ui.state.nextAction}</div>
      </Box>

      <Box title="Estado do fluxo de história" tone={ui.state.tone}>
        <div><strong>Texto bruto:</strong> {ui.rawTextPresent ? "Presente" : "Ainda em falta"}</div>
        <div><strong>Edição/paginação:</strong> {ui.shapedStoryPresent ? "Estrutura já iniciada" : "Ainda por estruturar"}</div>
      </Box>

      <Box title={ui.illustrationReadiness.label} tone={ui.illustrationReadiness.tone}>
        <div><strong>Significado:</strong> {ui.illustrationReadiness.meaning}</div>
      </Box>
    </div>
  )
}
