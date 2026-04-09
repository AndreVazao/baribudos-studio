import { useEffect, useMemo, useState } from "react"
import { getProjectCommercial, getWebsitePublishStatus, listProjects, publishProjectToWebsite, revalidateProjectOnWebsite, unpublishProjectOnWebsite, updateProjectCommercial } from "../api.js"

const STATES = ["private","internal_review","teaser_ready","prelaunch_public","launch_ready","published","archived"]
const EMPTY = { public_state:"private", teaser_badge:"Em breve", teaser_headline:"", teaser_subtitle:"", teaser_cta_label:"Ver novidades", teaser_release_label:"", teaser_gallery:[], teaser_cover_url:"", teaser_trailer_url:"", teaser_excerpt:"", teaser_visibility_notes:"", prelaunch_enabled:false, share_preview_images_during_production:true }

function Button({ children, onClick, disabled=false, tone="primary" }) {
  const style = tone === "secondary"
    ? { background:"#fff", color:"#111827", border:"1px solid #cbd5e1" }
    : tone === "danger"
      ? { background:"#991b1b", color:"#fff", border:"none" }
      : { background:"#2F5E2E", color:"#fff", border:"none" }
  return <button onClick={onClick} disabled={disabled} style={{ padding:"10px 12px", borderRadius:12, ...style, fontWeight:700, cursor:disabled?"not-allowed":"pointer", opacity:disabled?0.6:1 }}>{children}</button>
}

function Card({ title, children, extra=null }) {
  return <div style={{ border:"1px solid rgba(255,255,255,0.25)", borderRadius:16, background:"rgba(255,255,255,0.84)", backdropFilter:"blur(8px)", padding:16, display:"grid", gap:12, boxShadow:"0 10px 24px rgba(0,0,0,0.10)" }}><div style={{ display:"flex", justifyContent:"space-between", gap:12, alignItems:"center", flexWrap:"wrap" }}><h3 style={{ margin:0, color:"#2F5E2E" }}>{title}</h3>{extra}</div>{children}</div>
}

const parseLines = (v) => String(v || "").split(/\n+/).map((x) => x.trim()).filter(Boolean)
const toText = (v) => Array.isArray(v) ? v.join("\n") : ""
const img = (v) => /\.(png|jpg|jpeg|webp|gif|bmp|svg)$/i.test(String(v || ""))
const vid = (v) => /\.(mp4|webm|mov|m4v)$/i.test(String(v || ""))

function collect(project) {
  const set = new Set()
  const walk = (node) => {
    if (!node) return
    if (typeof node === "string") { if (img(node) || vid(node)) set.add(node); return }
    if (Array.isArray(node)) return node.forEach(walk)
    if (typeof node === "object") Object.values(node).forEach(walk)
  }
  walk(project?.cover_image)
  walk(project?.illustration_path)
  walk(project?.outputs)
  return Array.from(set)
}

