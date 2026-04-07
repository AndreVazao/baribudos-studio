import { buildWebsiteControlMeaningUiState } from "../utils/websiteControlMeaningUiState.js"

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

export default function WebsiteControlMeaningCard({ health = null, publicationDetail = null, divergence = null, lastError = "" }) {
  const ui = buildWebsiteControlMeaningUiState({ health, publicationDetail, divergence, lastError })

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <Box title={`Estado do Website: ${ui.healthState.label}`} tone={ui.healthState.tone}>
        <div><strong>Significado:</strong> {ui.healthState.meaning}</div>
        <div><strong>Próximo passo recomendado:</strong> {ui.healthState.nextAction}</div>
      </Box>

      <Box title={`Estado da publicação: ${ui.publicationState.label}`} tone={ui.publicationState.tone}>
        <div><strong>Significado:</strong> {ui.publicationState.meaning}</div>
        <div><strong>Próximo passo recomendado:</strong> {ui.publicationState.nextAction}</div>
      </Box>

      <Box title={`Divergência / reconcile: ${ui.divergenceState.label}`} tone={ui.divergenceState.tone}>
        <div><strong>Significado:</strong> {ui.divergenceState.meaning}</div>
        {ui.divergenceState.reasons?.length ? (
          <div style={{ display: "grid", gap: 4 }}>
            {ui.divergenceState.reasons.map((reason) => (
              <div key={reason}>- {reason}</div>
            ))}
          </div>
        ) : null}
        <div><strong>Próximo passo recomendado:</strong> {ui.divergenceState.nextAction}</div>
      </Box>
    </div>
  )
}
