import { useEffect, useMemo, useState } from "react"
import {
  getWebsiteControlCatalog,
  getWebsiteControlSummary,
  getWebsitePublishEnvelope,
  getWebsitePublishStatus,
  publishProjectToWebsite,
} from "../api.js"

function canPublish(user) {
  const role = String(user?.role || "").toLowerCase()
  const name = String(user?.name || "").toLowerCase()
  return ["owner", "creator", "admin"].includes(role) || ["andré", "andre", "esposa", "wife", "mama"].includes(name)
}

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
      <span
        style={{
          width: 8,
          height: 8,
          borderRadius: 999,
          background: ok ? "#16a34a" : "#dc2626",
        }}
      />
      {label}
    </span>
  )
}

function ActionButton({ children, onClick, disabled = false, tone = "primary" }) {
  const palette = tone === "danger"
    ? { background: "#991b1b", color: "#fff" }
    : tone === "secondary"
      ? { background: "#fff", color: "#111827", border: "1px solid #cbd5e1" }
      : { background: "#2F5E2E", color: "#fff" }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        padding: "10px 12px",
        borderRadius: 12,
        border: palette.border || "none",
        background: disabled ? "#94a3b8" : palette.background,
        color: palette.color,
        fontWeight: 700,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.75 : 1,
      }}
    >
      {children}
    </button>
  )
}

function SectionCard({ title, children, extra = null }) {
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
        boxShadow: "0 10px 24px rgba(0,0,0,0.10)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <h3 style={{ margin: 0, color: "#2F5E2E" }}>{title}</h3>
        {extra}
      </div>
      {children}
    </div>
  )
}