export default function WebsiteMarketingControlPanel({ user }) {
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [commercial, setCommercial] = useState({})
  const [marketing, setMarketing] = useState(EMPTY)
  const [publishStatus, setPublishStatus] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => { loadProjects() }, [])
  useEffect(() => { if (selectedProjectId) refreshProject(selectedProjectId) }, [selectedProjectId])

  const selectedProject = useMemo(() => projects.find((x) => x.id === selectedProjectId) || null, [projects, selectedProjectId])
  const assets = useMemo(() => collect(selectedProject), [selectedProject])
  const websiteSync = publishStatus?.website_sync || selectedProject?.website_sync || null
  const imageAssets = useMemo(() => assets.filter(img), [assets])
  const videoAssets = useMemo(() => assets.filter(vid), [assets])

  async function loadProjects() {
    const res = await listProjects(user)
    const list = res?.projects || []
    setProjects(list)
    if (!selectedProjectId && list.length) setSelectedProjectId(list[0].id)
  }

  async function refreshProject(projectId) {
    setBusy(true)
    try {
      const [commercialRes, statusRes] = await Promise.all([
        getProjectCommercial(projectId).catch(() => ({ commercial:{} })),
        getWebsitePublishStatus(projectId).catch(() => null),
      ])
      const nextCommercial = commercialRes?.commercial || {}
      setCommercial(nextCommercial)
      setMarketing({ ...EMPTY, ...(nextCommercial?.website_marketing || nextCommercial?.marketing || {}) })
      setPublishStatus(statusRes || null)
    } finally { setBusy(false) }
  }

  const setPatch = (patch) => setMarketing((c) => ({ ...c, ...patch }))
  const useCover = (v) => setPatch({ teaser_cover_url:v })
  const useTrailer = (v) => setPatch({ teaser_trailer_url:v })
  const addGallery = (v) => setPatch({ teaser_gallery:Array.from(new Set([...(marketing.teaser_gallery || []), v])) })

  function autofill() {
    setPatch({
      teaser_cover_url: marketing.teaser_cover_url || imageAssets[0] || selectedProject?.cover_image || selectedProject?.illustration_path || "",
      teaser_gallery: marketing.teaser_gallery?.length ? marketing.teaser_gallery : imageAssets.slice(0, 6),
      teaser_trailer_url: marketing.teaser_trailer_url || videoAssets[0] || "",
      teaser_headline: marketing.teaser_headline || selectedProject?.title || "",
      teaser_subtitle: marketing.teaser_subtitle || selectedProject?.summary || selectedProject?.description || `Uma nova criação do universo ${selectedProject?.saga_name || "Baribudos"} está a ganhar forma.`,
      teaser_excerpt: marketing.teaser_excerpt || selectedProject?.story || selectedProject?.summary || "",
    })
  }

  function applyPreset(mode) {
    const baseTitle = selectedProject?.title || "Nova criação"
    const sagaName = selectedProject?.saga_name || "Baribudos"
    const cover = marketing.teaser_cover_url || imageAssets[0] || selectedProject?.cover_image || selectedProject?.illustration_path || ""
    const gallery = marketing.teaser_gallery?.length ? marketing.teaser_gallery : imageAssets.slice(0, mode === "quick" ? 3 : 6)
    const trailer = marketing.teaser_trailer_url || videoAssets[0] || ""

    if (mode === "quick") {
      setPatch({
        public_state: "teaser_ready",
        prelaunch_enabled: false,
        teaser_badge: "Em breve",
        teaser_headline: marketing.teaser_headline || baseTitle,
        teaser_subtitle: marketing.teaser_subtitle || `Primeiro olhar sobre uma nova peça do universo ${sagaName}.`,
        teaser_cta_label: "Ver teaser",
        teaser_release_label: marketing.teaser_release_label || "Primeiras imagens",
        teaser_cover_url: cover,
        teaser_gallery: gallery,
      })
      return
    }

    if (mode === "prelaunch") {
      setPatch({
        public_state: "prelaunch_public",
        prelaunch_enabled: true,
        teaser_badge: "Pré-lançamento",
        teaser_headline: marketing.teaser_headline || baseTitle,
        teaser_subtitle: marketing.teaser_subtitle || `Página pública pronta para aquecer o lançamento de ${baseTitle}.`,
        teaser_cta_label: "Acompanhar lançamento",
        teaser_release_label: marketing.teaser_release_label || "Lançamento em breve",
        teaser_cover_url: cover,
        teaser_gallery: gallery,
        teaser_trailer_url: trailer,
      })
      return
    }

    setPatch({
      public_state: "published",
      prelaunch_enabled: false,
      teaser_badge: "Já disponível",
      teaser_headline: marketing.teaser_headline || baseTitle,
      teaser_subtitle: marketing.teaser_subtitle || `${baseTitle} já está pronto para descoberta e compra no Website.`,
      teaser_cta_label: "Comprar agora",
      teaser_release_label: marketing.teaser_release_label || "Disponível agora",
      teaser_cover_url: cover,
      teaser_gallery: gallery,
      teaser_trailer_url: trailer,
    })
  }

  async function save(nextMarketing, msg) {
    if (!selectedProjectId) return
    setBusy(true)
    try {
      await updateProjectCommercial(selectedProjectId, { ...commercial, website_marketing:{ ...nextMarketing, teaser_gallery:Array.isArray(nextMarketing.teaser_gallery) ? nextMarketing.teaser_gallery : parseLines(nextMarketing.teaser_gallery) } }, user)
      await refreshProject(selectedProjectId)
      if (msg) alert(msg)
    } catch (e) { alert(e?.message || "Erro ao guardar controlo de marketing.") } finally { setBusy(false) }
  }

  async function publishTeaser() {
    if (!selectedProjectId) return
    setBusy(true)
    try {
      await updateProjectCommercial(selectedProjectId, { ...commercial, website_marketing:{ ...marketing, public_state:"prelaunch_public", prelaunch_enabled:true } }, user)
      await publishProjectToWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Pré-lançamento empurrado para o Website.")
    } catch (e) { alert(e?.message || "Erro ao publicar pré-lançamento no Website.") } finally { setBusy(false) }
  }

  async function promoteLaunch() {
    if (!selectedProjectId) return
    setBusy(true)
    try {
      await updateProjectCommercial(selectedProjectId, { ...commercial, website_marketing:{ ...marketing, public_state:"published", prelaunch_enabled:false } }, user)
      await publishProjectToWebsite(selectedProjectId)
      await revalidateProjectOnWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Projeto promovido para lançamento final no Website.")
    } catch (e) { alert(e?.message || "Erro ao promover lançamento no Website.") } finally { setBusy(false) }
  }

  async function withdraw() {
    if (!selectedProjectId) return
    setBusy(true)
    try {
      await updateProjectCommercial(selectedProjectId, { ...commercial, website_marketing:{ ...marketing, public_state:"private", prelaunch_enabled:false } }, user)
      await unpublishProjectOnWebsite(selectedProjectId)
      await refreshProject(selectedProjectId)
      alert("Superfície pública retirada do Website.")
    } catch (e) { alert(e?.message || "Erro ao retirar superfície pública.") } finally { setBusy(false) }
  }

  return <Card title="Website Marketing Control" extra={<Button onClick={() => refreshProject(selectedProjectId)} disabled={busy || !selectedProjectId} tone="secondary">{busy ? "A atualizar..." : "Atualizar"}</Button>}>
    <div style={{ padding:12, borderRadius:12, border:"1px solid #e5e7eb", background:"rgba(248,250,252,0.9)", color:"#334155" }}>O Studio decide o que fica privado, teaser, pré-lançamento ou lançamento final. O Website só expõe a superfície pública escolhida aqui.</div>
    <label>Projeto</label>
    <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }}>
      <option value="">Selecionar projeto</option>
      {projects.map((project) => <option key={project.id} value={project.id}>{project.title} — {project.saga_name}</option>)}
    </select>
    {selectedProject ? <div style={{ padding:12, borderRadius:12, border:"1px solid #e5e7eb", background:"rgba(255,255,255,0.55)", display:"grid", gap:6 }}><div><strong>{selectedProject.title}</strong></div><div>IP: {selectedProject.saga_name} ({selectedProject.saga_slug})</div><div>Ready for publish: {selectedProject.ready_for_publish ? "Sim" : "Não"}</div><div>Estado público atual: {marketing.public_state}</div><div>Assets detetados: {assets.length}</div></div> : null}
    <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
      <Button onClick={autofill} disabled={busy || !selectedProjectId}>Preencher da produção</Button>
      <Button onClick={() => applyPreset("quick")} disabled={busy || !selectedProjectId} tone="secondary">Preset teaser rápido</Button>
      <Button onClick={() => applyPreset("prelaunch")} disabled={busy || !selectedProjectId} tone="secondary">Preset pré-lançamento</Button>
      <Button onClick={() => applyPreset("launch")} disabled={busy || !selectedProjectId} tone="secondary">Preset lançamento</Button>
    </div>
    <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
      <Button onClick={() => save(marketing, "Controlo de marketing do Website guardado.")} disabled={busy || !selectedProjectId}>Guardar controlo marketing</Button>
      <Button onClick={publishTeaser} disabled={busy || !selectedProjectId}>Publicar pré-lançamento</Button>
      <Button onClick={promoteLaunch} disabled={busy || !selectedProjectId}>Promover para lançamento</Button>
      <Button onClick={withdraw} disabled={busy || !selectedProjectId} tone="danger">Retirar do Website</Button>
    </div>
    <label>Estado público</label>
    <select value={marketing.public_state} onChange={(e) => setPatch({ public_state:e.target.value })} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }}>
      {STATES.map((value) => <option key={value} value={value}>{value}</option>)}
    </select>
    <label><input type="checkbox" checked={!!marketing.prelaunch_enabled} onChange={(e) => setPatch({ prelaunch_enabled:e.target.checked })} /> Pré-lançamento público ativo</label>
    <label><input type="checkbox" checked={marketing.share_preview_images_during_production !== false} onChange={(e) => setPatch({ share_preview_images_during_production:e.target.checked })} /> Permitir partilhar imagens teaser durante produção</label>
    {assets.length ? <div style={{ padding:12, borderRadius:12, border:"1px solid #dbe4d8", background:"rgba(240,253,244,0.85)", display:"grid", gap:8 }}><strong>Assets sugeridos do projeto</strong><div style={{ display:"grid", gap:8 }}>{assets.slice(0,10).map((item) => <div key={item} style={{ padding:10, borderRadius:10, border:"1px solid #d1d5db", background:"#fff", display:"grid", gap:8 }}><div style={{ display:"grid", gap:8, gridTemplateColumns: img(item) ? "92px 1fr" : "1fr" }}><div>{img(item) ? <img src={item} alt="asset preview" style={{ width:92, height:92, objectFit:"cover", borderRadius:10, border:"1px solid #e5e7eb" }} /> : vid(item) ? <div style={{ width:92, height:92, display:"grid", placeItems:"center", borderRadius:10, border:"1px solid #e5e7eb", background:"#111827", color:"#fff", fontWeight:700 }}>Vídeo</div> : null}</div><div style={{ wordBreak:"break-all" }}>{item}</div></div><div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>{img(item) ? <Button onClick={() => useCover(item)} tone="secondary">Usar como cover</Button> : null}{img(item) ? <Button onClick={() => addGallery(item)} tone="secondary">Adicionar galeria</Button> : null}{vid(item) ? <Button onClick={() => useTrailer(item)} tone="secondary">Usar como trailer</Button> : null}</div></div>)}</div></div> : null}
    <label>Badge teaser</label><input value={marketing.teaser_badge || ""} onChange={(e) => setPatch({ teaser_badge:e.target.value })} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }} />
    <label>Headline teaser</label><input value={marketing.teaser_headline || ""} onChange={(e) => setPatch({ teaser_headline:e.target.value })} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }} />
    <label>Subheadline teaser</label><textarea value={marketing.teaser_subtitle || ""} onChange={(e) => setPatch({ teaser_subtitle:e.target.value })} rows={3} style={{ width:"100%", padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none", resize:"vertical" }} />
    <label>CTA teaser</label><input value={marketing.teaser_cta_label || ""} onChange={(e) => setPatch({ teaser_cta_label:e.target.value })} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }} />
    <label>Texto de lançamento</label><input value={marketing.teaser_release_label || ""} onChange={(e) => setPatch({ teaser_release_label:e.target.value })} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }} />
    <label>Imagem teaser principal</label><input value={marketing.teaser_cover_url || ""} onChange={(e) => setPatch({ teaser_cover_url:e.target.value })} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }} />
    <label>Trailer teaser</label><input value={marketing.teaser_trailer_url || ""} onChange={(e) => setPatch({ teaser_trailer_url:e.target.value })} style={{ padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none" }} />
    <label>Galeria teaser</label><textarea value={toText(marketing.teaser_gallery)} onChange={(e) => setPatch({ teaser_gallery:parseLines(e.target.value) })} rows={4} style={{ width:"100%", padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none", resize:"vertical" }} />
    <label>Excerto público</label><textarea value={marketing.teaser_excerpt || ""} onChange={(e) => setPatch({ teaser_excerpt:e.target.value })} rows={4} style={{ width:"100%", padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none", resize:"vertical" }} />
    <label>Notas de visibilidade</label><textarea value={marketing.teaser_visibility_notes || ""} onChange={(e) => setPatch({ teaser_visibility_notes:e.target.value })} rows={3} style={{ width:"100%", padding:12, borderRadius:12, border:"1px solid #d1d5db", outline:"none", resize:"vertical" }} />
    <div style={{ padding:12, borderRadius:12, border:"1px solid #e5e7eb", background:"rgba(255,255,255,0.55)", display:"grid", gap:8 }}><div><strong>Preview rápido do teaser</strong></div><div style={{ display:"grid", gap:8, padding:12, borderRadius:12, background:"#fff", border:"1px solid #e5e7eb" }}><div style={{ display:"inline-flex", width:"fit-content", padding:"6px 10px", borderRadius:999, background:"rgba(212,167,60,0.18)", color:"#7c5a00", fontWeight:700 }}>{marketing.teaser_badge || "Em breve"}</div><div style={{ fontSize:22, fontWeight:800, color:"#1f2937" }}>{marketing.teaser_headline || selectedProject?.title || "Headline teaser"}</div><div style={{ color:"#475569" }}>{marketing.teaser_subtitle || "Subheadline teaser"}</div><div style={{ display:"flex", gap:8, flexWrap:"wrap", color:"#64748b" }}><span>CTA: {marketing.teaser_cta_label || "-"}</span><span>•</span><span>{marketing.teaser_release_label || "-"}</span></div>{marketing.teaser_cover_url ? <div style={{ wordBreak:"break-all", color:"#64748b" }}>Cover: {marketing.teaser_cover_url}</div> : null}{(marketing.teaser_gallery || []).length ? <div style={{ color:"#64748b" }}>Galeria: {(marketing.teaser_gallery || []).length} imagem(ns)</div> : null}</div></div>
    {websiteSync ? <div style={{ padding:12, borderRadius:12, border:"1px solid #e5e7eb", background:"rgba(255,255,255,0.55)", display:"grid", gap:6 }}><div><strong>Último sync Website</strong></div><div>Publication ID: {websiteSync.publication_id || "-"}</div><div>Checksum: {websiteSync.checksum || "-"}</div><div>Publicado em: {websiteSync.published_at || "-"}</div><div>Último unpublish: {websiteSync.unpublished_at || "-"}</div><div>Última revalidate: {websiteSync.last_revalidate_at || "-"}</div></div> : null}
  </Card>
}
