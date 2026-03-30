import { useEffect, useState } from "react"
import {
  getWebsiteVisualSetReconcile,
  getWebsiteVisualSetsStatus,
  listSagaVisualSets,
  publishAllSagaVisualSetsToWebsite,
  publishSagaVisualSetToWebsite,
  updateSagaVisualSet,
} from "../api.js"

function canCommercial(user) {
  const role = String(user?.role || "").toLowerCase()
  const name = String(user?.name || "").toLowerCase()
  return ["owner", "creator", "admin"].includes(role) || ["andré", "andre", "esposa", "wife", "mama"].includes(name)
}

function ActionButton({ children, onClick, disabled = false, tone = "primary" }) {
  const palette = tone === "secondary"
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

function reconcileBadge(status) {
  if (status === "in_sync") return { label: "Em sync", background: "rgba(220,252,231,0.8)", color: "#166534" }
  if (status === "diverged") return { label: "Divergiu", background: "rgba(254,249,195,0.85)", color: "#854d0e" }
  return { label: "Falta no Website", background: "rgba(254,226,226,0.85)", color: "#991b1b" }
}

export default function VisualSetsPanel({ user }) {
  const [items, setItems] = useState([])
  const [websiteItems, setWebsiteItems] = useState([])
  const [reconcileReport, setReconcileReport] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    refreshAll()
  }, [])

  async function loadLocal() {
    const response = await listSagaVisualSets()
    setItems(response?.items || [])
  }

  async function loadWebsite() {
    try {
      const response = await getWebsiteVisualSetsStatus()
      setWebsiteItems(response?.items || [])
    } catch {
      setWebsiteItems([])
    }
  }

  async function loadReconcile() {
    try {
      const response = await getWebsiteVisualSetReconcile()
      setReconcileReport(response?.report || [])
    } catch {
      setReconcileReport([])
    }
  }

  async function refreshAll() {
    setLoading(true)
    try {
      await Promise.all([loadLocal(), loadWebsite(), loadReconcile()])
    } finally {
      setLoading(false)
    }
  }

  async function handleToggleActive(item) {
    if (!canCommercial(user)) {
      alert("Sem permissão comercial.")
      return
    }
    setLoading(true)
    try {
      await updateSagaVisualSet(item.id, { active: !Boolean(item?.active) })
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Falha ao atualizar visual set.")
    } finally {
      setLoading(false)
    }
  }

  async function handlePublish(item) {
    if (!canCommercial(user)) {
      alert("Sem permissão comercial.")
      return
    }
    setLoading(true)
    try {
      await publishSagaVisualSetToWebsite(item.id)
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Falha ao publicar visual set.")
    } finally {
      setLoading(false)
    }
  }

  async function handlePublishAll() {
    if (!canCommercial(user)) {
      alert("Sem permissão comercial.")
      return
    }
    setLoading(true)
    try {
      await publishAllSagaVisualSetsToWebsite()
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Falha ao publicar visual sets.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ border: "1px solid rgba(255,255,255,0.25)", borderRadius: 16, background: "rgba(255,255,255,0.84)", backdropFilter: "blur(8px)", padding: 16, display: "grid", gap: 12, boxShadow: "0 10px 24px rgba(0,0,0,0.10)" }}>
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>Visual sets / Saga media</h3>

      <div style={{ display: "grid", gap: 8, padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
        <div><strong>Autoridade visual</strong></div>
        <div>O Studio é a source of truth dos visual sets por saga. O Website persiste e serve runtime público.</div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <ActionButton onClick={refreshAll} disabled={loading} tone="secondary">Atualizar estado</ActionButton>
          <ActionButton onClick={handlePublishAll} disabled={loading || !canCommercial(user)}>Publicar tudo no Website</ActionButton>
        </div>
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        <div><strong>Visual sets no Studio</strong></div>
        {items.length === 0 ? <div>Sem visual sets no Studio ainda.</div> : null}
        {items.map((item) => (
          <div key={item.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
            <div><strong>{item.display_name}</strong> ({item.saga_slug})</div>
            <div>Versão: {item.version} · Ativo: {item.active ? "Sim" : "Não"}</div>
            <div>Slots: {Object.keys(item.slots || {}).join(", ") || "-"}</div>
            <div>Último publish: {item.publish_state?.published_at || "-"}</div>
            <div>Status local: {item.publish_state?.status || "por publicar"}</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <ActionButton onClick={() => handleToggleActive(item)} disabled={loading || !canCommercial(user)} tone="secondary">{item.active ? "Desativar" : "Ativar"}</ActionButton>
              <ActionButton onClick={() => handlePublish(item)} disabled={loading || !canCommercial(user)}>Publicar no Website</ActionButton>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        <div><strong>Visual sets materializados no Website</strong></div>
        {websiteItems.length === 0 ? <div>Sem visual sets materializados ainda.</div> : null}
        {websiteItems.map((item) => (
          <div key={item.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
            <div><strong>{item.display_name}</strong> ({item.saga_slug})</div>
            <div>Versão: {item.version} · Ativo: {item.active ? "Sim" : "Não"}</div>
            <div>Slots: {Object.keys(item.slots || {}).join(", ") || "-"}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        <div><strong>Reconcile Studio ↔ Website</strong></div>
        {reconcileReport.length === 0 ? <div>Sem relatório de reconcile ainda.</div> : null}
        {reconcileReport.map((item) => {
          const badge = reconcileBadge(item.status)
          return (
            <div key={item.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <strong>{item.local?.display_name || item.id}</strong>
                <span style={{ padding: "6px 10px", borderRadius: 999, background: badge.background, color: badge.color, fontWeight: 700, fontSize: 12 }}>{badge.label}</span>
              </div>
              <div>Local: slots {item.local?.slots_count || 0} · versão {item.local?.version || 0}</div>
              <div>Website: {item.website ? `slots ${item.website.slots_count || 0} · versão ${item.website.version || 0}` : "Ainda não materializado"}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
