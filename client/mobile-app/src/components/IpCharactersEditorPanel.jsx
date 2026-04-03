import { useEffect, useState } from "react"
import { getIpCharacterLockStatus, getIpCharacters, getIpCharactersConsistencySummary, listIps, updateIpCharacters } from "../api.js"

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

function SummaryChip({ label, value }) {
  return (
    <div style={{ padding: "10px 12px", borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.7)", minWidth: 120 }}>
      <div style={{ fontSize: 12, color: "#64748b", fontWeight: 700 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 800, color: "#0f172a" }}>{value}</div>
    </div>
  )
}

function parseCsv(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
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
    signature_item: "",
    visual_identity: {
      species: "baribudo",
      body_shape: "",
      fur_primary: "",
      fur_secondary: "",
      hair_style: "",
      eye_shape: "",
      eye_color: "",
      nose_shape: "",
      beard_style: "",
      distinctive_marks: [],
      silhouette_keywords: [],
    },
    wardrobe_identity: {
      core_outfit: "",
      accessories: [],
      forbidden_changes: [],
    },
    consistency_rules: {
      must_keep: [],
      can_vary: [],
      never_change: [],
    },
    reference_assets: {
      front: "",
      side: "",
      expression_sheet: "",
      turnaround: "",
    },
    prompt_guardrails: {
      positive: [],
      negative: [],
    },
  }
}

