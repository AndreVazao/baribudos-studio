import { useEffect, useMemo, useState } from "react"
import {
  archiveAsset,
  listAssets,
  listIps,
  listProjects,
  publishAsset,
  rollbackAsset,
  uploadAsset
} from "../api.js"

const ASSET_TYPES = [
  "studio_logo",
  "ip_logo",
  "cover",
  "hero_background",
  "gallery_image",
  "thumbnail",
  "ornament",
  "badge",
  "promo_banner",
  "character_card",
  "background_texture",
  "trailer_thumbnail",
  "social_card",
  "campaign_visual"
]

const CONTEXTS = [
  "global_header",
  "global_footer",
  "homepage",
  "ip_page",
  "product_page",
  "checkout",
  "library",
  "admin",
  "campaign",
  "marketing_landing",
  "email",
  "social",
  "marketplace_amazon",
  "marketplace_website"
]

function Card({ title, children }) {
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
        boxShadow: "0 10px 24px rgba(0,0,0,0.10)"
      }}
    >
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>{title}</h3>
      {children}
    </div>
  )
}

function ActionButton({ children, onClick, color = "#2F5E2E" }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "10px 12px",
        borderRadius: 12,
        border: "none",
        background: color,
        color: "#fff",
        fontWeight: 700,
        cursor: "pointer"
      }}
    >
      {children}
    </button>
  )
}

