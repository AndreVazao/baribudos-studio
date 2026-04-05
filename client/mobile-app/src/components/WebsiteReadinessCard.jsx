import { buildWebsiteReadinessUiState } from "../utils/websiteReadinessUiState.js"

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

function SectionBox({ title, children, tone = "warning" }) {
  const styles = toneStyles(tone)
  return (
    <div style={{ padding: 12, borderRadius: 12, display: "grid", gap: 6, ...styles }}>
      <div><strong>{title}</strong></div>
      {children}
    </div>
  )
}

export default function WebsiteReadinessCard({ selectedProject = null, publishStatus = null }) {
  const ui = buildWebsiteReadinessUiState({ selectedProject, publishStatus })

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <SectionBox title={`Estado de readiness: ${ui.readiness.label}`} tone={ui.readiness.tone}>
        <div><strong>Significado:</strong> {ui.readiness.meaning}</div>
        <div><strong>Package:</strong> {ui.packageFrozen ? "Congelado" : "Não congelado"}</div>
        <div><strong>Ready técnico do projeto:</strong> {ui.readyForPublish ? "Sim" : "Não"}</div>
        <div><strong>Próximo passo recomendado:</strong> {ui.readiness.nextAction}</div>
      </SectionBox>

      {ui.blockers.length > 0 ? (
        <SectionBox title="Bloqueia publicação" tone="warning">
          {ui.blockers.map((item) => (
            <div key={item}>- {item}</div>
          ))}
        </SectionBox>
      ) : (
        <SectionBox title="Bloqueia publicação" tone="positive">
          <div>Sem bloqueios obrigatórios.</div>
        </SectionBox>
      )}

      {ui.optionalImprovements.length > 0 ? (
        <SectionBox title="Melhorias opcionais" tone="neutral">
          {ui.optionalImprovements.map((item) => (
            <div key={item}>- {item}</div>
          ))}
          <div><strong>Significado:</strong> Estas melhorias aumentam qualidade/comercialização, mas não bloqueiam publicação.</div>
        </SectionBox>
      ) : (
        <SectionBox title="Melhorias opcionais" tone="neutral">
          <div>Sem melhorias opcionais pendentes.</div>
        </SectionBox>
      )}

      <SectionBox title={`Contrato Website: ${ui.contractMeaning.label}`} tone={ui.contractMeaning.tone}>
        <div><strong>Significado:</strong> {ui.contractMeaning.meaning}</div>
        <div><strong>Estado bruto:</strong> {ui.publicationPolicy?.contract?.status || "-"} · score {ui.publicationPolicy?.contract?.score_percent || 0}%</div>
      </SectionBox>
    </div>
  )
}
