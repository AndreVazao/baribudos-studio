import { useEffect, useState } from "react"
import {
  getIpBranding,
  listIps,
  updateIpBranding,
  uploadIpBrandingAsset
} from "../api.js"

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

function AssetRow({ label, value, onChange, onUpload, previewBase }) {
  return (
    <div style={{ display: "grid", gap: 8, padding: 12, border: "1px solid #e5e7eb", borderRadius: 12, background: "rgba(255,255,255,0.55)" }}>
      <strong>{label}</strong>

      {value ? (
        <img
          src={`${previewBase}/${value.replace(/^public\//, "")}`}
          alt={label}
          style={{ maxHeight: 80, width: "auto", objectFit: "contain", justifySelf: "start" }}
        />
      ) : (
        <div>Sem ficheiro</div>
      )}

      <input
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder="public/brand/ips/minha-saga/logo.png"
        style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <input
        type="file"
        accept=".png,.jpg,.jpeg,.webp"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) onUpload(file)
        }}
      />
    </div>
  )
}

export default function IpBrandingEditorPanel({ user }) {
  const [ips, setIps] = useState([])
  const [selectedSlug, setSelectedSlug] = useState("")
  const [brandAssets, setBrandAssets] = useState({
    studio_logo: "",
    series_logo: "",
    seal_logo: ""
  })

  const previewBase = window.location.origin.replace(/\/+$/, "")

  useEffect(() => {
    loadIps()
  }, [])

  useEffect(() => {
    if (selectedSlug) {
      loadBranding(selectedSlug)
    }
  }, [selectedSlug])

  async function loadIps() {
    const res = await listIps(user)
    const list = res?.ips || []
    setIps(list)
    if (!selectedSlug && list.length) {
      setSelectedSlug(list[0].slug)
    }
  }

  async function loadBranding(slug) {
    try {
      const res = await getIpBranding(slug, user)
      setBrandAssets(res?.brand_assets || {})
    } catch (error) {
      alert(error?.message || "Erro ao carregar branding.")
    }
  }

  async function handleSave() {
    if (!selectedSlug) return

    try {
      await updateIpBranding(selectedSlug, brandAssets, user)
      alert("Branding guardado.")
      await loadBranding(selectedSlug)
    } catch (error) {
      alert(error?.message || "Erro ao guardar branding.")
    }
  }

  async function handleUpload(assetType, file) {
    if (!selectedSlug) return

    try {
      const res = await uploadIpBrandingAsset(selectedSlug, assetType, file, user)
      setBrandAssets(res?.brand_assets || {})
      alert("Upload concluído.")
    } catch (error) {
      alert(error?.message || "Erro no upload.")
    }
  }

  return (
    <Card title="Editor de Logos e Selos por IP">
      <label>IP / Saga</label>
      <select
        value={selectedSlug}
        onChange={(e) => setSelectedSlug(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="">Selecionar IP</option>
        {ips.map((item) => (
          <option key={item.id} value={item.slug}>
            {item.name}
          </option>
        ))}
      </select>

      <AssetRow
        label="Logo do Studio"
        value={brandAssets.studio_logo}
        onChange={(value) => setBrandAssets((current) => ({ ...current, studio_logo: value }))}
        onUpload={(file) => handleUpload("studio_logo", file)}
        previewBase={previewBase}
      />

      <AssetRow
        label="Logo da Saga"
        value={brandAssets.series_logo}
        onChange={(value) => setBrandAssets((current) => ({ ...current, series_logo: value }))}
        onUpload={(file) => handleUpload("series_logo", file)}
        previewBase={previewBase}
      />

      <AssetRow
        label="Selo da Saga"
        value={brandAssets.seal_logo}
        onChange={(value) => setBrandAssets((current) => ({ ...current, seal_logo: value }))}
        onUpload={(file) => handleUpload("seal_logo", file)}
        previewBase={previewBase}
      />

      <button
        onClick={handleSave}
        style={{
          padding: "10px 12px",
          borderRadius: 12,
          border: "none",
          background: "#2F5E2E",
          color: "#fff",
          fontWeight: 700,
          cursor: "pointer"
        }}
      >
        Guardar branding
      </button>
    </Card>
  )
  }