export default function VisualAssetsPanel({ user }) {
  const [ips, setIps] = useState([])
  const [projects, setProjects] = useState([])
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  const [selectedIp, setSelectedIp] = useState("baribudos")
  const [selectedProject, setSelectedProject] = useState("")
  const [assetType, setAssetType] = useState("ip_logo")
  const [context, setContext] = useState("ip_page")
  const [language, setLanguage] = useState("")
  const [priority, setPriority] = useState(0)
  const [isPrimary, setIsPrimary] = useState(true)
  const [status, setStatus] = useState("draft")
  const [file, setFile] = useState(null)

  useEffect(() => {
    loadBoot()
  }, [])

  useEffect(() => {
    loadAssets()
  }, [selectedIp, selectedProject])

  const filteredProjects = useMemo(() => {
    if (!selectedIp) return projects
    return projects.filter((project) => String(project?.saga_slug || "") === String(selectedIp))
  }, [projects, selectedIp])

  async function loadBoot() {
    try {
      const [ipsRes, projectsRes] = await Promise.all([
        listIps(user),
        listProjects(user)
      ])

      const ipsList = ipsRes?.ips || []
      const projectsList = projectsRes?.projects || []

      setIps(ipsList)
      setProjects(projectsList)

      if (!selectedIp && ipsList.length) {
        setSelectedIp(ipsList[0].slug)
      }
    } catch (error) {
      console.error(error)
    }
  }

  async function loadAssets() {
    setLoading(true)
    try {
      const res = await listAssets({
        ip_slug: selectedIp || undefined,
        project_id: selectedProject || undefined
      })
      setItems(res?.items || [])
    } catch (error) {
      console.error(error)
      setItems([])
    }
    setLoading(false)
  }

  async function handleUpload() {
    if (!file) {
      alert("Seleciona um ficheiro.")
      return
    }

    if (!selectedIp) {
      alert("Seleciona uma IP.")
      return
    }

    setUploading(true)
    try {
      await uploadAsset({
        file,
        ip_slug: selectedIp,
        asset_type: assetType,
        context,
        project_id: selectedProject || "",
        language,
        is_primary: isPrimary,
        priority,
        status
      })

      setFile(null)
      await loadAssets()
      alert("Asset carregado com sucesso.")
    } catch (error) {
      console.error(error)
      alert(error?.message || "Erro ao carregar asset.")
    }
    setUploading(false)
  }

  async function handlePublish(assetId) {
    try {
      await publishAsset(assetId)
      await loadAssets()
    } catch (error) {
      console.error(error)
      alert(error?.message || "Erro ao publicar asset.")
    }
  }

  async function handleArchive(assetId) {
    try {
      await archiveAsset(assetId)
      await loadAssets()
    } catch (error) {
      console.error(error)
      alert(error?.message || "Erro ao arquivar asset.")
    }
  }

  async function handleRollback(assetId) {
    try {
      await rollbackAsset(assetId)
      await loadAssets()
    } catch (error) {
      console.error(error)
      alert(error?.message || "Erro ao fazer rollback do asset.")
    }
  }

  return (
    <Card title="Visual Assets">
      <div style={{ display: "grid", gap: 12 }}>
        <label>IP</label>
        <select
          value={selectedIp}
          onChange={(e) => setSelectedIp(e.target.value)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        >
          <option value="">Selecionar IP</option>
          {ips.map((ip) => (
            <option key={ip.id || ip.slug} value={ip.slug}>
              {ip.name}
            </option>
          ))}
        </select>

        <label>Projeto</label>
        <select
          value={selectedProject}
          onChange={(e) => setSelectedProject(e.target.value)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        >
          <option value="">Sem projeto específico</option>
          {filteredProjects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.title}
            </option>
          ))}
        </select>

        <label>Tipo de asset</label>
        <select
          value={assetType}
          onChange={(e) => setAssetType(e.target.value)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        >
          {ASSET_TYPES.map((item) => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>

        <label>Contexto</label>
        <select
          value={context}
          onChange={(e) => setContext(e.target.value)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        >
          {CONTEXTS.map((item) => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>

        <label>Idioma</label>
        <input
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          placeholder="ex: pt-PT"
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />

        <label>Priority</label>
        <input
          type="number"
          value={priority}
          onChange={(e) => setPriority(Number(e.target.value || 0))}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />

        <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input
            type="checkbox"
            checked={isPrimary}
            onChange={(e) => setIsPrimary(e.target.checked)}
          />
          Marcar como primary
        </label>

        <label>Status inicial</label>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        >
          <option value="draft">draft</option>
          <option value="approved">approved</option>
          <option value="published">published</option>
          <option value="archived">archived</option>
        </select>

        <label>Ficheiro</label>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />

        <ActionButton onClick={handleUpload}>
          {uploading ? "A carregar..." : "Upload asset"}
        </ActionButton>
      </div>

      <div>
        <strong>Assets registados</strong>
      </div>

      {loading ? <div>A carregar assets...</div> : null}

      <div style={{ display: "grid", gap: 12 }}>
        {items.map((asset) => (
          <div
            key={asset.asset_id}
            style={{
              border: "1px solid #e5e7eb",
              borderRadius: 12,
              padding: 12,
              display: "grid",
              gap: 8,
              background: "rgba(255,255,255,0.55)"
            }}
          >
            <div><strong>{asset.asset_type}</strong></div>
            <div>Contexto: {asset.context || "-"}</div>
            <div>IP: {asset.ip_slug || "-"}</div>
            <div>Projeto: {asset.project_id || "-"}</div>
            <div>Idioma: {asset.language || "-"}</div>
            <div>Versão: {asset.version}</div>
            <div>Primary: {asset.is_primary ? "Sim" : "Não"}</div>
            <div>Status: {asset.status}</div>
            <div>Storage: {asset.storage_path || "-"}</div>
            <div>URL: {asset.url || "-"}</div>

            {asset.url ? (
              <img
                src={asset.url}
                alt={asset.asset_type}
                style={{
                  width: "100%",
                  maxWidth: 320,
                  borderRadius: 12,
                  border: "1px solid #e5e7eb"
                }}
              />
            ) : null}

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <ActionButton onClick={() => handlePublish(asset.asset_id)}>Publicar</ActionButton>
              <ActionButton onClick={() => handleRollback(asset.asset_id)} color="#7c3aed">Rollback</ActionButton>
              <ActionButton onClick={() => handleArchive(asset.asset_id)} color="#991b1b">Arquivar</ActionButton>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
  }
