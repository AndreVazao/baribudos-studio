import { useEffect, useState } from "react"
import { getIpCanon, listIps, updateIpCanon } from "../api.js"

const CANON_OPTIONS = [
  { value: "visual", label: "Visual Canon" },
  { value: "narrative", label: "Narrative Canon" },
  { value: "episode", label: "Episode Canon" },
  { value: "series_arc", label: "Series Arc Canon" },
  { value: "pedagogical", label: "Pedagogical Canon" },
  { value: "age_badge", label: "Age Badge Canon" },
  { value: "characters", label: "Characters Master" }
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

export default function IpCanonsEditorPanel({ user }) {
  const [ips, setIps] = useState([])
  const [selectedSlug, setSelectedSlug] = useState("")
  const [canonType, setCanonType] = useState("visual")
  const [jsonText, setJsonText] = useState("{}")

  useEffect(() => {
    loadIps()
  }, [])

  useEffect(() => {
    if (selectedSlug && canonType) {
      loadCanon(selectedSlug, canonType)
    }
  }, [selectedSlug, canonType])

  async function loadIps() {
    const res = await listIps(user)
    const list = res?.ips || []
    setIps(list)
    if (!selectedSlug && list.length) {
      setSelectedSlug(list[0].slug)
    }
  }

  async function loadCanon(slug, type) {
    try {
      const res = await getIpCanon(slug, type, user)
      setJsonText(JSON.stringify(res?.data || {}, null, 2))
    } catch (error) {
      alert(error?.message || "Erro ao carregar canon.")
    }
  }

  async function handleSave() {
    if (!selectedSlug || !canonType) return

    try {
      const parsed = JSON.parse(jsonText)
      await updateIpCanon(selectedSlug, canonType, parsed, user)
      alert("Canon guardado.")
      await loadCanon(selectedSlug, canonType)
    } catch (error) {
      alert(error?.message || "JSON inválido ou erro ao guardar.")
    }
  }

  return (
    <Card title="Editor de Canons por IP">
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

      <label>Tipo de canon</label>
      <select
        value={canonType}
        onChange={(e) => setCanonType(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        {CANON_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <textarea
        value={jsonText}
        onChange={(e) => setJsonText(e.target.value)}
        rows={24}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 12,
          border: "1px solid #d1d5db",
          outline: "none",
          fontFamily: "monospace",
          fontSize: 13,
          resize: "vertical"
        }}
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
        Guardar canon
      </button>
    </Card>
  )
  }
