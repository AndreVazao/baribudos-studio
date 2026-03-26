import { useEffect, useMemo, useState } from "react"
import {
  createCommerceGroup,
  deleteCommerceGroup,
  getBundleReconcileReport,
  getWebsiteBundlesStatus,
  getWebsiteControlCatalog,
  listCommerceGroups,
  publishCommerceGroupToWebsite,
  updateCommerceGroup,
} from "../api.js"

function canCommercial(user) {
  const role = String(user?.role || "").toLowerCase()
  const name = String(user?.name || "").toLowerCase()
  return ["owner", "creator", "admin"].includes(role) || ["andré", "andre", "esposa", "wife", "mama"].includes(name)
}

function isOwner(user) {
  const role = String(user?.role || "").toLowerCase()
  const name = String(user?.name || "").toLowerCase()
  return role === "owner" || ["andré", "andre"].includes(name)
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

function productToGroupItem(product, position = 0) {
  return {
    product_id: product?.product_id || "",
    slug: product?.slug || "",
    title: product?.title || "",
    type: product?.type || "",
    currency: product?.currency || "EUR",
    price_cents: Number(product?.price_cents || 0),
    position,
  }
}

function reconcileBadge(status) {
  if (status === "in_sync") return { label: "Em sync", background: "rgba(220,252,231,0.8)", color: "#166534" }
  if (status === "diverged") return { label: "Divergiu", background: "rgba(254,249,195,0.85)", color: "#854d0e" }
  return { label: "Falta no Website", background: "rgba(254,226,226,0.85)", color: "#991b1b" }
}

export default function CommerceGroupsPanel({ user, catalogItems = [] }) {
  const [groups, setGroups] = useState([])
  const [remoteCatalog, setRemoteCatalog] = useState([])
  const [websiteBundles, setWebsiteBundles] = useState([])
  const [reconcileReport, setReconcileReport] = useState([])
  const [loading, setLoading] = useState(false)
  const [newSlug, setNewSlug] = useState("")
  const [newName, setNewName] = useState("")
  const [newDescription, setNewDescription] = useState("")
  const [newPrice, setNewPrice] = useState("0.00")
  const [selectedProductIds, setSelectedProductIds] = useState([])

  useEffect(() => {
    loadGroups()
    loadCatalog()
    loadWebsiteBundles()
    loadReconcileReport()
  }, [])

  const effectiveCatalog = useMemo(
    () => (catalogItems && catalogItems.length ? catalogItems : remoteCatalog),
    [catalogItems, remoteCatalog]
  )

  const catalogMap = useMemo(() => {
    const map = new Map()
    effectiveCatalog.forEach((item) => map.set(item.product_id, item))
    return map
  }, [effectiveCatalog])

  async function loadCatalog() {
    try {
      const response = await getWebsiteControlCatalog({ limit: 50, activeOnly: false })
      setRemoteCatalog(response?.website?.items || response?.items || [])
    } catch {
      setRemoteCatalog([])
    }
  }

  async function loadWebsiteBundles() {
    try {
      const response = await getWebsiteBundlesStatus(20)
      setWebsiteBundles(response?.website?.bundles || response?.bundles || [])
    } catch {
      setWebsiteBundles([])
    }
  }

  async function loadReconcileReport() {
    try {
      const response = await getBundleReconcileReport(100)
      setReconcileReport(response?.report || [])
    } catch {
      setReconcileReport([])
    }
  }

  async function loadGroups() {
    setLoading(true)
    try {
      const response = await listCommerceGroups()
      setGroups(response?.groups || [])
    } catch (error) {
      alert(error?.message || "Falha ao carregar grupos comerciais.")
    } finally {
      setLoading(false)
    }
  }

  function toggleSelectedProduct(productId) {
    setSelectedProductIds((current) =>
      current.includes(productId)
        ? current.filter((id) => id !== productId)
        : [...current, productId]
    )
  }

  async function refreshAll() {
    await Promise.all([loadGroups(), loadWebsiteBundles(), loadReconcileReport()])
  }

  async function handleCreateGroup() {
    if (!canCommercial(user)) {
      alert("Sem permissão comercial.")
      return
    }
    if (!newSlug.trim() || !newName.trim()) {
      alert("Slug e nome são obrigatórios.")
      return
    }

    const amount = Number(String(newPrice || "0").replace(",", "."))
    if (!Number.isFinite(amount) || amount < 0) {
      alert("Preço inválido.")
      return
    }

    const items = selectedProductIds
      .map((productId, index) => productToGroupItem(catalogMap.get(productId), index))
      .filter((item) => item.product_id)

    setLoading(true)
    try {
      await createCommerceGroup({
        slug: newSlug.trim(),
        name: newName.trim(),
        description: newDescription.trim(),
        group_type: "bundle",
        currency: "EUR",
        price_cents: Math.round(amount * 100),
        active: false,
        featured: false,
        items,
      })
      setNewSlug("")
      setNewName("")
      setNewDescription("")
      setNewPrice("0.00")
      setSelectedProductIds([])
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Falha ao criar grupo comercial.")
    } finally {
      setLoading(false)
    }
  }

  async function handleToggleFlag(group, field) {
    if (!canCommercial(user)) {
      alert("Sem permissão comercial.")
      return
    }
    setLoading(true)
    try {
      await updateCommerceGroup(group.id, { [field]: !Boolean(group?.[field]) })
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Falha ao atualizar grupo.")
    } finally {
      setLoading(false)
    }
  }

  async function handleUpdatePrice(group) {
    if (!isOwner(user)) {
      alert("Preço estrutural reservado ao owner / super admin.")
      return
    }
    const current = (Number(group?.price_cents || 0) / 100).toFixed(2)
    const input = window.prompt(`Novo preço para ${group.name}`, current)
    if (input === null) return
    const amount = Number(String(input).replace(",", "."))
    if (!Number.isFinite(amount) || amount < 0) {
      alert("Preço inválido.")
      return
    }
    setLoading(true)
    try {
      await updateCommerceGroup(group.id, { price_cents: Math.round(amount * 100) })
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Falha ao atualizar preço do grupo.")
    } finally {
      setLoading(false)
    }
  }

  async function handleDeleteGroup(group) {
    if (!isOwner(user)) {
      alert("Remoção estrutural reservada ao owner / super admin.")
      return
    }
    if (!window.confirm(`Apagar o grupo ${group.name}?`)) return
    setLoading(true)
    try {
      await deleteCommerceGroup(group.id)
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Falha ao apagar grupo.")
    } finally {
      setLoading(false)
    }
  }

  async function handlePublishGroup(group) {
    if (!canCommercial(user)) {
      alert("Sem permissão comercial.")
      return
    }
    setLoading(true)
    try {
      await publishCommerceGroupToWebsite(group.id)
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Falha ao publicar bundle no Website.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ border: "1px solid rgba(255,255,255,0.25)", borderRadius: 16, background: "rgba(255,255,255,0.84)", backdropFilter: "blur(8px)", padding: 16, display: "grid", gap: 12, boxShadow: "0 10px 24px rgba(0,0,0,0.10)" }}>
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>Grupos comerciais / Bundles</h3>

      <div style={{ display: "grid", gap: 8, padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
        <div><strong>Autoridade comercial</strong></div>
        <div>O Studio é a source of truth para grupos, bundles e pricing estrutural.</div>
        <div>Website materializa e expõe; não manda na lógica comercial de origem.</div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <ActionButton onClick={refreshAll} disabled={loading} tone="secondary">Atualizar estado</ActionButton>
        </div>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <input value={newSlug} onChange={(e) => setNewSlug(e.target.value)} placeholder="Slug do bundle" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }} />
        <input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Nome do bundle" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }} />
        <input value={newDescription} onChange={(e) => setNewDescription(e.target.value)} placeholder="Descrição" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }} />
        <input value={newPrice} onChange={(e) => setNewPrice(e.target.value)} placeholder="Preço do bundle (EUR)" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }} />
        <div style={{ display: "grid", gap: 8 }}>
          <div><strong>Produtos a incluir</strong></div>
          {effectiveCatalog.length === 0 ? <div>Sem produtos do Website carregados no cockpit.</div> : null}
          {effectiveCatalog.map((item) => (
            <label key={item.product_id} style={{ display: "flex", gap: 8, alignItems: "center", padding: 8, borderRadius: 10, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
              <input type="checkbox" checked={selectedProductIds.includes(item.product_id)} onChange={() => toggleSelectedProduct(item.product_id)} />
              <span>{item.title} · {item.type} · {item.currency} {(Number(item.price_cents || 0) / 100).toFixed(2)}</span>
            </label>
          ))}
        </div>
        <ActionButton onClick={handleCreateGroup} disabled={loading || !canCommercial(user)}>Criar grupo comercial</ActionButton>
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        <div><strong>Grupos guardados no Studio</strong></div>
        {groups.length === 0 ? <div>Sem grupos comerciais ainda.</div> : null}
        {groups.map((group) => (
          <div key={group.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
            <div><strong>{group.name}</strong> ({group.slug})</div>
            <div>Tipo: {group.group_type} · {group.currency} {(Number(group.price_cents || 0) / 100).toFixed(2)}</div>
            <div>Ativo: {group.active ? "Sim" : "Não"} · Featured: {group.featured ? "Sim" : "Não"}</div>
            <div>Itens: {(group.items || []).map((item) => item.title || item.slug || item.product_id).join(", ") || "-"}</div>
            <div>Publish Website: {group.publish_state?.website?.published ? "Publicado" : "Por publicar"}</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <ActionButton onClick={() => handleToggleFlag(group, "active")} disabled={loading || !canCommercial(user)} tone="secondary">{group.active ? "Desativar" : "Ativar"}</ActionButton>
              <ActionButton onClick={() => handleToggleFlag(group, "featured")} disabled={loading || !canCommercial(user)} tone="secondary">{group.featured ? "Remover destaque" : "Destacar"}</ActionButton>
              <ActionButton onClick={() => handleUpdatePrice(group)} disabled={loading || !isOwner(user)}>Atualizar preço</ActionButton>
              <ActionButton onClick={() => handlePublishGroup(group)} disabled={loading || !canCommercial(user)}>Publicar no Website</ActionButton>
              <ActionButton onClick={() => handleDeleteGroup(group)} disabled={loading || !isOwner(user)} tone="danger">Apagar</ActionButton>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        <div><strong>Bundles materializados no Website</strong></div>
        {websiteBundles.length === 0 ? <div>Sem bundles materializados ainda.</div> : null}
        {websiteBundles.map((bundle) => (
          <div key={bundle.group_id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
            <div><strong>{bundle.name}</strong> ({bundle.slug})</div>
            <div>Tipo: {bundle.group_type} · {bundle.currency} {(Number(bundle.price_cents || 0) / 100).toFixed(2)}</div>
            <div>Ativo: {bundle.active ? "Sim" : "Não"} · Featured: {bundle.featured ? "Sim" : "Não"}</div>
            <div>Itens: {(bundle.items || []).map((item) => item.title || item.slug || item.product_id).join(", ") || "-"}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        <div><strong>Reconcile Studio ↔ Website</strong></div>
        {reconcileReport.length === 0 ? <div>Sem relatório de reconcile ainda.</div> : null}
        {reconcileReport.map((item) => {
          const badge = reconcileBadge(item.status)
          return (
            <div key={item.group_id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <strong>{item.local?.name || item.local?.slug || item.group_id}</strong>
                <span style={{ padding: "6px 10px", borderRadius: 999, background: badge.background, color: badge.color, fontWeight: 700, fontSize: 12 }}>{badge.label}</span>
              </div>
              <div>Local: {item.local?.currency} {(Number(item.local?.price_cents || 0) / 100).toFixed(2)} · itens {item.local?.items_count || 0}</div>
              <div>Website: {item.website ? `${item.website.currency} ${(Number(item.website.price_cents || 0) / 100).toFixed(2)} · itens ${item.website.items_count || 0}` : "Ainda não materializado"}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
