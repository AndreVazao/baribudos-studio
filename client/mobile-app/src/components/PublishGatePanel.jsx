import React from "react"

export default function PublishGatePanel() {
  return (
    <div style={{
      padding: 16,
      background: "#1e293b",
      borderRadius: 12,
      marginTop: 12
    }}>
      <h3 style={{ color: "white" }}>Publishing Gate</h3>

      <p style={{ color: "#94a3b8" }}>
        Este painel irá controlar permissões de publicação,
        revisão editorial e autorização final.
      </p>

      <div style={{ marginTop: 10 }}>
        <button style={{
          padding: "8px 12px",
          background: "#22c55e",
          border: "none",
          borderRadius: 8,
          color: "white"
        }}>
          Aprovar Publicação
        </button>
      </div>
    </div>
  )
        }