export default function IpCharactersEditorPanel({ user }) {
  const [ips, setIps] = useState([])
  const [selectedSlug, setSelectedSlug] = useState("")
  const [characters, setCharacters] = useState([])
  const [consistencySummary, setConsistencySummary] = useState(null)
  const [characterLock, setCharacterLock] = useState(null)

  useEffect(() => {
    loadIps()
  }, [])

  useEffect(() => {
    if (selectedSlug) {
      loadCharacters(selectedSlug)
      loadConsistency(selectedSlug)
      loadCharacterLock(selectedSlug)
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
      setCharacters((res?.main_characters || []).map((char) => ({
        ...emptyCharacter(),
        ...char,
        visual_identity: { ...emptyCharacter().visual_identity, ...(char?.visual_identity || {}) },
        wardrobe_identity: { ...emptyCharacter().wardrobe_identity, ...(char?.wardrobe_identity || {}) },
        consistency_rules: { ...emptyCharacter().consistency_rules, ...(char?.consistency_rules || {}) },
        reference_assets: { ...emptyCharacter().reference_assets, ...(char?.reference_assets || {}) },
        prompt_guardrails: { ...emptyCharacter().prompt_guardrails, ...(char?.prompt_guardrails || {}) },
      })))
    } catch (error) {
      alert(error?.message || "Erro ao carregar personagens.")
    }
  }

  async function loadConsistency(slug) {
    try {
      const res = await getIpCharactersConsistencySummary(slug, user)
      setConsistencySummary(res || null)
    } catch {
      setConsistencySummary(null)
    }
  }

  async function loadCharacterLock(slug) {
    try {
      const res = await getIpCharacterLockStatus(slug, user)
      setCharacterLock(res || null)
    } catch {
      setCharacterLock(null)
    }
  }

  function updateCharacter(index, patch) {
    setCharacters((current) => current.map((item, i) => (i === index ? { ...item, ...patch } : item)))
  }

  function updateNested(index, key, patch) {
    setCharacters((current) =>
      current.map((item, i) =>
        i === index ? { ...item, [key]: { ...(item?.[key] || {}), ...patch } } : item
      )
    )
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
        age: char.age === "" ? null : Number(char.age),
        traits: Array.isArray(char.traits) ? char.traits : [],
        visual_identity: {
          ...(char.visual_identity || {}),
          distinctive_marks: Array.isArray(char?.visual_identity?.distinctive_marks) ? char.visual_identity.distinctive_marks : [],
          silhouette_keywords: Array.isArray(char?.visual_identity?.silhouette_keywords) ? char.visual_identity.silhouette_keywords : [],
        },
        wardrobe_identity: {
          ...(char.wardrobe_identity || {}),
          accessories: Array.isArray(char?.wardrobe_identity?.accessories) ? char.wardrobe_identity.accessories : [],
          forbidden_changes: Array.isArray(char?.wardrobe_identity?.forbidden_changes) ? char.wardrobe_identity.forbidden_changes : [],
        },
        consistency_rules: {
          ...(char.consistency_rules || {}),
          must_keep: Array.isArray(char?.consistency_rules?.must_keep) ? char.consistency_rules.must_keep : [],
          can_vary: Array.isArray(char?.consistency_rules?.can_vary) ? char.consistency_rules.can_vary : [],
          never_change: Array.isArray(char?.consistency_rules?.never_change) ? char.consistency_rules.never_change : [],
        },
        reference_assets: {
          ...(char.reference_assets || {}),
          front: String(char?.reference_assets?.front || "").trim(),
          side: String(char?.reference_assets?.side || "").trim(),
          expression_sheet: String(char?.reference_assets?.expression_sheet || "").trim(),
          turnaround: String(char?.reference_assets?.turnaround || "").trim(),
        },
        prompt_guardrails: {
          ...(char.prompt_guardrails || {}),
          positive: Array.isArray(char?.prompt_guardrails?.positive) ? char.prompt_guardrails.positive : [],
          negative: Array.isArray(char?.prompt_guardrails?.negative) ? char.prompt_guardrails.negative : [],
        },
      }))

      await updateIpCharacters(selectedSlug, normalized, user)
      alert("Personagens guardadas.")
      await loadCharacters(selectedSlug)
      await loadConsistency(selectedSlug)
      await loadCharacterLock(selectedSlug)
    } catch (error) {
      alert(error?.message || "Erro ao guardar personagens.")
    }
  }

  const lockReady = Boolean(characterLock?.character_lock_ready)

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

      <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: lockReady ? "rgba(220,252,231,0.65)" : "rgba(254,226,226,0.7)" }}>
        <div style={{ fontWeight: 800, color: lockReady ? "#166534" : "#991b1b" }}>
          {lockReady ? "Character lock pronto para produção" : "Character lock ainda bloqueado"}
        </div>
        <div style={{ marginTop: 4 }}>
          {lockReady ? "A família principal está consistente para produção contínua." : `Itens a bloquear o lock: ${characterLock?.needs_attention ?? 0}`}
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <SummaryChip label="Personagens" value={consistencySummary?.count ?? characters.length} />
        <SummaryChip label="Completos" value={consistencySummary?.complete ?? 0} />
        <SummaryChip label="Precisam atenção" value={consistencySummary?.needs_attention ?? 0} />
      </div>

      {Array.isArray(characterLock?.blocking_items) && characterLock.blocking_items.length > 0 ? (
        <div style={{ display: "grid", gap: 8 }}>
          {characterLock.blocking_items.map((item) => (
            <div key={item.id || item.name} style={{ padding: 10, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(254,226,226,0.55)" }}>
              <div><strong>{item.name || item.id || "Sem nome"}</strong> — bloqueia o character lock</div>
              {Array.isArray(item.missing) && item.missing.length > 0 ? (
                <div style={{ color: "#991b1b", fontSize: 13 }}>Em falta: {item.missing.join(", ")}</div>
              ) : null}
            </div>
          ))}
        </div>
      ) : null}

      {Array.isArray(consistencySummary?.reports) && consistencySummary.reports.length > 0 ? (
        <div style={{ display: "grid", gap: 8 }}>
          {consistencySummary.reports.map((report) => (
            <div key={report.id || report.name} style={{ padding: 10, borderRadius: 12, border: "1px solid #e5e7eb", background: report.status === "complete" ? "rgba(220,252,231,0.6)" : "rgba(254,249,195,0.7)" }}>
              <div><strong>{report.name || report.id || "Sem nome"}</strong> — {report.status === "complete" ? "Consistente" : "Precisa atenção"}</div>
              {Array.isArray(report.missing) && report.missing.length > 0 ? (
                <div style={{ color: "#854d0e", fontSize: 13 }}>Em falta: {report.missing.join(", ")}</div>
              ) : null}
            </div>
          ))}
        </div>
      ) : null}

      <button onClick={addCharacter} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#2F5E2E", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
        Adicionar personagem
      </button>

      {characters.map((char, index) => (
        <div key={`${char.id || "new"}-${index}`} style={{ display: "grid", gap: 10, padding: 12, border: "1px solid #e5e7eb", borderRadius: 12, background: "rgba(255,255,255,0.55)" }}>
          <div style={{ fontWeight: 800, color: "#2F5E2E" }}>Base</div>
          <input value={char.id || ""} onChange={(e) => updateCharacter(index, { id: e.target.value })} placeholder="ID interno" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char.name || ""} onChange={(e) => updateCharacter(index, { name: e.target.value })} placeholder="Nome" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char.role || ""} onChange={(e) => updateCharacter(index, { role: e.target.value })} placeholder="Papel (father, mother, child...)" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char.age ?? ""} onChange={(e) => updateCharacter(index, { age: e.target.value })} placeholder="Idade" type="number" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char.archetype || ""} onChange={(e) => updateCharacter(index, { archetype: e.target.value })} placeholder="Arquétipo" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={(char.traits || []).join(", ")} onChange={(e) => updateCharacter(index, { traits: parseCsv(e.target.value) })} placeholder="Traços separados por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <input type="color" value={char.accent_color || "#6FA86A"} onChange={(e) => updateCharacter(index, { accent_color: e.target.value })} style={{ width: 52, height: 40, border: "none", background: "transparent" }} />
            <input value={char.accent_color || ""} onChange={(e) => updateCharacter(index, { accent_color: e.target.value })} placeholder="#000000" style={{ flex: 1, padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          </div>
          <input value={char.signature_item || ""} onChange={(e) => updateCharacter(index, { signature_item: e.target.value })} placeholder="Item assinatura / acessório principal" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

          <div style={{ fontWeight: 800, color: "#2F5E2E", marginTop: 6 }}>Identidade visual</div>
          <input value={char?.visual_identity?.body_shape || ""} onChange={(e) => updateNested(index, "visual_identity", { body_shape: e.target.value })} placeholder="Forma corporal / silhueta" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.visual_identity?.fur_primary || ""} onChange={(e) => updateNested(index, "visual_identity", { fur_primary: e.target.value })} placeholder="Pelo principal" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.visual_identity?.fur_secondary || ""} onChange={(e) => updateNested(index, "visual_identity", { fur_secondary: e.target.value })} placeholder="Pelo secundário" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.visual_identity?.hair_style || ""} onChange={(e) => updateNested(index, "visual_identity", { hair_style: e.target.value })} placeholder="Estilo de cabelo/topo" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.visual_identity?.eye_shape || ""} onChange={(e) => updateNested(index, "visual_identity", { eye_shape: e.target.value })} placeholder="Forma dos olhos" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.visual_identity?.eye_color || ""} onChange={(e) => updateNested(index, "visual_identity", { eye_color: e.target.value })} placeholder="Cor dos olhos" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.visual_identity?.nose_shape || ""} onChange={(e) => updateNested(index, "visual_identity", { nose_shape: e.target.value })} placeholder="Forma do nariz" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.visual_identity?.beard_style || ""} onChange={(e) => updateNested(index, "visual_identity", { beard_style: e.target.value })} placeholder="Estilo de barba" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={(char?.visual_identity?.distinctive_marks || []).join(", ")} onChange={(e) => updateNested(index, "visual_identity", { distinctive_marks: parseCsv(e.target.value) })} placeholder="Marcas distintivas separadas por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={(char?.visual_identity?.silhouette_keywords || []).join(", ")} onChange={(e) => updateNested(index, "visual_identity", { silhouette_keywords: parseCsv(e.target.value) })} placeholder="Keywords de silhueta separadas por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

          <div style={{ fontWeight: 800, color: "#2F5E2E", marginTop: 6 }}>Wardrobe identity</div>
          <input value={char?.wardrobe_identity?.core_outfit || ""} onChange={(e) => updateNested(index, "wardrobe_identity", { core_outfit: e.target.value })} placeholder="Roupa base / outfit principal" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={(char?.wardrobe_identity?.accessories || []).join(", ")} onChange={(e) => updateNested(index, "wardrobe_identity", { accessories: parseCsv(e.target.value) })} placeholder="Acessórios separados por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={(char?.wardrobe_identity?.forbidden_changes || []).join(", ")} onChange={(e) => updateNested(index, "wardrobe_identity", { forbidden_changes: parseCsv(e.target.value) })} placeholder="Mudanças proibidas" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

          <div style={{ fontWeight: 800, color: "#2F5E2E", marginTop: 6 }}>Regras de consistência</div>
          <input value={(char?.consistency_rules?.must_keep || []).join(", ")} onChange={(e) => updateNested(index, "consistency_rules", { must_keep: parseCsv(e.target.value) })} placeholder="Deve manter sempre" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={(char?.consistency_rules?.can_vary || []).join(", ")} onChange={(e) => updateNested(index, "consistency_rules", { can_vary: parseCsv(e.target.value) })} placeholder="Pode variar" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={(char?.consistency_rules?.never_change || []).join(", ")} onChange={(e) => updateNested(index, "consistency_rules", { never_change: parseCsv(e.target.value) })} placeholder="Nunca mudar" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

          <div style={{ fontWeight: 800, color: "#2F5E2E", marginTop: 6 }}>Reference assets</div>
          <input value={char?.reference_assets?.front || ""} onChange={(e) => updateNested(index, "reference_assets", { front: e.target.value })} placeholder="Asset referência frontal" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.reference_assets?.side || ""} onChange={(e) => updateNested(index, "reference_assets", { side: e.target.value })} placeholder="Asset referência lateral" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.reference_assets?.expression_sheet || ""} onChange={(e) => updateNested(index, "reference_assets", { expression_sheet: e.target.value })} placeholder="Expression sheet" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={char?.reference_assets?.turnaround || ""} onChange={(e) => updateNested(index, "reference_assets", { turnaround: e.target.value })} placeholder="Turnaround / rotação" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

          <div style={{ fontWeight: 800, color: "#2F5E2E", marginTop: 6 }}>Guardrails de prompt</div>
          <input value={(char?.prompt_guardrails?.positive || []).join(", ")} onChange={(e) => updateNested(index, "prompt_guardrails", { positive: parseCsv(e.target.value) })} placeholder="Prompts positivos" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
          <input value={(char?.prompt_guardrails?.negative || []).join(", ")} onChange={(e) => updateNested(index, "prompt_guardrails", { negative: parseCsv(e.target.value) })} placeholder="Prompts negativos" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

          <button onClick={() => removeCharacter(index)} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#991b1b", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
            Remover personagem
          </button>
        </div>
      ))}

      <button onClick={handleSave} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#2F5E2E", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
        Guardar personagens
      </button>
    </Card>
  )
}
