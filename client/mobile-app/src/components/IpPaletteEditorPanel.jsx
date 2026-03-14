import { useEffect, useState } from "react"
import { getIpPalette, listIps, updateIpPalette } from "../api.js"

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

function ColorField({ label, value, onChange }) {
  return (
    <div style={{ display: "grid", gap: 6 }}>
      <label>{label}</label>
      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
        <input
          type="color"
          value={value || "#000000"}
          onChange={(e) => onChange(e.target.value)}
          style={{ width: 52, height: 40, border: "none", background: "transparent" }}
        />
        <input
          value={value || ""}
          onChange={(e) => onChange(e.target.value)}
          placeholder="#000000"
          style={{ flex: 1, padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />
      </div>
    </div>
  )
}

export default function IpPaletteEditorPanel({ user }) {
  const [ips, setIps] = useState([])
  const [selectedSlug, setSelectedSlug] = useState("")
  const [palette, setPalette] = useState({
    primary: "#2F5E2E",
    secondary: "#6FA86A",
    accent: "#D4A73C",
    background: "#F5EED6",
    character_base: "#8B5E3C"
  })

  useEffect(() => {
    loadIps()
  }, [])

  useEffect(() => {
    if (selectedSlug) {
      loadPalette(selectedSlug)
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

  async function loadPalette(slug) {
    try {
      const res = await getIpPalette(slug, user)
      setPalette(res?.palette || {})
    } catch (error) {
      alert(error?.message || "Erro ao carregar paleta.")
    }
  }

  async function handleSave() {
    if (!selectedSlug) return
    try {
      await updateIpPalette(selectedSlug, palette, user)
      alert("Paleta atualizada.")
      await loadPalette(selectedSlug)
    } catch (error) {
      alert(error?.message || "Erro ao guardar paleta.")
    }
  }

  return (
    <Card title="Editor de Paleta por IP">
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

      <ColorField
        label="Cor principal"
        value={palette.primary}
        onChange={(value) => setPalette((current) => ({ ...current, primary: value }))}
      />

      <ColorField
        label="Cor secundária"
        value={palette.secondary}
        onChange={(value) => setPalette((current) => ({ ...current, secondary: value }))}
      />

      <ColorField
        label="Cor de acento"
        value={palette.accent}
        onChange={(value) => setPalette((current) => ({ ...current, accent: value }))}
      />

      <ColorField
        label="Cor de fundo"
        value={palette.background}
        onChange={(value) => setPalette((current) => ({ ...current, background: value }))}
      />

      <ColorField
        label="Cor base de personagem"
        value={palette.character_base}
        onChange={(value) => setPalette((current) => ({ ...current, character_base: value }))}
      />

      <div style={{ display: "grid", gap: 8 }}>
        <strong>Preview rápida</strong>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {Object.entries(palette).map(([key, value]) => (
            <div
              key={key}
              style={{
                width: 90,
                borderRadius: 12,
                overflow: "hidden",
                border: "1px solid #d1d5db",
                background: "#fff"
              }}
            >
              <div style={{ height: 42, background: value }} />
              <div style={{ padding: 8, fontSize: 12 }}>{key}</div>
            </div>
          ))}
        </div>
      </div>

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
        Guardar paleta
      </button>
    </Card>
  )
}