export default function WebsiteControlPanel({ user, projects = [], onReload }) {
  const [summary, setSummary] = useState(null)
  const [catalog, setCatalog] = useState(null)
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [publishStatus, setPublishStatus] = useState(null)
  const [publishEnvelope, setPublishEnvelope] = useState(null)
  const [busy, setBusy] = useState(false)
  const [busyLabel, setBusyLabel] = useState("")
  const [lastError, setLastError] = useState("")

  useEffect(() => {
    loadWebsiteData()
  }, [])

  useEffect(() => {
    if (!selectedProjectId && projects.length) {
      setSelectedProjectId(projects[0].id)
    }
  }, [projects, selectedProjectId])

  useEffect(() => {
    if (!selectedProjectId) return
    refreshProjectStatus(selectedProjectId)
  }, [selectedProjectId])

  const selectedProject = useMemo(
    () => projects.find((item) => item.id === selectedProjectId) || null,
    [projects, selectedProjectId]
  )

  async function loadWebsiteData() {
    setBusy(true)
    setBusyLabel("A sincronizar painel do Website...")
    setLastError("")
    try {
      const [summaryRes, catalogRes] = await Promise.all([
        getWebsiteControlSummary(),
        getWebsiteControlCatalog({ limit: 12, activeOnly: false }),
      ])
      setSummary(summaryRes?.website || summaryRes || null)
      setCatalog(catalogRes?.website || catalogRes || null)
    } catch (error) {
      setLastError(error?.message || "Falha ao carregar painel do Website.")
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function refreshProjectStatus(projectId) {
    if (!projectId) return
    setBusy(true)
    setBusyLabel("A consultar estado de publicação...")
    setLastError("")
    try {
      const [statusRes, envelopeRes] = await Promise.all([
        getWebsitePublishStatus(projectId),
        getWebsitePublishEnvelope(projectId),
      ])
      setPublishStatus(statusRes || null)
      setPublishEnvelope(envelopeRes?.envelope || null)
    } catch (error) {
      setPublishStatus(null)
      setPublishEnvelope(null)
      setLastError(error?.message || "Falha ao carregar estado de publicação.")
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handlePublishSelectedProject() {
    if (!selectedProjectId) {
      alert("Seleciona um projeto primeiro.")
      return
    }

    if (!canPublish(user)) {
      alert("Sem permissão para publicar no Website.")
      return
    }

    setBusy(true)
    setBusyLabel("A publicar snapshot no Website...")
    setLastError("")
    try {
      const result = await publishProjectToWebsite(selectedProjectId)
      alert(`Projeto publicado no Website. Publication: ${result?.receipt?.publication_id || "-"}`)
      await refreshProjectStatus(selectedProjectId)
      await loadWebsiteData()
      if (typeof onReload === "function") {
        await onReload()
      }
    } catch (error) {
      const message = error?.message || "Falha ao publicar no Website."
      setLastError(message)
      alert(message)
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  const counters = summary?.counters || {}
  const recentPublications = summary?.recent_publications || []
  const recentProducts = summary?.recent_products || []
  const catalogItems = catalog?.items || []
  const currentSync = selectedProject?.website_sync || publishStatus?.website_sync || null

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <SectionCard
        title="Website Control Center"
        extra={
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <StatusPill ok={!lastError} label={lastError ? "Com falhas" : "Ligado ao Website"} />
            <ActionButton onClick={loadWebsiteData} disabled={busy} tone="secondary">
              {busy ? busyLabel || "A atualizar..." : "Atualizar Website"}
            </ActionButton>
          </div>
        }
      >
        <div className="grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12 }}>
          <div className="card" style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}><div className="muted">IPs</div><strong>{counters.ips || 0}</strong></div>
          <div className="card" style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}><div className="muted">Publicações</div><strong>{counters.publications || 0}</strong></div>
          <div className="card" style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}><div className="muted">Variantes</div><strong>{counters.variants || 0}</strong></div>
          <div className="card" style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}><div className="muted">Produtos</div><strong>{counters.products || 0}</strong></div>
          <div className="card" style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}><div className="muted">Produtos ativos</div><strong>{counters.active_products || 0}</strong></div>
          <div className="card" style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}><div className="muted">Pedidos pagos</div><strong>{counters.paid_orders || 0}</strong></div>
        </div>

        {summary?.checked_at ? (
          <div style={{ fontSize: 12, color: "#475569" }}>
            Última leitura do Website: {summary.checked_at}
          </div>
        ) : null}

        {lastError ? (
          <div style={{ padding: 12, borderRadius: 12, border: "1px solid rgba(220,38,38,0.25)", background: "rgba(254,226,226,0.7)", color: "#991b1b", fontWeight: 600 }}>
            {lastError}
          </div>
        ) : null}
      </SectionCard>

      <SectionCard title="Publicar e sincronizar Website">
        <div style={{ display: "grid", gap: 10 }}>
          <label>Projeto a controlar/publicar</label>
          <select
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
          >
            <option value="">Selecionar projeto</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.title} · {project.language} · {project.saga_name}
              </option>
            ))}
          </select>

          {selectedProject ? (
            <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
              <div><strong>{selectedProject.title}</strong></div>
              <div>Projeto: {selectedProject.id}</div>
              <div>IP: {selectedProject.saga_name} ({selectedProject.saga_slug})</div>
              <div>Língua: {selectedProject.language}</div>
              <div>Pronto para publicar: {selectedProject.ready_for_publish ? "Sim" : "Não"}</div>
            </div>
          ) : null}

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <ActionButton onClick={() => refreshProjectStatus(selectedProjectId)} disabled={busy || !selectedProjectId} tone="secondary">
              Atualizar estado
            </ActionButton>
            <ActionButton onClick={handlePublishSelectedProject} disabled={busy || !selectedProjectId}>
              Publicar no Website
            </ActionButton>
          </div>

          {currentSync ? (
            <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
              <div><strong>Último sync guardado no Studio</strong></div>
              <div>OK: {currentSync.ok ? "Sim" : "Não"}</div>
              <div>Publication ID: {currentSync.publication_id || "-"}</div>
              <div>Variant ID: {currentSync.variant_id || "-"}</div>
              <div>Checksum: {currentSync.checksum || "-"}</div>
              <div>Publicado em: {currentSync.published_at || "-"}</div>
              <div>Sincronizado em: {currentSync.synced_at || "-"}</div>
            </div>
          ) : null}

          {publishEnvelope ? (
            <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
              <div><strong>Envelope pronto para Website</strong></div>
              <div>Schema: {publishEnvelope.schema_version || "website_ingest_v1"}</div>
              <div>Publication ID: {publishEnvelope.publication_id || "-"}</div>
              <div>Variant ID: {publishEnvelope.variant_id || "-"}</div>
              <div>Projeto: {publishEnvelope.project_id || "-"}</div>
            </div>
          ) : null}
        </div>
      </SectionCard>

      <SectionCard title="Últimas publicações recebidas pelo Website">
        <div style={{ display: "grid", gap: 10 }}>
          {recentPublications.length === 0 ? <div>Sem publicações recentes.</div> : null}
          {recentPublications.map((item) => (
            <div key={item.publication_id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
              <div><strong>{item.ip_name || item.ip_slug || "IP"}</strong> — {item.project_slug || item.project_id}</div>
              <div>Publication: {item.publication_id}</div>
              <div>Canal: {item.channel} · Língua: {item.language} · Estado: {item.status}</div>
              <div>Variantes: {(item.variants || []).map((variant) => `${variant.format}/${variant.language}`).join(", ") || "-"}</div>
              <div>Atualizado em: {item.updated_at}</div>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Catálogo live do Website">
        <div style={{ display: "grid", gap: 10 }}>
          {catalogItems.length === 0 ? <div>Sem itens no catálogo live.</div> : null}
          {catalogItems.map((item) => (
            <div key={item.product_id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
              <div><strong>{item.title}</strong></div>
              <div>Produto: {item.slug}</div>
              <div>Tipo: {item.type} · {item.currency} · {(Number(item.price_cents || 0) / 100).toFixed(2)}</div>
              <div>Projeto: {item.variant?.project_id || "-"} · Variant: {item.variant?.variant_id || "-"}</div>
              <div>IP: {item.publication?.ip_name || item.publication?.ip_slug || "-"}</div>
              <div>Ativo: {item.active ? "Sim" : "Não"} · Featured: {item.featured ? "Sim" : "Não"}</div>
              <div>Assets: {(item.asset_roles || []).join(", ") || "-"}</div>
            </div>
          ))}
        </div>

        {recentProducts.length ? (
          <div style={{ display: "grid", gap: 8 }}>
            <div><strong>Últimos produtos tocados no Website</strong></div>
            {recentProducts.map((item) => (
              <div key={item.id} style={{ fontSize: 13, color: "#334155" }}>
                {item.title} · {item.slug} · {item.type} · {item.updated_at}
              </div>
            ))}
          </div>
        ) : null}
      </SectionCard>
    </div>
  )
}
