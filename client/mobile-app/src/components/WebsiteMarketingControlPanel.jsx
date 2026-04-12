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

const STATES = [
  "private",
  "internal_review",
  "teaser_ready",
  "prelaunch_public",
  "launch_ready",
  "published",
  "archived",
]

const EMPTY = {
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

function getDistributionDestinations(project, marketing, websiteSync) {
  const publicState = marketing?.public_state || "private"
  const ready = !!project?.ready_for_publish
  const hasWebsiteActivity = !!(
    websiteSync?.published_at ||
    websiteSync?.last_revalidate_at ||
    websiteSync?.publication_id
  )

  const websiteStatus = publicState === "published"
    ? "published"
    : publicState === "prelaunch_public" || publicState === "teaser_ready"
      ? "ready"
      : ready
        ? "queued"
        : "draft"

  return [
    {
      id: "website",
      label: "Website próprio",
      description: "Destino ativo agora. Recebe teaser, pré-lançamento, lançamento e revalidate.",
      status: websiteStatus,
      detail: hasWebsiteActivity
        ? `Sync conhecido: ${websiteSync?.published_at || websiteSync?.last_revalidate_at || websiteSync?.publication_id}`
        : "Sem publicação conhecida ainda.",
    },
    {
      id: "amazon",
      label: "Amazon KDP / futuras integrações",
      description: "Destino futuro para ebooks e publicações comerciais controladas pelo Studio.",
      status: ready ? "planned" : "draft",
      detail: ready
        ? "Projeto tecnicamente perto de ficar pronto para preparação de distribuição."
        : "Falta fechar mais dados editoriais antes de distribuição externa.",
    },
    {
      id: "youtube",
      label: "YouTube / YouTube Kids",
      description: "Destino futuro para séries, trailers, shorts e distribuição audiovisual controlada pelo Studio.",
      status: marketing?.teaser_trailer_url ? "ready" : "planned",
      detail: marketing?.teaser_trailer_url
        ? "Já existe trailer ou asset de vídeo que pode alimentar um fluxo futuro."
        : "Ainda sem asset de vídeo principal associado ao fluxo público.",
    },
    {
      id: "audio",
      label: "Audiobook / outras plataformas",
      description: "Destino futuro para expansão de distribuição fora do Website próprio.",
      status: marketing?.teaser_excerpt ? "planned" : "draft",
      detail: marketing?.teaser_excerpt
        ? "Já existe copy pública que ajuda a preparar metadados de distribuição."
        : "Ainda sem base pública suficiente para distribuição editorial externa.",
    },
  ]
}

function getStatusMeta(status) {
  if (status === "published") {
    return { label: "published", bg: "rgba(34,197,94,0.15)", color: "#166534" }
  }
  if (status === "ready") {
    return { label: "ready", bg: "rgba(59,130,246,0.15)", color: "#1d4ed8" }
  }
  if (status === "queued") {
    return { label: "queued", bg: "rgba(245,158,11,0.18)", color: "#92400e" }
  }
  if (status === "planned") {
    return { label: "planned", bg: "rgba(148,163,184,0.18)", color: "#475569" }
  }
  return { label: "draft", bg: "rgba(100,116,139,0.12)", color: "#475569" }
}

function getSalesReadiness(project, marketing, websiteSync) {
  const checks = [
    {
      key: "headline",
      label: "Headline forte",
      ok: !!String(marketing?.teaser_headline || "").trim(),
    },
    {
      key: "subtitle",
      label: "Subtítulo claro",
      ok: !!String(marketing?.teaser_subtitle || "").trim(),
    },
    {
      key: "cta",
      label: "CTA definido",
      ok: !!String(marketing?.teaser_cta_label || "").trim(),
    },
    {
      key: "cover",
      label: "Cover principal",
      ok: !!String(marketing?.teaser_cover_url || project?.cover_image || "").trim(),
    },
    {
      key: "gallery",
      label: "Galeria mínima",
      ok: Array.isArray(marketing?.teaser_gallery) && marketing.teaser_gallery.length > 0,
    },
    {
      key: "state",
      label: "Estado público coerente",
      ok: ["teaser_ready", "prelaunch_public", "launch_ready", "published"].includes(marketing?.public_state),
    },
    {
      key: "project-ready",
      label: "Projeto pronto para publicação",
      ok: !!project?.ready_for_publish,
    },
    {
      key: "website-sync",
      label: "Sync Website conhecido",
      ok: !!(websiteSync?.publication_id || websiteSync?.published_at || websiteSync?.last_revalidate_at),
    },
  ]

  const completed = checks.filter((item) => item.ok).length
  const total = checks.length
  const ratio = total ? completed / total : 0

  let level = "draft"
  let label = "Ainda não deve avançar"
  let color = "#991b1b"
  let bg = "rgba(239,68,68,0.10)"

  if (ratio >= 1) {
    level = "sell-now"
    label = "Pronto para vender"
    color = "#166534"
    bg = "rgba(34,197,94,0.12)"
  } else if (ratio >= 0.75) {
    level = "almost-ready"
    label = "Quase pronto para vender"
    color = "#1d4ed8"
    bg = "rgba(59,130,246,0.12)"
  } else if (ratio >= 0.5) {
    level = "needs-work"
    label = "Precisa de fechar mais base comercial"
    color = "#92400e"
    bg = "rgba(245,158,11,0.14)"
  }

  return {
    checks,
    completed,
    total,
    ratio,
    level,
    label,
    color,
    bg,
  }
}

function Button({ children, onClick, disabled = false, tone = "primary" }) {
  const style =
    tone === "secondary"
      ? { background: "#fff", color: "#111827", border: "1px solid #cbd5e1" }
      : tone === "danger"
        ? { background: "#991b1b", color: "#fff", border: "none" }
        : { background: "#2F5E2E", color: "#fff", border: "none" }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        padding: "10px 12px",
        borderRadius: 12,
        ...style,
        fontWeight: 700,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.6 : 1,
      }}
    >
      {children}
    </button>
  )
}

