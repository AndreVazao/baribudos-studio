import { useEffect, useState } from "react"
import { createIp, getIpPermissions, listIps } from "../api.js"

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

export default function IpCreatorPanel({ user }) {
  const [ips, setIps] = useState([])
  const [selectedSlug, setSelectedSlug] = useState("")
  const [permissions, setPermissions] = useState(null)

  const [name, setName] = useState("")
  const [defaultLanguage, setDefaultLanguage] = useState("pt-PT")
  const [privateOnly, setPrivateOnly] = useState(true)

  useEffect(() => {
    loadIps()
  }, [])

  useEffect(() => {
    if (selectedSlug) {
      loadPermissions(selectedSlug)
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

  async function loadPermissions(slug) {
    const res = await getIpPermissions(slug, user)
    setPermissions(res || null)
  }

  async function handleCreateIp() {
    if (!name.trim()) return

    await createIp({
      name,
      owner_id: user?.id || "",
      owner_name: user?.name || "",
      exclusive: false,
      visible_to_owner_only: privateOnly,
      editable_by_roles: ["owner", "admin"],
      publishable_by_roles: ["owner", "admin"],
      cloneable: true,
      default_language: defaultLanguage,
      output_languages: [defaultLanguage],
      brand_assets: {
        studio_logo: "public/brand/baribudos-studio-logo.png",
        series_logo: "",
        seal_logo: ""
      }
    })

    setName("")
    await loadIps()
    alert("Nova IP criada.")
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <Card title="As minhas IPs / Sagas">
        {ips.length === 0 ? <div>Sem IPs visíveis para este user.</div> : null}

        {ips.map((item) => (
          <button
            key={item.id}
            onClick={() => setSelectedSlug(item.slug)}
            style={{
              textAlign: "left",
              padding: 12,
              borderRadius: 12,
              border: selectedSlug === item.slug ? "2px solid #2F5E2E" : "1px solid #d1d5db",
              background: "#fff",
              cursor: "pointer"
            }}
          >
            <div><strong>{item.name}</strong></div>
            <div>Slug: {item.slug}</div>
            <div>Owner: {item.owner_name || "-"}</div>
            <div>Exclusiva: {item.exclusive ? "Sim" : "Não"}</div>
            <div>Privada: {item.visible_to_owner_only ? "Sim" : "Não"}</div>
            <div>Língua default: {item.default_language || "-"}</div>
          </button>
        ))}
      </Card>

      <Card title="Permissões da saga selecionada">
        {selectedSlug ? <div><strong>Saga:</strong> {selectedSlug}</div> : null}
        <div><strong>Pode editar:</strong> {permissions?.can_edit ? "Sim" : "Não"}</div>
        <div><strong>Pode publicar:</strong> {permissions?.can_publish ? "Sim" : "Não"}</div>
      </Card>

      <Card title="Criar nova IP / Saga">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome da IP"
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        />

        <select
          value={defaultLanguage}
          onChange={(e) => setDefaultLanguage(e.target.value)}
          style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
        >
          <option value="pt-PT">Português (PT-PT)</option>
          <option value="pt-BR">Português (PT-BR)</option>
          <option value="en">English</option>
          <option value="es">Español</option>
          <option value="fr">Français</option>
          <option value="de">Deutsch</option>
          <option value="it">Italiano</option>
          <option value="nl">Nederlands</option>
          <option value="zh">中文</option>
          <option value="ja">日本語</option>
        </select>

        <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input
            type="checkbox"
            checked={privateOnly}
            onChange={(e) => setPrivateOnly(e.target.checked)}
          />
          Visível só para o criador
        </label>

        <button
          onClick={handleCreateIp}
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
          Criar nova IP
        </button>
      </Card>
    </div>
  )
        }
