import { useEffect, useState } from "react"
import { getIpCharacters, listIps, updateIpCharacters } from "../api.js"

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

function emptyCharacter() {
  return {
    id: "",
    name: "",
    role: "",
    age: "",
    archetype: "",
    traits: [],
    accent_color: "#6FA86A",
    signature_item: ""
  }
}

export default function IpCharactersEditorPanel({ user }) {
  const [ips, setIps] = useState([])
  const [selectedSlug, setSelectedSlug] = useState("")
  const [characters, setCharacters] = useState([])

  useEffect(() => {
    loadIps()
  }, [])

  useEffect(() => {
    if (selectedSlug) {
      loadCharacters(selectedSlug)
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

  async function loadCharacters(slug) {
    try {
      const res = await getIpCharacters(slug, user)
      setCharacters(res?.main_characters || [])
    } catch (error) {
      alert(error?.message || "Erro ao carregar personagens.")
    }
  }

  function updateCharacter(index, patch) {
    setCharacters((current) =>
      current.map((item, i) => (i === index ? { ...item, ...patch } : item))
    )
  }

  function updateTraits(index, value) {
    const traits = String(value || "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)

    updateCharacter(index, { traits })
  }

  function addCharacter() {
    setCharacters((current) => [...current, emptyCharacter()])
  }

  function removeCharacter(index) {
    setCharacters((current) => current.filter((_, i) => i !== index))
  }

  async function handleSave() {
    if (!selectedSlug) return

    try {
      const normalized = characters.map((char) => ({
        ...char,
        age: char.age === "" ? null : Number(char.age)
      }))

      await updateIpCharacters(selectedSlug, normalized, user)
      alert("Personagens guardadas.")
      await loadCharacters(selectedSlug)
    } catch (error) {
      alert(error?.message || "Erro ao guardar personagens.")
    }
  }

  return (
    <Card title="Editor de Personagens Principais por IP">
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

      <button
        onClick={addCharacter}
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
        Adicionar personagem
      </button>

      {characters.map((char, index) => (
        <div
          key={`${char.id || "new"}-${index}`}
          style={{
            display: "grid",
            gap: 10,
            padding: 12,
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            background: "rgba(255,255,255,0.55)"
          }}
        >
          <input
            value={char.id || ""}
            onChange={(e) => updateCharacter(index, { id: e.target.value })}
            placeholder="ID interno"
            style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
          />

          <input
            value={char.name || ""}
            onChange={(e) => updateCharacter(index, { name: e.target.value })}
            placeholder="Nome"
            style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
          />

          <input
            value={char.role || ""}
            onChange={(e) => updateCharacter(index, { role: e.target.value })}
            placeholder="Papel (father, mother, hero, child, mentor...)"
            style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
          />

          <input
            value={char.age ?? ""}
            onChange={(e) => updateCharacter(index, { age: e.target.value })}
            placeholder="Idade"
            type="number"
            style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
          />

          <input
            value={char.archetype || ""}
            onChange={(e) => updateCharacter(index, { archetype: e.target.value })}
            placeholder="Arquétipo"
            style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
          />

          <input
            value={(char.traits || []).join(", ")}
            onChange={(e) => updateTraits(index, e.target.value)}
            placeholder="Traços separados por vírgula"
            style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
          />

          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <input
              type="color"
              value={char.accent_color || "#6FA86A"}
              onChange={(e) => updateCharacter(index, { accent_color: e.target.value })}
              style={{ width: 52, height: 40, border: "none", background: "transparent" }}
            />
            <input
              value={char.accent_color || ""}
              onChange={(e) => updateCharacter(index, { accent_color: e.target.value })}
              placeholder="#000000"
              style={{ flex: 1, padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
            />
          </div>

          <input
            value={char.signature_item || ""}
            onChange={(e) => updateCharacter(index, { signature_item: e.target.value })}
            placeholder="Item assinatura / acessório principal"
            style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
          />

          <button
            onClick={() => removeCharacter(index)}
            style={{
              padding: "10px 12px",
              borderRadius: 12,
              border: "none",
              background: "#991b1b",
              color: "#fff",
              fontWeight: 700,
              cursor: "pointer"
            }}
          >
            Remover personagem
          </button>
        </div>
      ))}

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
        Guardar personagens
      </button>
    </Card>
  )
      }
