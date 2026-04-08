import { useEffect, useMemo, useState } from "react"
import {
  getDbControlReadiness,
  getDbControlStatus,
  getDeployControlVercelSummary,
  getWebsiteControlCatalog,
  getWebsiteControlDivergence,
  getWebsiteControlHealth,
  getWebsiteControlPublication,
  getWebsiteControlSummary,
  getWebsitePublishEnvelope,
  getWebsitePublishStatus,
  publishProjectToWebsite,
  revalidateProjectOnWebsite,
  unpublishProjectOnWebsite,
  updateWebsiteProductPricing,
  updateWebsiteProductVisibility,
} from "../api.js"
import WebsitePublishConfidenceCard from "./WebsitePublishConfidenceCard.jsx"
import WebsiteReadinessCard from "./WebsiteReadinessCard.jsx"

function canPublish(user) {
  const role = String(user?.role || "").toLowerCase()
  const name = String(user?.name || "").toLowerCase()
  return ["owner", "creator", "admin"].includes(role) || ["andré", "andre", "esposa", "wife", "mama"].includes(name)
}

function isStructuralOwner(user) {
  const role = String(user?.role || "").toLowerCase()
  const name = String(user?.name || "").toLowerCase()
  return role === "owner" || ["andré", "andre"].includes(name)
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
      <span style={{ width: 8, height: 8, borderRadius: 999, background: ok ? "#16a34a" : "#dc2626" }} />
      {label}
    </span>
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

function SmallInfoCard({ label, value }) {
  return (
    <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
      <div className="muted">{label}</div>
      <strong>{value}</strong>
    </div>
  )
}

export default function WebsiteControlPanel({ user, projects = [], onReload }) {
  const [health, setHealth] = useState(null)
  const [summary, setSummary] = useState(null)
  const [catalog, setCatalog] = useState(null)
  const [deploySummary, setDeploySummary] = useState(null)
  const [dbStatus, setDbStatus] = useState(null)
  const [dbReadiness, setDbReadiness] = useState(null)
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [publishStatus, setPublishStatus] = useState(null)
  const [selectedPublicationId, setSelectedPublicationId] = useState("")
  const [publicationDetail, setPublicationDetail] = useState(null)
  const [divergence, setDivergence] = useState(null)
  const [busy, setBusy] = useState(false)
  const [busyLabel, setBusyLabel] = useState("")
  const [lastError, setLastError] = useState("")

  useEffect(() => {
    loadWebsiteData()
  }, [])

  useEffect(() => {
    if (!selectedProjectId && projects.length) setSelectedProjectId(projects[0].id)
  }, [projects, selectedProjectId])

  useEffect(() => {
    if (selectedProjectId) refreshProjectStatus(selectedProjectId)
  }, [selectedProjectId])

  const selectedProject = useMemo(
    () => projects.find((item) => item.id === selectedProjectId) || null,
    [projects, selectedProjectId]
  )

  async function loadWebsiteData() {
    setBusy(true)
    setBusyLabel("A sincronizar cockpit...")
    setLastError("")

    try {
      const [healthRes, summaryRes, catalogRes, deploySummaryRes, dbStatusRes, dbReadinessRes] = await Promise.all([
        getWebsiteControlHealth(),
        getWebsiteControlSummary(),
        getWebsiteControlCatalog({ limit: 12, activeOnly: false }),
        getDeployControlVercelSummary(),
        getDbControlStatus(),
        getDbControlReadiness(),
      ])

      setHealth(healthRes?.website || healthRes || null)
      setSummary(summaryRes?.website?.summary || summaryRes?.website || summaryRes || null)
      setCatalog(catalogRes?.website || catalogRes || null)
      setDeploySummary(deploySummaryRes?.deploy || deploySummaryRes || null)
      setDbStatus(dbStatusRes?.database || dbStatusRes || null)
      setDbReadiness(dbReadinessRes?.database || dbReadinessRes || null)
    } catch (error) {
      setLastError(error?.message || "Falha ao carregar cockpit do Studio.")
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
        getWebsitePublishEnvelope(projectId).catch(() => null),
      ])

      setPublishStatus(statusRes || null)

      const publicationId = statusRes?.website_sync?.publication_id || envelopeRes?.envelope?.publication_id || ""

      if (publicationId) {
        setSelectedPublicationId(publicationId)

        const publicationRes = await getWebsiteControlPublication(publicationId).catch(() => null)
        setPublicationDetail(
          publicationRes?.website?.status ||
          publicationRes?.status ||
          publicationRes?.website?.publication ||
          publicationRes?.publication ||
          null
        )

        const divergenceRes = await getWebsiteControlDivergence(
          publicationId,
          statusRes?.website_sync?.checksum || "",
          statusRes?.publication_package_frozen_at || ""
        ).catch(() => null)

        setDivergence(divergenceRes?.website || divergenceRes || null)
      } else {
        setPublicationDetail(null)
        setDivergence(null)
      }
    } catch (error) {
      setPublishStatus(null)
      setPublicationDetail(null)
      setDivergence(null)
      setLastError(error?.message || "Falha ao carregar estado de publicação.")
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handleLookupPublication() {
    if (!selectedPublicationId.trim()) return alert("Indica um publication_id.")

    setBusy(true)
    setBusyLabel("A consultar publication no Website...")
    setLastError("")

    try {
      const publicationRes = await getWebsiteControlPublication(selectedPublicationId)
      setPublicationDetail(
        publicationRes?.website?.status ||
        publicationRes?.status ||
        publicationRes?.website?.publication ||
        publicationRes?.publication ||
        null
      )

      const divergenceRes = await getWebsiteControlDivergence(
        selectedPublicationId,
        publishStatus?.website_sync?.checksum || "",
        publishStatus?.publication_package_frozen_at || ""
      ).catch(() => null)

      setDivergence(divergenceRes?.website || divergenceRes || null)
    } catch (error) {
      setPublicationDetail(null)
      setDivergence(null)
      setLastError(error?.message || "Falha ao consultar publication.")
      alert(error?.message || "Falha ao consultar publication.")
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handlePublishSelectedProject() {
    if (!selectedProjectId) return alert("Seleciona um projeto primeiro.")
    if (!canPublish(user)) return alert("Sem permissão para publicar no Website.")

    setBusy(true)
    setBusyLabel("A publicar snapshot no Website...")
    setLastError("")

    try {
      const result = await publishProjectToWebsite(selectedProjectId)
      alert(`Projeto publicado no Website. Publication: ${result?.receipt?.publication_id || "-"}`)
      await refreshProjectStatus(selectedProjectId)
      await loadWebsiteData()
      if (typeof onReload === "function") await onReload()
    } catch (error) {
      const message = error?.message || "Falha ao publicar no Website."
      setLastError(message)
      alert(message)
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handleUnpublishSelectedProject() {
    if (!selectedProjectId) return alert("Seleciona um projeto primeiro.")
    if (!canPublish(user)) return alert("Sem permissão para despublicar no Website.")

    setBusy(true)
    setBusyLabel("A despublicar no Website...")
    setLastError("")

    try {
      await unpublishProjectOnWebsite(selectedProjectId)
      alert("Projeto despublicado no Website.")
      await refreshProjectStatus(selectedProjectId)
      await loadWebsiteData()
      if (typeof onReload === "function") await onReload()
    } catch (error) {
      const message = error?.message || "Falha ao despublicar no Website."
      setLastError(message)
      alert(message)
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handleRevalidateSelectedProject() {
    if (!selectedProjectId) return alert("Seleciona um projeto primeiro.")
    if (!canPublish(user)) return alert("Sem permissão para revalidar no Website.")

    setBusy(true)
    setBusyLabel("A revalidar páginas públicas...")
    setLastError("")

    try {
      await revalidateProjectOnWebsite(selectedProjectId)
      alert("Revalidação pedida ao Website.")
      await refreshProjectStatus(selectedProjectId)
      await loadWebsiteData()
    } catch (error) {
      const message = error?.message || "Falha ao revalidar o Website."
      setLastError(message)
      alert(message)
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handleToggleProductActive(item) {
    if (!canPublish(user)) return alert("Sem permissão para alterar visibilidade operacional.")

    setBusy(true)
    setBusyLabel("A atualizar produto...")
    setLastError("")

    try {
      await updateWebsiteProductVisibility(item.product_id, { active: !item.active })
      await loadWebsiteData()
    } catch (error) {
      const message = error?.message || "Falha ao atualizar estado do produto."
      setLastError(message)
      alert(message)
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  async function handleToggleProductFeatured(item) {
    if (!canPublish(user)) return alert("Sem permissão para alterar destaque operacional.")

    setBusy(true)
    setBusyLabel("A atualizar destaque...")
    setLastError("")

    try {
      await updateWebsiteProductVisibility(item.product_id, { featured: !item.featured })
      await loadWebsiteData()
    } catch (error) {
      const message = error?.message || "Falha ao atualizar destaque do produto."
      setLastError(message)
      alert(message)
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }
  async function handleUpdateProductPricing(item) {
    if (!isStructuralOwner(user)) return alert("Pricing estrutural reservado ao owner / super admin.")

    const input = window.prompt(
      `Novo preço para ${item.title} (${item.currency || "EUR"})`,
      (Number(item.price_cents || 0) / 100).toFixed(2)
    )

    if (input === null) return

    const amount = Number(String(input).replace(",", ".").trim())
    if (!Number.isFinite(amount) || amount < 0) return alert("Preço inválido.")

    setBusy(true)
    setBusyLabel("A atualizar preço...")
    setLastError("")

    try {
      await updateWebsiteProductPricing(item.product_id, {
        price_cents: Math.round(amount * 100),
        currency: item.currency || "EUR",
      })
      await loadWebsiteData()
    } catch (error) {
      const message = error?.message || "Falha ao atualizar preço do produto."
      setLastError(message)
      alert(message)
    } finally {
      setBusy(false)
      setBusyLabel("")
    }
  }

  function openWebsite(path = "") {
    const base = String(health?.site_url || "").trim()
    if (!base) return alert("O Website ainda não devolveu NEXT_PUBLIC_SITE_URL.")
    window.open(`${base.replace(/\/$/, "")}${path}`, "_blank", "noopener,noreferrer")
  }

  const counters = summary?.counters || summary || {}
  const recentPublications = summary?.recent_publications || []
  const recentProducts = summary?.recent_products || []
  const catalogItems = catalog?.items || []
  const currentSync = selectedProject?.website_sync || publishStatus?.website_sync || null
  const publicationPolicy = publishStatus?.publication_policy || null
  const siteUrl = String(health?.site_url || "").trim()
  const structuralOwner = isStructuralOwner(user)
  const latestDeployment = deploySummary?.latest_deployment || {}
  const projectInfo = deploySummary?.project || {}
  const dbProbeOk = Boolean(dbStatus?.network_probe?.ok)
  const dbReady = Boolean(dbReadiness?.ready)
  const hasWebsiteControlContext = Boolean(publicationPolicy || publicationDetail || divergence || currentSync)

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <SectionCard
        title="Website Control Center"
        extra={
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <StatusPill
              ok={Boolean(health?.ok) && !lastError}
              label={lastError ? "Com falhas" : (health?.status === "healthy" ? "Website saudável" : "Ligado ao Website")}
            />
            <ActionButton onClick={loadWebsiteData} disabled={busy} tone="secondary">
              {busy ? busyLabel || "A atualizar..." : "Atualizar cockpit"}
            </ActionButton>
          </div>
        }
      >
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12 }}>
          <SmallInfoCard label="Publications" value={counters.publications || 0} />
          <SmallInfoCard label="Variants" value={counters.variants || 0} />
          <SmallInfoCard label="Products" value={counters.products || 0} />
          <SmallInfoCard label="Ativos" value={counters.active_products || counters.activeProducts || 0} />
        </div>

        <div style={{ display: "grid", gap: 8, padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
          <div><strong>Saúde e acesso</strong></div>
          <div>Status: {health?.status || "-"}</div>
          <div>Environment: {health?.environment || "-"}</div>
          <div>Database interna do Website: {health?.services?.database?.ok ? "OK" : "FALHA"}</div>
          <div>Site URL: {siteUrl || "-"}</div>
          <div>Última leitura: {health?.checked_at || summary?.checked_at || "-"}</div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <ActionButton onClick={() => openWebsite("/")} disabled={!siteUrl} tone="secondary">Abrir Website</ActionButton>
            <ActionButton onClick={() => openWebsite("/admin")} disabled={!siteUrl} tone="secondary">Abrir admin Website</ActionButton>
            <ActionButton onClick={() => openWebsite("/loja")} disabled={!siteUrl} tone="secondary">Abrir loja</ActionButton>
          </div>
        </div>

        {lastError ? (
          <div
            style={{
              padding: 12,
              borderRadius: 12,
              border: "1px solid rgba(220,38,38,0.25)",
              background: "rgba(254,226,226,0.7)",
              color: "#991b1b",
              fontWeight: 600,
            }}
          >
            {lastError}
          </div>
        ) : null}
      </SectionCard>

      <SectionCard title="Deploy e infraestrutura pública">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
          <SmallInfoCard label="Projeto Vercel" value={projectInfo.name || "-"} />
          <SmallInfoCard label="Framework" value={projectInfo.framework || "-"} />
          <SmallInfoCard label="Node" value={projectInfo.node_version || "-"} />
          <SmallInfoCard label="Último deploy" value={latestDeployment.ready_state || "-"} />
          <SmallInfoCard label="Database readiness" value={dbReady ? "READY" : "PENDENTE"} />
          <SmallInfoCard label="DB network probe" value={dbProbeOk ? "OK" : "FALHA"} />
        </div>
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

          {publicationPolicy ? (
            <div
              style={{
                padding: 12,
                borderRadius: 12,
                border: "1px solid #e5e7eb",
                background: publicationPolicy.eligible_for_website_publish ? "rgba(220,252,231,0.7)" : "rgba(254,242,242,0.8)",
                display: "grid",
                gap: 6,
              }}
            >
              <div><strong>Política de publicação</strong></div>
              <div>Ready for publish: {publicationPolicy.ready_for_publish ? "Sim" : "Não"}</div>
              <div>Package congelado: {publicationPolicy.has_frozen_package ? "Sim" : "Não"}</div>
              <div>Contrato: {publicationPolicy.contract?.status || "-"} · score {publicationPolicy.contract?.score_percent || 0}%</div>
              <div>Razões: {(publicationPolicy.reasons || []).join(", ") || "nenhuma"}</div>
            </div>
          ) : null}

          {hasWebsiteControlContext ? (
            <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(248,250,252,0.9)", color: "#334155" }}>
              Os cartões abaixo resumem prontidão, significado e confiança. Os blocos seguintes mantêm os factos brutos do Website para validação operacional.
            </div>
          ) : null}

          <WebsiteReadinessCard
           selectedProject={selectedProject}
           publishStatus={publishStatus}
          />
          <WebsitePublishConfidenceCard
            selectedProject={selectedProject}
            publishStatus={publishStatus}
            publicationDetail={publicationDetail}
            divergence={divergence}
            lastError={lastError}
          />

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <ActionButton onClick={() => refreshProjectStatus(selectedProjectId)} disabled={busy || !selectedProjectId} tone="secondary">
              Atualizar estado
            </ActionButton>
            <ActionButton onClick={handlePublishSelectedProject} disabled={busy || !selectedProjectId || !canPublish(user)}>
              Publicar no Website
            </ActionButton>
            <ActionButton onClick={handleUnpublishSelectedProject} disabled={busy || !selectedProjectId || !canPublish(user)} tone="danger">
              Despublicar
            </ActionButton>
            <ActionButton onClick={handleRevalidateSelectedProject} disabled={busy || !selectedProjectId || !canPublish(user)} tone="secondary">
              Revalidar cache
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
              <div>Último unpublish: {currentSync.unpublished_at || "-"}</div>
              <div>Última revalidate: {currentSync.last_revalidate_at || "-"}</div>
            </div>
          ) : null}
        </div>
      </SectionCard>

      <SectionCard title="Divergência Studio vs Website">
        {divergence ? (
          <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: divergence.divergence_ok ? "rgba(220,252,231,0.7)" : "rgba(254,242,242,0.8)", display: "grid", gap: 6 }}>
            <div><strong>{divergence.divergence_ok ? "Sem divergência crítica" : "Divergência detetada"}</strong></div>
            <div>Publication ID: {divergence.publication_id}</div>
            <div>Checksum esperado: {divergence.expected_checksum || "-"}</div>
            <div>Checksum Website: {divergence.actual_checksum || "-"}</div>
            <div>Versão esperada: {divergence.expected_project_version || "-"}</div>
            <div>Versão Website: {divergence.actual_project_version || "-"}</div>
            <div>Razões: {(divergence.reasons || []).join(", ") || "nenhuma"}</div>
          </div>
        ) : (
          <div>Sem análise de divergência carregada ainda.</div>
        )}
      </SectionCard>

      <SectionCard title="Detalhe de publication no Website">
        <div style={{ display: "grid", gap: 10 }}>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <input
              value={selectedPublicationId}
              onChange={(e) => setSelectedPublicationId(e.target.value)}
              placeholder="publication_id"
              style={{ flex: 1, minWidth: 220, padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
            />
            <ActionButton onClick={handleLookupPublication} disabled={busy || !selectedPublicationId.trim()} tone="secondary">
              Consultar publication
            </ActionButton>
          </div>

          {publicationDetail ? (
            <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 8 }}>
              <div><strong>{publicationDetail.ip?.name || publicationDetail.ip?.slug || publicationDetail.project_slug || "Publication"}</strong></div>
              <div>Publication ID: {publicationDetail.publication_id}</div>
              <div>Projeto: {publicationDetail.project_slug || publicationDetail.project_id}</div>
              <div>Canal: {publicationDetail.channel} · Língua: {publicationDetail.language} · Estado: {publicationDetail.status}</div>
              <div>Série: {publicationDetail.series?.name || "-"}</div>
              <div>Studio meta: checksum {publicationDetail.studio_meta?.checksum || "-"} · version {publicationDetail.studio_meta?.project_version || "-"}</div>
              <div>Atualizado em: {publicationDetail.updated_at}</div>

              <div style={{ display: "grid", gap: 8 }}>
                {(publicationDetail.variants || []).map((variant) => (
                  <div key={variant.variant_id} style={{ padding: 10, borderRadius: 10, border: "1px solid #e5e7eb", background: "#fff", display: "grid", gap: 4 }}>
                    <div><strong>{variant.slug || variant.variant_id}</strong></div>
                    <div>Variant: {variant.variant_id}</div>
                    <div>Formato: {variant.format} · Língua: {variant.language}</div>
                    <div>Publicado: {variant.published ? "Sim" : "Não"}</div>
                    <div>Assets count: {variant.assets_count || 0}</div>
                    <div>Studio meta: checksum {variant.studio_meta?.checksum || "-"}</div>
                    <div>
                      Produtos: {(variant.products || []).map((product) => `${product.slug} (${product.active ? "ativo" : "inativo"})`).join(", ") || "-"}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div>Sem detalhe de publication carregado.</div>
          )}
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

              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <ActionButton onClick={() => handleToggleProductActive(item)} disabled={busy || !canPublish(user)} tone="secondary">
                  {item.active ? "Desativar" : "Ativar"}
                </ActionButton>
                <ActionButton onClick={() => handleToggleProductFeatured(item)} disabled={busy || !canPublish(user)} tone="secondary">
                  {item.featured ? "Remover destaque" : "Destacar"}
                </ActionButton>
                <ActionButton onClick={() => handleUpdateProductPricing(item)} disabled={busy || !structuralOwner}>
                  Atualizar preço
                </ActionButton>
              </div>
            </div>
          ))}
        </div>

        {recentPublications.length ? (
          <div style={{ display: "grid", gap: 8 }}>
            <div><strong>Últimas publicações recebidas</strong></div>
            {recentPublications.map((item) => (
              <div key={item.publication_id} style={{ fontSize: 13, color: "#334155" }}>
                {item.publication_id} · {item.project_slug || item.project_id} · {item.status || "-"}
              </div>
            ))}
          </div>
        ) : null}

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

      <SectionCard title="Nota editorial futura — tipografia por IP/Saga/volume">
        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
          <div><strong>Requisito registado</strong></div>
          <div>Adicionar um quadro tipográfico no Studio para escolher fonte por IP inteira, por Saga específica ou por volume/edição especial.</div>
          <div>Exemplo: Baribudos base usa uma fonte principal; um volume premium sazonal como Halloween ou Natal pode sobrepor fonte só nesse volume.</div>
          <div>Herança desejada: Studio default → IP → Saga → volume especial.</div>
        </div>
      </SectionCard>
    </div>
  )
}
