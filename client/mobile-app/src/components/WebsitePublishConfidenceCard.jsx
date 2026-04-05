import { buildWebsitePublishUiState } from "../utils/websitePublishUiState.js"

function StatusPill({ ok, label }) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "6px 10px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 700,
        background: ok ? "rgba(22,163,74,0.12)" : "rgba(220,38,38,0.12)",
        color: ok ? "#166534" : "#991b1b",
        border: `1px solid ${ok ? "rgba(22,163,74,0.25)" : "rgba(220,38,38,0.25)"}`,
      }}
    >
      <span style={{ width: 8, height: 8, borderRadius: 999, background: ok ? "#16a34a" : "#dc2626" }} />
      {label}
    </span>
  )
}

export default function WebsitePublishConfidenceCard({
  selectedProject = null,
  publishStatus = null,
  publicationDetail = null,
  divergence = null,
  lastError = "",
}) {
  const publishUi = buildWebsitePublishUiState({
    selectedProject,
    publishStatus,
    publicationDetail,
    divergence,
    lastError,
  })

  const currentSync = publishUi.currentSync
  const primary = publishUi.primary
  const receipt = publishUi.receipt
  const failure = publishUi.failure

  return (
    <div style={{ display: "grid", gap: 12 }}>
      {failure ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            border: "1px solid rgba(220,38,38,0.25)",
            background: "rgba(254,226,226,0.7)",
            color: "#991b1b",
            display: "grid",
            gap: 6,
          }}
        >
          <div><strong>{failure.label}</strong></div>
          <div>{failure.meaning}</div>
          <div><strong>Próximo passo recomendado:</strong> {failure.nextAction}</div>
        </div>
      ) : null}

      <div
        style={{
          padding: 12,
          borderRadius: 12,
          border: `1px solid ${primary.ok ? "rgba(22,163,74,0.25)" : "rgba(245,158,11,0.35)"}`,
          background: primary.ok ? "rgba(220,252,231,0.7)" : "rgba(255,247,237,0.9)",
          display: "grid",
          gap: 8,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
          <strong>{primary.label}</strong>
          <StatusPill ok={primary.ok} label={primary.ok ? "Estado positivo" : "Atenção necessária"} />
        </div>
        <div><strong>Significado:</strong> {primary.meaning}</div>
        <div><strong>Última atualização:</strong> {currentSync?.synced_at || publicationDetail?.updated_at || publishStatus?.publication_package_frozen_at || "-"}</div>
        <div><strong>Próximo passo recomendado:</strong> {primary.nextAction}</div>
        <div style={{ display: "grid", gap: 6 }}>
          {publishUi.steps.map((step) => (
            <div
              key={step.label}
              style={{
                display: "flex",
                gap: 8,
                alignItems: "center",
                color: step.done ? (step.attention ? "#991b1b" : "#166534") : "#475569",
                fontWeight: step.done ? 700 : 500,
              }}
            >
              <span
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: 999,
                  background: step.done ? (step.attention ? "#dc2626" : "#16a34a") : "#cbd5e1",
                }}
              />
              {step.label}
            </div>
          ))}
        </div>
      </div>

      {receipt ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            border: "1px solid rgba(22,163,74,0.25)",
            background: "rgba(240,253,244,0.9)",
            display: "grid",
            gap: 6,
          }}
        >
          <div><strong>Website confirmou receção</strong></div>
          <div>O Website aceitou a publicação enviada pelo Studio.</div>
          <div><strong>Publication ID:</strong> {receipt.publicationId}</div>
          <div><strong>Variant ID:</strong> {receipt.variantId}</div>
          <div><strong>Recebido em:</strong> {receipt.receivedAt}</div>
          <div><strong>Estado de sync:</strong> {receipt.label}</div>
          <div><strong>Próximo passo recomendado:</strong> {primary.nextAction}</div>
        </div>
      ) : null}
    </div>
  )
}
