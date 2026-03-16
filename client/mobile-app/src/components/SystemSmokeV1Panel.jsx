import { useState } from "react"
import { runSystemSmokeV1 } from "../api.js"

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

export default function SystemSmokeV1Panel() {
  const [result, setResult] = useState(null)

  async function handleRun() {
    try {
      const res = await runSystemSmokeV1()
      setResult(res || null)
      alert("Smoke test v1 concluído.")
    } catch (error) {
      alert(error?.message || "Erro no smoke test v1.")
    }
  }

  return (
    <Card title="System Smoke V1">
      <button
        onClick={handleRun}
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
        Executar smoke test v1
      </button>

      {result ? (
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
          <div><strong>Status:</strong> {result.status}</div>
          <div><strong>Score:</strong> {result.score?.passed || 0}/{result.score?.total || 0}</div>
          <div><strong>Projeto:</strong> {result.project_id || "-"}</div>

          {(result.checks || []).map((check) => (
            <div key={check.key}>
              {check.ok ? "✅" : "❌"} {check.label}
              {typeof check.count !== "undefined" ? ` (${check.count})` : ""}
            </div>
          ))}
        </div>
      ) : null}
    </Card>
  )
      }
