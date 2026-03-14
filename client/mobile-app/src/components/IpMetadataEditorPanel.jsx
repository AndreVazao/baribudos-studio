import { useEffect, useState } from "react"
import { getIpMetadata, listIps, updateIpMetadata } from "../api.js"

const LANGUAGE_OPTIONS = ["pt-PT", "pt-BR", "en", "es", "fr", "de", "it", "nl", "zh", "ja"]

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

export default function IpMetadataEditorPanel({ user }) {
  const [ips, setIps] = useState([])
  const [selectedSlug, setSelectedSlug] = useState("")
  const [defaultLanguage, setDefaultLanguage] = useState("pt-PT")
  const [outputLanguages, setOutputLanguages] = useState(["pt-PT"])
  const [metadata, setMetadata] = useState({
    author_default: "",
    producer: "",
    tagline: "",
    mission: "",
    target_age: "",
    series_name: "",
    genre: "",
    description: ""
  })

  useEffect(() => {
    loadIps()
  }, [])

  useEffect(() => {
    if (selectedSlug) {
      loadMetadata(selectedSlug)
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

  async function loadMetadata(slug) {
    try {
      const res = await getIpMetadata(slug, user)
      setMetadata({
        author_default: res?.metadata?.author_default || "",
        producer: res?.metadata?.producer || "",
        tagline: res?.metadata?.tagline || "",
        mission: res?.metadata?.mission || "",
        target_age: res?.metadata?.target_age || "",
        series_name: res?.metadata?.series_name || "",
        genre: res?.metadata?.genre || "",
        description: res?.metadata?.description || ""
      })
      setDefaultLanguage(res?.default_language || "pt-PT")
      setOutputLanguages(res?.output_languages || ["pt-PT"])
    } catch (error) {
      alert(error?.message || "Erro ao carregar metadados.")
    }
  }

  function toggleLanguage(lang) {
    setOutputLanguages((current) => {
      if (current.includes(lang)) {
        const next = current.filter((item) => item !== lang)
        return next.length ? next : [defaultLanguage]
      }
      return [...current, lang]
    })
  }

  async function handleSave() {
    if (!selectedSlug) return

    try {
      const normalizedOutputs = outputLanguages.includes(defaultLanguage)
        ? outputLanguages
        : [defaultLanguage, ...outputLanguages]

      await updateIpMetadata(
        selectedSlug,
        {
          metadata,
          default_language: defaultLanguage,
          output_languages: normalizedOutputs
        },
        user
      )
      alert("Metadados guardados.")
      await loadMetadata(selectedSlug)
    } catch (error) {
      alert(error?.message || "Erro ao guardar metadados.")
    }
  }

  return (
    <Card title="Editor de Metadados por IP">
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

      <label>Autor default</label>
      <input
        value={metadata.author_default}
        onChange={(e) => setMetadata((current) => ({ ...current, author_default: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Producer</label>
      <input
        value={metadata.producer}
        onChange={(e) => setMetadata((current) => ({ ...current, producer: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Tagline</label>
      <input
        value={metadata.tagline}
        onChange={(e) => setMetadata((current) => ({ ...current, tagline: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Missão</label>
      <input
        value={metadata.mission}
        onChange={(e) => setMetadata((current) => ({ ...current, mission: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Target age</label>
      <input
        value={metadata.target_age}
        onChange={(e) => setMetadata((current) => ({ ...current, target_age: e.target.value }))}
        placeholder="Ex.: 4-10"
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Nome da série</label>
      <input
        value={metadata.series_name}
        onChange={(e) => setMetadata((current) => ({ ...current, series_name: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Género</label>
      <input
        value={metadata.genre}
        onChange={(e) => setMetadata((current) => ({ ...current, genre: e.target.value }))}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      />

      <label>Descrição</label>
      <textarea
        value={metadata.description}
        onChange={(e) => setMetadata((current) => ({ ...current, description: e.target.value }))}
        rows={5}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none", resize: "vertical" }}
      />

      <label>Idioma default</label>
      <select
        value={defaultLanguage}
        onChange={(e) => setDefaultLanguage(e.target.value)}
        style={{ padding: 12, borderRadius: 12, border: "1px solid #d1d5db", outline: "none" }}
      >
        {LANGUAGE_OPTIONS.map((lang) => (
          <option key={lang} value={lang}>
            {lang}
          </option>
        ))}
      </select>

      <div style={{ display: "grid", gap: 8 }}>
        <strong>Idiomas de exportação</strong>
        {LANGUAGE_OPTIONS.map((lang) => (
          <label key={lang} style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={outputLanguages.includes(lang)}
              onChange={() => toggleLanguage(lang)}
            />
            {lang}
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
        Guardar metadados
      </button>
    </Card>
  )
}
