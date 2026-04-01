import { useEffect, useMemo, useState } from "react"
import { createVoiceProfile, listIps, listVoiceProfiles, updateVoiceProfile, validateVoiceProfile } from "../api.js"

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

function parseCsv(value) {
  return String(value || "").split(",").map((item) => item.trim()).filter(Boolean)
}

const EMPTY_FORM = {
  display_name: "",
  owner_person_id: "",
  owner_person_name: "",
  credited_name: "",
  voice_type: "narrator",
  source_type: "recorded_human",
  clone_provider: "xtts",
  language: "pt-PT",
  accent: "pt-PT",
  gender_hint: "",
  age_hint: "adult",
  consent_status: "pending",
  credit_visibility: "product_and_website",
  allowed_ips: [],
  allowed_sagas: [],
  allowed_roles: [],
  default_for_roles: [],
  sample_audio_paths: [],
  reference_text: "",
  notes: "",
  active: true,
  voice_variation_policy: {
    allow_variants: true,
    pitch_range_min: -2,
    pitch_range_max: 2,
    tone_range_min: -2,
    tone_range_max: 2,
    speed_range_min: 0.9,
    speed_range_max: 1.1,
    variant_notes: "Apenas variações subtis da voz original/clonada."
  }
}

export default function VoiceProfilesPanel({ user }) {
  const [items, setItems] = useState([])
  const [ips, setIps] = useState([])
  const [form, setForm] = useState(EMPTY_FORM)
  const [selectedIpSlug, setSelectedIpSlug] = useState("")
  const [selectedRole, setSelectedRole] = useState("narrator")
  const [validationResult, setValidationResult] = useState(null)

  useEffect(() => { refreshAll() }, [])
  const selectedIp = useMemo(() => ips.find((item) => item.slug === selectedIpSlug) || null, [ips, selectedIpSlug])

  async function refreshAll() {
    const [voiceProfilesRes, ipsRes] = await Promise.all([listVoiceProfiles(), listIps(user)])
    const voiceProfiles = voiceProfilesRes?.voice_profiles || []
    const ipsList = ipsRes?.ips || []
    setItems(voiceProfiles)
    setIps(ipsList)
    if (!selectedIpSlug && ipsList.length) setSelectedIpSlug(ipsList[0].slug)
  }

  function updateForm(patch) { setForm((current) => ({ ...current, ...patch })) }
  function updateVariationPolicy(patch) {
    setForm((current) => ({
      ...current,
      voice_variation_policy: { ...(current.voice_variation_policy || {}), ...patch }
    }))
  }

  async function handleCreate() {
    try {
      await createVoiceProfile(form)
      setForm(EMPTY_FORM)
      alert("Voice profile criada.")
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Erro ao criar voice profile.")
    }
  }

  async function handleToggleActive(item) {
    try {
      await updateVoiceProfile(item.id, { active: !Boolean(item?.active) })
      await refreshAll()
    } catch (error) {
      alert(error?.message || "Erro ao atualizar voice profile.")
    }
  }

  async function handleValidate(item) {
    try {
      const res = await validateVoiceProfile(item.id, { ip_slug: selectedIp?.slug || "", saga_slug: selectedIp?.slug || "", role: selectedRole })
      setValidationResult({ item, result: res })
    } catch (error) {
      alert(error?.message || "Erro ao validar voice profile.")
    }
  }

  return (
    <Card title="Voice Profiles / Clones de Voz">
      <div style={{ display: "grid", gap: 10, padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
        <div><strong>Criar perfil vocal</strong></div>
        <div style={{ color: "#475569", fontSize: 13 }}>O clone e quaisquer variações ficam sempre ligados ao dono real da voz original para créditos automáticos.</div>

        <input value={form.display_name} onChange={(e) => updateForm({ display_name: e.target.value })} placeholder="Nome do perfil vocal" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.owner_person_id} onChange={(e) => updateForm({ owner_person_id: e.target.value })} placeholder="ID da pessoa dona da voz" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.owner_person_name} onChange={(e) => updateForm({ owner_person_name: e.target.value })} placeholder="Nome da pessoa dona da voz" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.credited_name} onChange={(e) => updateForm({ credited_name: e.target.value })} placeholder="Nome para créditos automáticos" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

        <select value={form.voice_type} onChange={(e) => updateForm({ voice_type: e.target.value })} style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
          <option value="narrator">Narrator</option>
          <option value="character">Character</option>
          <option value="ambient">Ambient</option>
          <option value="promo">Promo</option>
          <option value="system">System</option>
        </select>

        <select value={form.source_type} onChange={(e) => updateForm({ source_type: e.target.value })} style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
          <option value="recorded_human">Recorded human</option>
          <option value="cloned_voice">Cloned voice</option>
          <option value="synthetic_hybrid">Synthetic hybrid</option>
        </select>

        <select value={form.consent_status} onChange={(e) => updateForm({ consent_status: e.target.value })} style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="restricted">Restricted</option>
          <option value="revoked">Revoked</option>
        </select>

        <select value={form.credit_visibility} onChange={(e) => updateForm({ credit_visibility: e.target.value })} style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
          <option value="internal_only">Internal only</option>
          <option value="product_only">Product only</option>
          <option value="product_and_website">Product and website</option>
          <option value="all_promotional">All promotional</option>
        </select>

        <input value={form.language} onChange={(e) => updateForm({ language: e.target.value })} placeholder="Língua" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.accent} onChange={(e) => updateForm({ accent: e.target.value })} placeholder="Accent" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.clone_provider} onChange={(e) => updateForm({ clone_provider: e.target.value })} placeholder="Clone provider" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.gender_hint} onChange={(e) => updateForm({ gender_hint: e.target.value })} placeholder="Gender hint" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.age_hint} onChange={(e) => updateForm({ age_hint: e.target.value })} placeholder="Age hint" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.allowed_ips.join(", ")} onChange={(e) => updateForm({ allowed_ips: parseCsv(e.target.value) })} placeholder="Allowed IPs separados por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.allowed_sagas.join(", ")} onChange={(e) => updateForm({ allowed_sagas: parseCsv(e.target.value) })} placeholder="Allowed sagas separadas por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.allowed_roles.join(", ")} onChange={(e) => updateForm({ allowed_roles: parseCsv(e.target.value) })} placeholder="Allowed roles separados por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
        <input value={form.default_for_roles.join(", ")} onChange={(e) => updateForm({ default_for_roles: parseCsv(e.target.value) })} placeholder="Roles default separados por vírgula" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />

        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #dbe4d8", background: "rgba(240,253,244,0.85)", display: "grid", gap: 8 }}>
          <strong>Variações controladas do clone</strong>
          <label><input type="checkbox" checked={form.voice_variation_policy?.allow_variants !== false} onChange={(e) => updateVariationPolicy({ allow_variants: e.target.checked })} /> Permitir variações controladas da voz clonada</label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 8 }}>
            <input type="number" value={form.voice_variation_policy?.pitch_range_min ?? -2} onChange={(e) => updateVariationPolicy({ pitch_range_min: Number(e.target.value) })} placeholder="Pitch mín" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
            <input type="number" value={form.voice_variation_policy?.pitch_range_max ?? 2} onChange={(e) => updateVariationPolicy({ pitch_range_max: Number(e.target.value) })} placeholder="Pitch máx" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
            <input type="number" value={form.voice_variation_policy?.tone_range_min ?? -2} onChange={(e) => updateVariationPolicy({ tone_range_min: Number(e.target.value) })} placeholder="Tom mín" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
            <input type="number" value={form.voice_variation_policy?.tone_range_max ?? 2} onChange={(e) => updateVariationPolicy({ tone_range_max: Number(e.target.value) })} placeholder="Tom máx" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
            <input type="number" step="0.01" value={form.voice_variation_policy?.speed_range_min ?? 0.9} onChange={(e) => updateVariationPolicy({ speed_range_min: Number(e.target.value) })} placeholder="Velocidade mín" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
            <input type="number" step="0.01" value={form.voice_variation_policy?.speed_range_max ?? 1.1} onChange={(e) => updateVariationPolicy({ speed_range_max: Number(e.target.value) })} placeholder="Velocidade máx" style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none" }} />
          </div>
          <textarea value={form.voice_variation_policy?.variant_notes || ""} onChange={(e) => updateVariationPolicy({ variant_notes: e.target.value })} rows={2} placeholder="Notas sobre os limites das variações" style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />
        </div>

        <textarea value={form.reference_text} onChange={(e) => updateForm({ reference_text: e.target.value })} rows={2} placeholder="Texto de referência" style={{ width: "100%", padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />
        <textarea value={form.notes} onChange={(e) => updateForm({ notes: e.target.value })} rows={2} placeholder="Notas" style={{ width: "100%", padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }} />

        <button onClick={handleCreate} style={{ padding: "10px 12px", borderRadius: 12, border: "none", background: "#2F5E2E", color: "#fff", fontWeight: 700, cursor: "pointer" }}>Criar voice profile</button>
      </div>

      <div style={{ display: "grid", gap: 10, padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)" }}>
        <div><strong>Validar contexto</strong></div>
        <select value={selectedIpSlug} onChange={(e) => setSelectedIpSlug(e.target.value)} style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}>
          <option value="">Selecionar IP</option>
          {ips.map((ip) => <option key={ip.id} value={ip.slug}>{ip.name}</option>)}
        </select>
        <input value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)} placeholder="Role para validar" style={{ padding: 10, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }} />
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        {items.map((item) => (
          <div key={item.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: "rgba(255,255,255,0.55)", display: "grid", gap: 6 }}>
            <div><strong>{item.display_name}</strong> — {item.voice_type}</div>
            <div>Owner real: {item.owner_person_name || item.owner_person_id || "-"}</div>
            <div>Crédito automático: {item.credited_name || item.owner_person_name || "-"}</div>
            <div>Consentimento: {item.consent_status} · Ativa: {item.active ? "Sim" : "Não"}</div>
            <div>Variações permitidas: {item.voice_variation_policy?.allow_variants === false ? "Não" : "Sim"}</div>
            <div>Pitch: {item.voice_variation_policy?.pitch_range_min ?? "-"} a {item.voice_variation_policy?.pitch_range_max ?? "-"} · Tom: {item.voice_variation_policy?.tone_range_min ?? "-"} a {item.voice_variation_policy?.tone_range_max ?? "-"}</div>
            <div>Velocidade: {item.voice_variation_policy?.speed_range_min ?? "-"} a {item.voice_variation_policy?.speed_range_max ?? "-"}</div>
            <div>Escopo IPs: {(item.allowed_ips || []).join(", ") || "global"}</div>
            <div>Escopo sagas: {(item.allowed_sagas || []).join(", ") || "global"}</div>
            <div>Roles: {(item.allowed_roles || []).join(", ") || "qualquer"}</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button onClick={() => handleToggleActive(item)} style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #cbd5e1", background: "#fff", color: "#111827", cursor: "pointer" }}>{item.active ? "Desativar" : "Ativar"}</button>
              <button onClick={() => handleValidate(item)} style={{ padding: "8px 10px", borderRadius: 10, border: "none", background: "#7c3aed", color: "#fff", cursor: "pointer" }}>Validar contexto</button>
            </div>
          </div>
        ))}
        {items.length === 0 ? <div>Sem voice profiles ainda.</div> : null}
      </div>

      {validationResult ? (
        <div style={{ padding: 12, borderRadius: 12, border: "1px solid #e5e7eb", background: validationResult.result?.usable ? "rgba(220,252,231,0.6)" : "rgba(254,226,226,0.7)", display: "grid", gap: 6 }}>
          <div><strong>Validação:</strong> {validationResult.item?.display_name}</div>
          <div>Usável: {validationResult.result?.usable ? "Sim" : "Não"}</div>
          <div>Checks: {JSON.stringify(validationResult.result?.checks || {}, null, 2)}</div>
        </div>
      ) : null}
    </Card>
  )
}
