import { useEffect, useState } from "react"
import { getSagaRuntime, listIps } from "../api.js"

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
      <h3 style={{ margin: 0 }}>{title}</h3>
      {children}
    </div>
  )
}

export default function SagaRuntimePanel({ user }) {
  const [ips, setIps] = useState([])
  const [selectedSlug, setSelectedSlug] = useState("")
  const [runtime, setRuntime] = useState(null)

  useEffect(() => {
    loadIps()
  }, [])

  useEffect(() => {
    if (selectedSlug) {
      loadRuntime(selectedSlug)
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

  async function loadRuntime(slug) {
    try {
      const res = await getSagaRuntime(slug)
      setRuntime(res?.runtime || null)
    } catch (error) {
      alert(error?.message || "Erro ao carregar runtime da saga.")
    }
  }

  return (
    <Card title="Saga Runtime Engine">
      <label>IP / Saga</label>
      <select
        value={selectedSlug}
        onChange={(e) => setSelectedSlug(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        <option value="">Selecionar saga</option>
        {ips.map((item) => (
          <option key={item.id} value={item.slug}>
            {item.name}
          </option>
        ))}
      </select>

      {runtime ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            border: "1px solid #e5e7eb",
            background: "rgba(255,255,255,0.55)",
            display: "grid",
            gap: 8
          }}
        >
          <div><strong>Nome:</strong> {runtime.name}</div>
          <div><strong>Slug:</strong> {runtime.slug}</div>
          <div><strong>Default language:</strong> {runtime.default_language}</div>
          <div><strong>Output languages:</strong> {(runtime.output_languages || []).join(", ")}</div>
          <div><strong>Series name:</strong> {runtime?.resolved?.series_name || "-"}</div>
          <div><strong>Producer:</strong> {runtime?.resolved?.producer || "-"}</div>
          <div><strong>Target age:</strong> {runtime?.resolved?.target_age || "-"}</div>
          <div><strong>Validation OK:</strong> {runtime?.validation?.ok ? "Sim" : "Não"}</div>
          <div><strong>Warnings:</strong> {(runtime?.validation?.warnings || []).join(", ") || "-"}</div>

          <textarea
            readOnly
            value={JSON.stringify(runtime, null, 2)}
            rows={22}
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
        </div>
      ) : null}
    </Card>
  )
      }
