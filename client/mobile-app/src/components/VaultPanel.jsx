import { useEffect, useState } from "react"
import {
  createVault,
  deleteVault,
  exportVault,
  listVaults,
} from "../api.js"

function canManageVaults(user) {
  const role = String(user?.role || "").toLowerCase()
  const name = String(user?.name || "").toLowerCase()
  return ["owner", "creator", "admin"].includes(role) || ["andré", "andre", "esposa", "wife", "mama"].includes(name)
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

export default function VaultPanel({ user }) {
  const [vaults, setVaults] = useState([])
  const [loading, setLoading] = useState(false)
  const [name, setName] = useState("")
  const [target, setTarget] = useState("website")
  const [environment, setEnvironment] = useState("local")
  const [fileName, setFileName] = useState(".env")
  const [notes, setNotes] = useState("")
  const [rawText, setRawText] = useState("")

  useEffect(() => {
    loadVaults()
  }, [])

  async function loadVaults() {
    setLoading(true)
    try {
      const response = await listVaults()
      setVaults(response?.vaults || [])
    } catch (error) {
      alert(error?.message || "Falha ao carregar cofre local.")
    } finally {
      setLoading(false)
    }
  }

  async function handleCreateVault() {
    if (!canManageVaults(user)) {
      alert("Sem permissão para gerir credenciais.")
      return
    }
    if (!name.trim()) {
      alert("Indica um nome para o vault.")
      return
    }
    setLoading(true)
    try {
      await createVault({
        name: name.trim(),
        target,
        environment,
        file_name: fileName.trim() || ".env",
        raw_text: rawText,
        notes: notes.trim(),
      })
      setName("")
      setTarget("website")
      setEnvironment("local")
      setFileName(".env")
      setNotes("")
      setRawText("")
      await loadVaults()
    } catch (error) {
      alert(error?.message || "Falha ao criar vault.")
    } finally {
      setLoading(false)
    }
  }

  async function handleDeleteVault(vault) {
    if (!canManageVaults(user)) {
      alert("Sem permissão para apagar credenciais.")
      return
    }
    if (!window.confirm(`Apagar o vault ${vault.name}?`)) return
    setLoading(true)
    try {
      await deleteVault(vault.id)
      await loadVaults()
    } catch (error) {
      alert(error?.message || "Falha ao apagar vault.")
    } finally {
      setLoading(false)
    }
  }

  async function handleExportVault(vault) {
    setLoading(true)
    try {
      const response = await exportVault(vault.id)
      const content = String(response?.content || "")
      await navigator.clipboard.writeText(content)
      alert(`Vault exportado e copiado para a área de transferência: ${vault.file_name || '.env'}`)
    } catch (error) {
      alert(error?.message || "Falha ao exportar vault.")
    } finally {
      setLoading(false)
    }
  }

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
      <h3 style={{ margin: 0, color: "#2F5E2E" }}>Credential Vault / .env local</h3>

      <div style={{ display: "grid", gap: 8, padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
        <div><strong>Objetivo</strong></div>
        <div>Guardar e gerir credenciais localmente no Studio, fora do Website e fora do frontend público.</div>
        <div>Este cofre é a base para Website, Vercel, Supabase, Render e restantes integrações.</div>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nome do vault" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }} />
        <input value={fileName} onChange={(e) => setFileName(e.target.value)} placeholder="Nome do ficheiro (.env.website)" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }} />
        <select value={target} onChange={(e) => setTarget(e.target.value)} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }}>
          <option value="website">Website</option>
          <option value="vercel">Vercel</option>
          <option value="supabase">Supabase</option>
          <option value="render">Render</option>
          <option value="twilio">Twilio</option>
          <option value="custom">Custom</option>
        </select>
        <input value={environment} onChange={(e) => setEnvironment(e.target.value)} placeholder="Ambiente (local, preview, production...)" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }} />
        <input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Notas" style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db" }} />
        <textarea value={rawText} onChange={(e) => setRawText(e.target.value)} placeholder="Cola aqui o conteúdo do .env" rows={10} style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", fontFamily: "monospace" }} />
        <ActionButton onClick={handleCreateVault} disabled={loading || !canManageVaults(user)}>
          Guardar no cofre local
        </ActionButton>
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        <div><strong>Vaults guardados</strong></div>
        {vaults.length === 0 ? <div>Sem vaults locais ainda.</div> : null}
        {vaults.map((vault) => (
          <div key={vault.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
            <div><strong>{vault.name}</strong></div>
            <div>Target: {vault.target} · Environment: {vault.environment}</div>
            <div>Ficheiro: {vault.file_name}</div>
            <div>Rows: {(vault.rows || []).length}</div>
            <div>Notas: {vault.notes || "-"}</div>
            <div style={{ display: "grid", gap: 4 }}>
              {(vault.rows || []).filter((row) => row.kind === "entry").slice(0, 8).map((row) => (
                <div key={row.id} style={{ fontFamily: "monospace", fontSize: 13 }}>
                  {row.key}= {row.masked_value || ""}
                </div>
              ))}
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <ActionButton onClick={() => handleExportVault(vault)} disabled={loading} tone="secondary">
                Exportar / copiar
              </ActionButton>
              <ActionButton onClick={() => handleDeleteVault(vault)} disabled={loading || !canManageVaults(user)} tone="danger">
                Apagar
              </ActionButton>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
