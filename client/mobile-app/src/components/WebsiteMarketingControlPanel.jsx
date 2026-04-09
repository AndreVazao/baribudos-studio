import { useEffect, useMemo, useState } from "react"
import {
  getProjectCommercial,
  getWebsitePublishStatus,
  listProjects,
  publishProjectToWebsite,
  revalidateProjectOnWebsite,
  unpublishProjectOnWebsite,
  updateProjectCommercial,
} from "../api.js"

const PUBLIC_STATES = [
  "private",
  "internal_review",
  "teaser_ready",
  "prelaunch_public",
  "launch_ready",
  "published",
  "archived",
]

const EMPTY_MARKETING = {
  public_state: "private",
  teaser_badge: "Em breve",
  teaser_headline: "",
  teaser_subtitle: "",
  teaser_cta_label: "Ver novidades",
  teaser_release_label: "",
  teaser_gallery: [],
  teaser_cover_url: "",
  teaser_trailer_url: "",
  teaser_excerpt: "",
  teaser_visibility_notes: "",
  prelaunch_enabled: false,
  share_preview_images_during_production: true,
}

function Card({ title, children, extra = null }) {
  return (
    <div style={{ border: "1px solid rgba(255,255,255,0.25)", borderRadius: 16, background: "rgba(255,255,255,0.84)", backdropFilter: "blur(8px)", padding: 16, display: "grid", gap: 12, boxShadow: "0 10px 24px rgba(0,0,0,0.10)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <h3 style={{ margin: 0, color: "#2F5E2E" }}>{title}</h3>
        {extra}
      </div>
      {children}
    </div>
  )
}

function ActionButton({ children, onClick, disabled = false, tone = "primary" }) {
  const palette =
    tone === "danger"
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
      }}
    >
      {children}
    </button>
  )
}

