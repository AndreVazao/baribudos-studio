import { useEffect, useState } from "react"
import { getProjectCommercial, listProjects, updateProjectCommercial } from "../api.js"

const CURRENCIES = ["EUR", "USD", "GBP", "BRL"]
const CHANNELS = ["amazon_kdp", "google_play_books", "apple_books", "shopify", "gumroad", "youtube_kids"]
const MARKETPLACES = ["PT", "BR", "ES", "FR", "DE", "IT", "NL", "US", "UK", "JP"]

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

const EMPTY_COMMERCIAL = {
  internal_code: "",
  isbn: "",
  asin: "",
  price: "",
  currency: "EUR",
  collection_seal: "",
  marketplaces: [],
  commercial_status: "draft",
  channels: [],
  keywords: [],
  subtitle: "",
  blurb: ""
}

export default function ProjectCommercialEditorPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [commercial, setCommercial] = useState(EMPTY_COMMERCIAL)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadCommercial(selectedProjectId)
    }
  }, [selectedProjectId])

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) {
      setSelectedProjectId(list[0].id)
    }
  }

  async function loadCommercial(projectId) {
    try {
      const res = await getProjectCommercial(projectId)
      setCommercial({ ...EMPTY_COMMERCIAL, ...(res?.commercial || {}) })
    } catch (error) {
      alert(error?.message || "Erro ao carregar comercial.")
    }
  }

  function toggleListValue(field, value) {
    setCommercial((current) => {
      const list = Array.isArray(current[field]) ? current[field] : []
      return {
        ...current,
        [field]: list.includes(value)
          ? list.filter((item) => item !== value)
          : [...list, value]
      }
    })
  }

  async function handleSave() {
    if (!selectedProjectId) return

    try {
      const payload = {
        ...commercial,
        keywords: String(commercial.keywords || [])
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean)
      }

      await updateProjectCommercial(selectedProjectId, payload, user)
      alert("Metadados comerciais guardados.")
      await loadCommercial(selectedProjectId)
    } catch (error) {
      alert(error?.message || "Erro ao guardar comercial.")
    }
  }

  return (
    <Card title="Editor Comercial por Projeto">
      <label>Projeto</label>
      <select
        value={selectedProjectId}
        onChange={(e) => setSelectedProjectId(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="">Selecionar projeto</option>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>
            {project.title} — {project.saga_name}
          </option>
        ))}
      </select>

      <label>Código interno</label>
      <input
        value={commercial.internal_code || ""}
        onChange={(e) => setCommercial((c) => ({ ...c, internal_code: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>ISBN</label>
      <input
        value={commercial.isbn || ""}
        onChange={(e) => setCommercial((c) => ({ ...c, isbn: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>ASIN</label>
      <input
        value={commercial.asin || ""}
        onChange={(e) => setCommercial((c) => ({ ...c, asin: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Preço</label>
      <input
        value={commercial.price || ""}
        onChange={(e) => setCommercial((c) => ({ ...c, price: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Moeda</label>
      <select
        value={commercial.currency || "EUR"}
        onChange={(e) => setCommercial((c) => ({ ...c, currency: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        {CURRENCIES.map((currency) => (
          <option key={currency} value={currency}>
            {currency}
          </option>
        ))}
      </select>

      <label>Selo comercial / coleção</label>
      <input
        value={commercial.collection_seal || ""}
        onChange={(e) => setCommercial((c) => ({ ...c, collection_seal: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Subtitle</label>
      <input
        value={commercial.subtitle || ""}
        onChange={(e) => setCommercial((c) => ({ ...c, subtitle: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Blurb</label>
      <textarea
        value={commercial.blurb || ""}
        onChange={(e) => setCommercial((c) => ({ ...c, blurb: e.target.value }))}
        rows={4}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }}
      />

      <label>Keywords (separadas por vírgula)</label>
      <input
        value={Array.isArray(commercial.keywords) ? commercial.keywords.join(", ") : commercial.keywords || ""}
        onChange={(e) => setCommercial((c) => ({ ...c, keywords: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Estado comercial</label>
      <select
        value={commercial.commercial_status || "draft"}
        onChange={(e) => setCommercial((c) => ({ ...c, commercial_status: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="draft">draft</option>
        <option value="ready">ready</option>
        <option value="published">published</option>
        <option value="archived">archived</option>
      </select>

      <div style={{ display: "grid", gap: 8 }}>
        <strong>Canais</strong>
        {CHANNELS.map((value) => (
          <label key={value} style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={(commercial.channels || []).includes(value)}
              onChange={() => toggleListValue("channels", value)}
            />
            {value}
          </label>
        ))}
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <strong>Marketplaces</strong>
        {MARKETPLACES.map((value) => (
          <label key={value} style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={(commercial.marketplaces || []).includes(value)}
              onChange={() => toggleListValue("marketplaces", value)}
            />
            {value}
          </label>
        ))}
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
        Guardar comercial
      </button>
    </Card>
  )
  }
