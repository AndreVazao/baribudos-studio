import { buildVoiceUsageUiState } from "../utils/voiceUsageUiState.js"

function toneStyles(tone) {
  if (tone === "positive") {
    return {
      border: "1px solid rgba(22,163,74,0.25)",
      background: "rgba(220,252,231,0.7)",
      color: "#166534",
    }
  }

  if (tone === "neutral") {
    return {
      border: "1px solid rgba(59,130,246,0.25)",
      background: "rgba(239,246,255,0.85)",
      color: "#1d4ed8",
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

export default function VoiceUsageGuidanceCard({ profile = null }) {
  const ui = buildVoiceUsageUiState(profile || {})

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <Box title={`Tipo de voz: ${ui.voiceTypeLabel}`} tone={ui.usage.tone}>
        <div><strong>Dono real:</strong> {ui.realOwner}</div>
        <div><strong>Nome para créditos:</strong> {ui.creditedName}</div>
        {ui.linkedOriginal ? <div><strong>Ligação original:</strong> {ui.linkedOriginal}</div> : null}
      </Box>

      <Box title={ui.usage.label} tone={ui.usage.tone}>
        <div><strong>Significado:</strong> {ui.usage.meaning}</div>
        <div><strong>Próximo passo recomendado:</strong> {ui.nextAction}</div>
      </Box>
    </div>
  )
}