function parseLines(value) {
  return String(value || "")
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function toTextarea(value) {
  return Array.isArray(value) ? value.join("\n") : ""
}

export default function WebsiteMarketingControlPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [commercial, setCommercial] = useState({})
  const [marketing, setMarketing] = useState(EMPTY_MARKETING)
  const [publishStatus, setPublishStatus] = useState(null)
  const [busy, setBusy] = useState(false)
  const [busyLabel, setBusyLabel] = useState("")

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) refreshProject(selectedProjectId)
  }, [selectedProjectId])

  const selectedProject = useMemo(
    () => projects.find((item) => item.id === selectedProjectId) || null,
    [projects, selectedProjectId]
  )

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) setSelectedProjectId(list[0].id)
  }

  async function refreshProject(projectId) {
    setBusy(true)
    setBusyLabel("A sincronizar marketing do Website...")
    try {
      const [commercialRes, statusRes] = await Promise.all([
        getProjectCommercial(projectId).catch(() => ({ commercial: {} })),
        getWebsitePublishStatus(projectId).catch(() => null),
      ])

      const nextCommercial = commercialRes?.commercial || {}
      const nextMarketing = {
        ...EMPTY_MARKETING,
        ...(nextCommercial?.website_marketing || nextCommercial?.marketing || {}),
      }

      setCommercial(nextCommercial)
      setMarketing(nextMarketing)
      setPublishStatus(statusRes || null)
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  function updateMarketing(patch) {
    setMarketing((current) => ({ ...current, ...patch }))
  }

  async function handleSaveMarketing() {
    if (!selectedProjectId) return

    setBusy(true)
    setBusyLabel("A guardar controlo de marketing...")
    try {
      const payload = {
        ...commercial,
        website_marketing: {
          ...marketing,
          teaser_gallery: Array.isArray(marketing.teaser_gallery)
            ? marketing.teaser_gallery
            : parseLines(marketing.teaser_gallery),
        },
      }

      await updateProjectCommercial(selectedProjectId, payload, user)
      await refreshProject(selectedProjectId)
      alert("Controlo de marketing do Website guardado.")
    } catch (error) {
      alert(error?.message || "Erro ao guardar controlo de marketing.")
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handlePublishTeaser() {
    if (!selectedProjectId) return
    setBusy(true)
    setBusyLabel("A publicar pré-lançamento no Website...")
    try {
      await updateProjectCommercial(selectedProjectId, {
        ...commercial,
        website_marketing: {
          ...marketing,
          public_state: "prelaunch_public",
          prelaunch_enabled: true,
        },
      }, user)
      await publishProjectToWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Pré-lançamento empurrado para o Website.")
    } catch (error) {
      alert(error?.message || "Erro ao publicar pré-lançamento no Website.")
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handlePromoteLaunch() {
    if (!selectedProjectId) return
    setBusy(true)
    setBusyLabel("A promover para lançamento...")
    try {
      await updateProjectCommercial(selectedProjectId, {
        ...commercial,
        website_marketing: {
          ...marketing,
          public_state: "published",
          prelaunch_enabled: false,
        },
      }, user)
      await publishProjectToWebsite(selectedProjectId)
      await revalidateProjectOnWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Projeto promovido para lançamento final no Website.")
    } catch (error) {
      alert(error?.message || "Erro ao promover lançamento no Website.")
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handleWithdrawPublicSurface() {
    if (!selectedProjectId) return
    setBusy(true)
    setBusyLabel("A retirar superfície pública...")
    try {
      await updateProjectCommercial(selectedProjectId, {
        ...commercial,
        website_marketing: {
          ...marketing,
          public_state: "private",
          prelaunch_enabled: false,
        },
      }, user)
      await unpublishProjectOnWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Superfície pública retirada do Website.")
    } catch (error) {
      alert(error?.message || "Erro ao retirar superfície pública.")
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  const websiteSync = publishStatus?.website_sync || selectedProject?.website_sync || null

  return (
    <Card
      title="Website Marketing Control"
      extra={<ActionButton onClick={() => refreshProject(selectedProjectId)} disabled={busy || !selectedProjectId} tone="secondary">{busy ? busyLabel || "A atualizar..." : "Atualizar"}</ActionButton>}
    >
      <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(248,250,252,0.9)", color: "#334155" }}>
        O Studio decide o que fica privado, teaser, pré-lançamento ou lançamento final. O Website só expõe a superfície pública escolhida aqui.
      </div>

      <label>Projeto</label>
      <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
        <option value="">Selecionar projeto</option>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>{project.title} — {project.saga_name}</option>
        ))}
      </select>

      {selectedProject ? (
        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
          <div><strong>{selectedProject.title}</strong></div>
          <div>IP: {selectedProject.saga_name} ({selectedProject.saga_slug})</div>
          <div>Ready for publish: {selectedProject.ready_for_publish ? "Sim" : "Não"}</div>
          <div>Estado público atual: {marketing.public_state}</div>
          <div>Pré-lançamento ativo: {marketing.prelaunch_enabled ? "Sim" : "Não"}</div>
        </div>
      ) : null}

      <label>Estado público</label>
      <select value={marketing.public_state} onChange={(e) => updateMarketing({ public_state: e.target.value })} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
        {PUBLIC_STATES.map((value) => <option key={value} value={value}>{value}</option>)}
      </select>

      <label><input type="checkbox" checked={!!marketing.prelaunch_enabled} onChange={(e) => updateMarketing({ prelaunch_enabled: e.target.checked })} /> Pré-lançamento público ativo</label>
      <label><input type="checkbox" checked={marketing.share_preview_images_during_production !== false} onChange={(e) => updateMarketing({ share_preview_images_during_production: e.target.checked })} /> Permitir partilhar imagens teaser durante produção</label>

      <label>Badge teaser</label>
      <input value={marketing.teaser_badge || ""} onChange={(e) => updateMarketing({ teaser_badge: e.target.value })} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <label>Headline teaser</label>
      <input value={marketing.teaser_headline || ""} onChange={(e) => updateMarketing({ teaser_headline: e.target.value })} placeholder="Ex.: Uma nova aventura Baribudos está a chegar" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <label>Subheadline teaser</label>
      <textarea value={marketing.teaser_subtitle || ""} onChange={(e) => updateMarketing({ teaser_subtitle: e.target.value })} rows={3} style={{ width: "100%", padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />

      <label>CTA teaser</label>
      <input value={marketing.teaser_cta_label || ""} onChange={(e) => updateMarketing({ teaser_cta_label: e.target.value })} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <label>Texto de lançamento</label>
      <input value={marketing.teaser_release_label || ""} onChange={(e) => updateMarketing({ teaser_release_label: e.target.value })} placeholder="Ex.: Lançamento em breve" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <label>Imagem teaser principal (URL/asset path)</label>
      <input value={marketing.teaser_cover_url || ""} onChange={(e) => updateMarketing({ teaser_cover_url: e.target.value })} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <label>Trailer teaser (URL/asset path)</label>
      <input value={marketing.teaser_trailer_url || ""} onChange={(e) => updateMarketing({ teaser_trailer_url: e.target.value })} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

      <label>Galeria teaser (uma imagem por linha)</label>
      <textarea value={toTextarea(marketing.teaser_gallery)} onChange={(e) => updateMarketing({ teaser_gallery: parseLines(e.target.value) })} rows={4} style={{ width: "100%", padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />

      <label>Excerto público</label>
      <textarea value={marketing.teaser_excerpt || ""} onChange={(e) => updateMarketing({ teaser_excerpt: e.target.value })} rows={4} style={{ width: "100%", padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />

      <label>Notas de visibilidade</label>
      <textarea value={marketing.teaser_visibility_notes || ""} onChange={(e) => updateMarketing({ teaser_visibility_notes: e.target.value })} rows={3} style={{ width: "100%", padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <ActionButton onClick={handleSaveMarketing} disabled={busy || !selectedProjectId}>Guardar controlo marketing</ActionButton>
        <ActionButton onClick={handlePublishTeaser} disabled={busy || !selectedProjectId} tone="secondary">Publicar pré-lançamento</ActionButton>
        <ActionButton onClick={handlePromoteLaunch} disabled={busy || !selectedProjectId}>Promover para lançamento</ActionButton>
        <ActionButton onClick={handleWithdrawPublicSurface} disabled={busy || !selectedProjectId} tone="danger">Retirar do Website</ActionButton>
      </div>

      {websiteSync ? (
        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
          <div><strong>Último sync Website</strong></div>
          <div>Publication ID: {websiteSync.publication_id || "-"}</div>
          <div>Checksum: {websiteSync.checksum || "-"}</div>
          <div>Publicado em: {websiteSync.published_at || "-"}</div>
          <div>Último unpublish: {websiteSync.unpublished_at || "-"}</div>
          <div>Última revalidate: {websiteSync.last_revalidate_at || "-"}</div>
        </div>
      ) : null}
    </Card>
  )
}