function Card({ title, children, extra = null }) {
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
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <h3 style={{ margin: 0, color: "#2F5E2E" }}>{title}</h3>
        {extra}
      </div>
      {children}
    </div>
  )
}

const parseLines = (value) =>
  String(value || "")
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean)

const toText = (value) => (Array.isArray(value) ? value.join("\n") : "")

const isImage = (value) =>
  /\.(png|jpg|jpeg|webp|gif|bmp|svg)$/i.test(String(value || ""))

const isVideo = (value) =>
  /\.(mp4|webm|mov|m4v)$/i.test(String(value || ""))

function collect(project) {
  const found = new Set()

  const walk = (node) => {
    if (!node) return

    if (typeof node === "string") {
      if (isImage(node) || isVideo(node)) found.add(node)
      return
    }

    if (Array.isArray(node)) {
      node.forEach(walk)
      return
    }

    if (typeof node === "object") {
      Object.values(node).forEach(walk)
    }
  }

  walk(project?.cover_image)
  walk(project?.illustration_path)
  walk(project?.outputs)

  return Array.from(found)
}

export default function WebsiteMarketingControlPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [commercial, setCommercial] = useState({})
  const [marketing, setMarketing] = useState(EMPTY)
  const [publishStatus, setPublishStatus] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      refreshProject(selectedProjectId)
    }
  }, [selectedProjectId])

  const selectedProject = useMemo(
    () => projects.find((item) => item.id === selectedProjectId) || null,
    [projects, selectedProjectId]
  )

  const assets = useMemo(() => collect(selectedProject), [selectedProject])
  const imageAssets = useMemo(() => assets.filter(isImage), [assets])
  const videoAssets = useMemo(() => assets.filter(isVideo), [assets])
  const websiteSync = publishStatus?.website_sync || selectedProject?.website_sync || null
  const distributionDestinations = useMemo(
    () => getDistributionDestinations(selectedProject, marketing, websiteSync),
    [selectedProject, marketing, websiteSync]
  )
  const salesReadiness = useMemo(
    () => getSalesReadiness(selectedProject, marketing, websiteSync),
    [selectedProject, marketing, websiteSync]
  )

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) {
      setSelectedProjectId(list[0].id)
    }
  }

  async function refreshProject(projectId) {
    setBusy(true)
    try {
      const [commercialRes, statusRes] = await Promise.all([
        getProjectCommercial(projectId).catch(() => ({ commercial: {} })),
        getWebsitePublishStatus(projectId).catch(() => null),
      ])

      const nextCommercial = commercialRes?.commercial || {}
      setCommercial(nextCommercial)
      setMarketing({
        ...EMPTY,
        ...(nextCommercial?.website_marketing || nextCommercial?.marketing || {}),
      })
      setPublishStatus(statusRes || null)
    } finally {
      setBusy(false)
    }
  }

  const setPatch = (patch) => {
    setMarketing((current) => ({ ...current, ...patch }))
  }

  const useCover = (value) => setPatch({ teaser_cover_url: value })
  const useTrailer = (value) => setPatch({ teaser_trailer_url: value })
  const addGallery = (value) =>
    setPatch({
      teaser_gallery: Array.from(new Set([...(marketing.teaser_gallery || []), value])),
    })

  const useFirstThreeGallery = () => setPatch({ teaser_gallery: imageAssets.slice(0, 3) })
  const useFirstSixGallery = () => setPatch({ teaser_gallery: imageAssets.slice(0, 6) })

  function autofill() {
    setPatch({
      teaser_cover_url:
        marketing.teaser_cover_url ||
        imageAssets[0] ||
        selectedProject?.cover_image ||
        selectedProject?.illustration_path ||
        "",
      teaser_gallery:
        marketing.teaser_gallery?.length ? marketing.teaser_gallery : imageAssets.slice(0, 6),
      teaser_trailer_url: marketing.teaser_trailer_url || videoAssets[0] || "",
      teaser_headline: marketing.teaser_headline || selectedProject?.title || "",
      teaser_subtitle:
        marketing.teaser_subtitle ||
        selectedProject?.summary ||
        selectedProject?.description ||
        `Uma nova criação do universo ${selectedProject?.saga_name || "Baribudos"} está a ganhar forma.`,
      teaser_excerpt:
        marketing.teaser_excerpt || selectedProject?.story || selectedProject?.summary || "",
    })
  }

  function buildPreset(mode) {
    const baseTitle = selectedProject?.title || "Nova criação"
    const sagaName = selectedProject?.saga_name || "Baribudos"
    const cover =
      marketing.teaser_cover_url ||
      imageAssets[0] ||
      selectedProject?.cover_image ||
      selectedProject?.illustration_path ||
      ""
    const gallery =
      marketing.teaser_gallery?.length
        ? marketing.teaser_gallery
        : imageAssets.slice(0, mode === "quick" ? 3 : 6)
    const trailer = marketing.teaser_trailer_url || videoAssets[0] || ""

    if (mode === "quick") {
      return {
        ...marketing,
        public_state: "teaser_ready",
        prelaunch_enabled: false,
        teaser_badge: "Em breve",
        teaser_headline: marketing.teaser_headline || baseTitle,
        teaser_subtitle:
          marketing.teaser_subtitle ||
          `Primeiro olhar sobre uma nova peça do universo ${sagaName}.`,
        teaser_cta_label: "Ver teaser",
        teaser_release_label: marketing.teaser_release_label || "Primeiras imagens",
        teaser_cover_url: cover,
        teaser_gallery: gallery,
      }
    }

    if (mode === "prelaunch") {
      return {
        ...marketing,
        public_state: "prelaunch_public",
        prelaunch_enabled: true,
        teaser_badge: "Pré-lançamento",
        teaser_headline: marketing.teaser_headline || baseTitle,
        teaser_subtitle:
          marketing.teaser_subtitle ||
          `Página pública pronta para aquecer o lançamento de ${baseTitle}.`,
        teaser_cta_label: "Acompanhar lançamento",
        teaser_release_label: marketing.teaser_release_label || "Lançamento em breve",
        teaser_cover_url: cover,
        teaser_gallery: gallery,
        teaser_trailer_url: trailer,
      }
    }

    return {
      ...marketing,
      public_state: "published",
      prelaunch_enabled: false,
      teaser_badge: "Já disponível",
      teaser_headline: marketing.teaser_headline || baseTitle,
      teaser_subtitle:
        marketing.teaser_subtitle ||
        `${baseTitle} já está pronto para descoberta e compra no Website.`,
      teaser_cta_label: "Comprar agora",
      teaser_release_label: marketing.teaser_release_label || "Disponível agora",
      teaser_cover_url: cover,
      teaser_gallery: gallery,
      teaser_trailer_url: trailer,
    }
  }

  function applyPreset(mode) {
    setMarketing(buildPreset(mode))
  }

  async function save(nextMarketing, successMessage) {
    if (!selectedProjectId) return

    setBusy(true)
    try {
      await updateProjectCommercial(
        selectedProjectId,
        {
          ...commercial,
          website_marketing: {
            ...nextMarketing,
            teaser_gallery: Array.isArray(nextMarketing.teaser_gallery)
              ? nextMarketing.teaser_gallery
              : parseLines(nextMarketing.teaser_gallery),
          },
        },
        user
      )

      await refreshProject(selectedProjectId)

      if (successMessage) {
        alert(successMessage)
      }
    } catch (error) {
      alert(error?.message || "Erro ao guardar controlo de marketing.")
    } finally {
      setBusy(false)
    }
  }

  async function publishTeaser() {
    if (!selectedProjectId) return

    setBusy(true)
    try {
      await updateProjectCommercial(
        selectedProjectId,
        {
          ...commercial,
          website_marketing: {
            ...marketing,
            public_state: "prelaunch_public",
            prelaunch_enabled: true,
          },
        },
        user
      )

      await publishProjectToWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Pré-lançamento empurrado para o Website.")
    } catch (error) {
      alert(error?.message || "Erro ao publicar pré-lançamento no Website.")
    } finally {
      setBusy(false)
    }
  }

  async function presetAndPublishTeaser() {
    if (!selectedProjectId) return

    setBusy(true)
    try {
      const nextMarketing = buildPreset("prelaunch")

      await updateProjectCommercial(
        selectedProjectId,
        {
          ...commercial,
          website_marketing: {
            ...nextMarketing,
            teaser_gallery: Array.isArray(nextMarketing.teaser_gallery)
              ? nextMarketing.teaser_gallery
              : parseLines(nextMarketing.teaser_gallery),
          },
        },
        user
      )

      await publishProjectToWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Preset de pré-lançamento aplicado e publicado no Website.")
    } catch (error) {
      alert(error?.message || "Erro ao aplicar e publicar teaser.")
    } finally {
      setBusy(false)
    }
  }

  async function promoteLaunch() {
    if (!selectedProjectId) return

    setBusy(true)
    try {
      await updateProjectCommercial(
        selectedProjectId,
        {
          ...commercial,
          website_marketing: {
            ...marketing,
            public_state: "published",
            prelaunch_enabled: false,
          },
        },
        user
      )

      await publishProjectToWebsite(selectedProjectId)
      await revalidateProjectOnWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Projeto promovido para lançamento final no Website.")
    } catch (error) {
      alert(error?.message || "Erro ao promover lançamento no Website.")
    } finally {
      setBusy(false)
    }
  }

  async function withdraw() {
    if (!selectedProjectId) return

    setBusy(true)
    try {
      await updateProjectCommercial(
        selectedProjectId,
        {
          ...commercial,
          website_marketing: {
            ...marketing,
            public_state: "private",
            prelaunch_enabled: false,
          },
        },
        user
      )

      await unpublishProjectToWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Superfície pública retirada do Website.")
    } catch (error) {
      alert(error?.message || "Erro ao retirar superfície pública.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card
      title="Website Marketing Control"
      extra={
        <Button
          onClick={() => refreshProject(selectedProjectId)}
          disabled={busy || !selectedProjectId}
          tone="secondary"
        >
          {busy ? "A atualizar..." : "Atualizar"}
        </Button>
      }
    >
      <div
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #e5e7eb",
          background: "rgba(248,250,252,0.9)",
          color: "#334155",
        }}
      >
        O Studio decide o que fica privado, teaser, pré-lançamento ou lançamento final.
        O Website só expõe a superfície pública escolhida aqui.
      </div>

      <label>Projeto</label>
      <select
        value={selectedProjectId}
        onChange={(e) => setSelectedProjectId(e.target.value)}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
        }}
      >
        <option value="">Selecionar projeto</option>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>
            {project.title} — {project.saga_name}
          </option>
        ))}
      </select>

      {selectedProject ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            border: "1px solid #e5e7eb",
            background: "rgba(255,255,255,0.55)",
            display: "grid",
            gap: 6,
          }}
        >
          <div>
            <strong>{selectedProject.title}</strong>
          </div>
          <div>
            IP: {selectedProject.saga_name} ({selectedProject.saga_slug})
          </div>
          <div>Ready for publish: {selectedProject.ready_for_publish ? "Sim" : "Não"}</div>
          <div>Estado público atual: {marketing.public_state}</div>
          <div>Assets detetados: {assets.length}</div>
        </div>
      ) : null}

      <div
        style={{
          padding: 12,
          borderRadius: 12,
          border: `1px solid ${salesReadiness.color}`,
          background: salesReadiness.bg,
          display: "grid",
          gap: 10,
        }}
      >
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
          <strong>Sales readiness</strong>
          <span
            style={{
              display: "inline-flex",
              width: "fit-content",
              padding: "4px 8px",
              borderRadius: 999,
              background: "#fff",
              color: salesReadiness.color,
              fontWeight: 700,
              fontSize: 12,
            }}
          >
            {salesReadiness.label}
          </span>
          <span style={{ color: salesReadiness.color, fontWeight: 700 }}>
            {salesReadiness.completed}/{salesReadiness.total}
          </span>
        </div>

        <div
          style={{
            height: 10,
            borderRadius: 999,
            overflow: "hidden",
            background: "rgba(255,255,255,0.65)",
          }}
        >
          <div
            style={{
              width: `${Math.round(salesReadiness.ratio * 100)}%`,
              height: "100%",
              background: salesReadiness.color,
            }}
          />
        </div>

        <div style={{ display: "grid", gap: 8 }}>
          {salesReadiness.checks.map((item) => (
            <div
              key={item.key}
              style={{
                padding: 10,
                borderRadius: 10,
                border: "1px solid rgba(148,163,184,0.3)",
                background: "rgba(255,255,255,0.78)",
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                alignItems: "center",
              }}
            >
              <span>{item.label}</span>
              <span
                style={{
                  color: item.ok ? "#166534" : "#991b1b",
                  fontWeight: 700,
                }}
              >
                {item.ok ? "OK" : "Falta"}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #e5e7eb",
          background: "rgba(255,255,255,0.55)",
          display: "grid",
          gap: 8,
        }}
      >
        <div><strong>Distribution Hub snapshot</strong></div>
        <div style={{ color: "#475569" }}>
          O Studio é o centro de comando. O Website é só um destino. Amazon, YouTube e outros canais entram aqui como próximos destinos operacionais.
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          {distributionDestinations.map((destination) => {
            const meta = getStatusMeta(destination.status)
            return (
              <div
                key={destination.id}
                style={{
                  padding: 12,
                  borderRadius: 12,
                  border: "1px solid #d1d5db",
                  background: "#fff",
                  display: "grid",
                  gap: 6,
                }}
              >
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                  <strong>{destination.label}</strong>
                  <span
                    style={{
                      display: "inline-flex",
                      width: "fit-content",
                      padding: "4px 8px",
                      borderRadius: 999,
                      background: meta.bg,
                      color: meta.color,
                      fontWeight: 700,
                      fontSize: 12,
                    }}
                  >
                    {meta.label}
                  </span>
                </div>
                <div style={{ color: "#475569" }}>{destination.description}</div>
                <div style={{ color: "#64748b", fontSize: 13 }}>{destination.detail}</div>
              </div>
            )
          })}
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <Button onClick={autofill} disabled={busy || !selectedProjectId}>
          Preencher da produção
        </Button>
        <Button
          onClick={() => applyPreset("quick")}
          disabled={busy || !selectedProjectId}
          tone="secondary"
        >
          Preset teaser rápido
        </Button>
        <Button
          onClick={() => applyPreset("prelaunch")}
          disabled={busy || !selectedProjectId}
          tone="secondary"
        >
          Preset pré-lançamento
        </Button>
        <Button
          onClick={() => applyPreset("launch")}
          disabled={busy || !selectedProjectId}
          tone="secondary"
        >
          Preset lançamento
        </Button>
        <Button onClick={presetAndPublishTeaser} disabled={busy || !selectedProjectId}>
          Preset + publicar teaser
        </Button>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <Button
          onClick={() => save(marketing, "Controlo de marketing do Website guardado.")}
          disabled={busy || !selectedProjectId}
        >
          Guardar controlo marketing
        </Button>
        <Button onClick={publishTeaser} disabled={busy || !selectedProjectId}>
          Publicar pré-lançamento
        </Button>
        <Button onClick={promoteLaunch} disabled={busy || !selectedProjectId}>
          Promover para lançamento
        </Button>
        <Button onClick={withdraw} disabled={busy || !selectedProjectId} tone="danger">
          Retirar do Website
        </Button>
      </div>

      <label>Estado público</label>
      <select
        value={marketing.public_state}
        onChange={(e) => setPatch({ public_state: e.target.value })}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
        }}
      >
        {STATES.map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>

      <label>
        <input
          type="checkbox"
          checked={!!marketing.prelaunch_enabled}
          onChange={(e) => setPatch({ prelaunch_enabled: e.target.checked })}
        />{" "}
        Pré-lançamento público ativo
      </label>

      <label>
        <input
          type="checkbox"
          checked={marketing.share_preview_images_during_production !== false}
          onChange={(e) =>
            setPatch({ share_preview_images_during_production: e.target.checked })
          }
        />{" "}
        Permitir partilhar imagens teaser durante produção
      </label>

      {imageAssets.length ? (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <Button
            onClick={() => useCover(imageAssets[0])}
            disabled={busy || !selectedProjectId}
            tone="secondary"
          >
            Usar 1ª imagem como cover
          </Button>
          <Button
            onClick={useFirstThreeGallery}
            disabled={busy || !selectedProjectId}
            tone="secondary"
          >
            Usar 3 primeiras na galeria
          </Button>
          <Button
            onClick={useFirstSixGallery}
            disabled={busy || !selectedProjectId}
            tone="secondary"
          >
            Usar 6 primeiras na galeria
          </Button>
        </div>
      ) : null}

      {assets.length ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            border: "1px solid #dbe4d8",
            background: "rgba(240,253,244,0.85)",
            display: "grid",
            gap: 8,
          }}
        >
          <strong>Assets sugeridos do projeto</strong>

          <div style={{ display: "grid", gap: 8 }}>
            {assets.slice(0, 10).map((item) => {
              const isSelected =
                item === marketing.teaser_cover_url ||
                item === marketing.teaser_trailer_url ||
                (marketing.teaser_gallery || []).includes(item)

              return (
                <div
                  key={item}
                  style={{
                    padding: 10,
                    borderRadius: 10,
                    border: isSelected ? "2px solid #2F5E2E" : "1px solid #d1d5db",
                    background: "#fff",
                    display: "grid",
                    gap: 8,
                  }}
                >
                  <div
                    style={{
                      display: "grid",
                      gap: 8,
                      gridTemplateColumns: isImage(item) ? "92px 1fr" : "1fr",
                    }}
                  >
                    <div>
                      {isImage(item) ? (
                        <img
                          src={item}
                          alt="asset preview"
                          style={{
                            width: 92,
                            height: 92,
                            objectFit: "cover",
                            borderRadius: 10,
                            border: "1px solid #e5e7eb",
                          }}
                        />
                      ) : isVideo(item) ? (
                        <div
                          style={{
                            width: 92,
                            height: 92,
                            display: "grid",
                            placeItems: "center",
                            borderRadius: 10,
                            border: "1px solid #e5e7eb",
                            background: "#111827",
                            color: "#fff",
                            fontWeight: 700,
                          }}
                        >
                          Vídeo
                        </div>
                      ) : null}
                    </div>

                    <div style={{ wordBreak: "break-all" }}>{item}</div>
                  </div>

                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {isImage(item) ? (
                      <Button onClick={() => useCover(item)} tone="secondary">
                        Usar como cover
                      </Button>
                    ) : null}
                    {isImage(item) ? (
                      <Button onClick={() => addGallery(item)} tone="secondary">
                        Adicionar galeria
                      </Button>
                    ) : null}
                    {isVideo(item) ? (
                      <Button onClick={() => useTrailer(item)} tone="secondary">
                        Usar como trailer
                      </Button>
                    ) : null}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ) : null}

      <label>Badge teaser</label>
      <input
        value={marketing.teaser_badge || ""}
        onChange={(e) => setPatch({ teaser_badge: e.target.value })}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
        }}
      />

      <label>Headline teaser</label>
      <input
        value={marketing.teaser_headline || ""}
        onChange={(e) => setPatch({ teaser_headline: e.target.value })}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
        }}
      />

      <label>Subheadline teaser</label>
      <textarea
        value={marketing.teaser_subtitle || ""}
        onChange={(e) => setPatch({ teaser_subtitle: e.target.value })}
        rows={3}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
          resize: "vertical",
        }}
      />

      <label>CTA teaser</label>
      <input
        value={marketing.teaser_cta_label || ""}
        onChange={(e) => setPatch({ teaser_cta_label: e.target.value })}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
        }}
      />

      <label>Texto de lançamento</label>
      <input
        value={marketing.teaser_release_label || ""}
        onChange={(e) => setPatch({ teaser_release_label: e.target.value })}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
        }}
      />

      <label>Imagem teaser principal</label>
      <input
        value={marketing.teaser_cover_url || ""}
        onChange={(e) => setPatch({ teaser_cover_url: e.target.value })}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
        }}
      />

      <label>Trailer teaser</label>
      <input
        value={marketing.teaser_trailer_url || ""}
        onChange={(e) => setPatch({ teaser_trailer_url: e.target.value })}
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
        }}
      />

      <label>Galeria teaser</label>
      <textarea
        value={toText(marketing.teaser_gallery)}
        onChange={(e) => setPatch({ teaser_gallery: parseLines(e.target.value) })}
        rows={4}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
          resize: "vertical",
        }}
      />

      <label>Excerto público</label>
      <textarea
        value={marketing.teaser_excerpt || ""}
        onChange={(e) => setPatch({ teaser_excerpt: e.target.value })}
        rows={4}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
          resize: "vertical",
        }}
      />

      <label>Notas de visibilidade</label>
      <textarea
        value={marketing.teaser_visibility_notes || ""}
        onChange={(e) => setPatch({ teaser_visibility_notes: e.target.value })}
        rows={3}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
          resize: "vertical",
        }}
      />

      <div
        style={{
          padding: 12,
          borderRadius: 12,
          border: "1px solid #e5e7eb",
          background: "rgba(255,255,255,0.55)",
          display: "grid",
          gap: 8,
        }}
      >
        <div>
          <strong>Preview rápido do teaser</strong>
        </div>

        <div
          style={{
            display: "grid",
            gap: 8,
            padding: 12,
            borderRadius: 12,
            background: "#fff",
            border: "1px solid #e5e7eb",
          }}
        >
          <div
            style={{
              display: "inline-flex",
              width: "fit-content",
              padding: "6px 10px",
              borderRadius: 999,
              background: "rgba(212,167,60,0.18)",
              color: "#7c5a00",
              fontWeight: 700,
            }}
          >
            {marketing.teaser_badge || "Em breve"}
          </div>

          <div style={{ fontSize: 22, fontWeight: 800, color: "#1f2937" }}>
            {marketing.teaser_headline || selectedProject?.title || "Headline teaser"}
          </div>

          <div style={{ color: "#475569" }}>
            {marketing.teaser_subtitle || "Subheadline teaser"}
          </div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", color: "#64748b" }}>
            <span>CTA: {marketing.teaser_cta_label || "-"}</span>
            <span>•</span>
            <span>{marketing.teaser_release_label || "-"}</span>
          </div>

          {marketing.teaser_cover_url ? (
            <div style={{ wordBreak: "break-all", color: "#64748b" }}>
              Cover: {marketing.teaser_cover_url}
            </div>
          ) : null}

          {(marketing.teaser_gallery || []).length ? (
            <div style={{ color: "#64748b" }}>
              Galeria: {(marketing.teaser_gallery || []).length} imagem(ns)
            </div>
          ) : null}
        </div>
      </div>

      {websiteSync ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            border: "1px solid #e5e7eb",
            background: "rgba(255,255,255,0.55)",
            display: "grid",
            gap: 6,
          }}
        >
          <div>
            <strong>Último sync Website</strong>
          </div>
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
