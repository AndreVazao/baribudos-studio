import { useEffect, useState } from "react"
import { get, post } from "../api.js"

export default function VisualAssetsPanel() {
  const [ipSlug, setIpSlug] = useState("baribudos")
  const [assets, setAssets] = useState([])
  const [file, setFile] = useState(null)
  const [assetType, setAssetType] = useState("ip_logo")
  const [context, setContext] = useState("ip_page")
  const [loading, setLoading] = useState(false)

  async function loadAssets() {
    setLoading(true)
    try {
      const res = await get(`/assets?ip_slug=${ipSlug}&status=published`)
      setAssets(res.items || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => {
    loadAssets()
  }, [])

  async function upload() {
    if (!file) return

    const form = new FormData()
    form.append("file", file)
    form.append("ip_slug", ipSlug)
    form.append("asset_type", assetType)
    form.append("context", context)
    form.append("is_primary", "true")

    try {
      await post("/assets/upload", form, true)
      await loadAssets()
    } catch (e) {
      alert("Erro upload")
    }
  }

  async function publish(id) {
    await post(`/assets/${id}/publish`)
    await loadAssets()
  }

  async function rollback(id) {
    await post(`/assets/${id}/rollback`)
    await loadAssets()
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Visual Asset Registry</h2>

      <div style={{ marginBottom: 20 }}>
        <input
          value={ipSlug}
          onChange={(e) => setIpSlug(e.target.value)}
          placeholder="IP slug"
        />

        <select value={assetType} onChange={(e) => setAssetType(e.target.value)}>
          <option>ip_logo</option>
          <option>cover</option>
          <option>hero_background</option>
          <option>gallery_image</option>
          <option>promo_banner</option>
          <option>character_card</option>
          <option>background_texture</option>
          <option>social_card</option>
        </select>

        <select value={context} onChange={(e) => setContext(e.target.value)}>
          <option>ip_page</option>
          <option>homepage</option>
          <option>product_page</option>
          <option>campaign</option>
          <option>marketing_landing</option>
        </select>

        <input type="file" onChange={(e) => setFile(e.target.files[0])} />

        <button onClick={upload}>Upload</button>
      </div>

      {loading && <div>Loading...</div>}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20 }}>
        {assets.map((a) => (
          <div key={a.asset_id} style={{ border: "1px solid #333", padding: 10 }}>
            <img
              src={a.url}
              style={{ width: "100%", height: 150, objectFit: "cover" }}
            />
            <div>{a.asset_type}</div>
            <div>v{a.version}</div>

            <button onClick={() => publish(a.asset_id)}>Publish</button>
            <button onClick={() => rollback(a.asset_id)}>Rollback</button>
          </div>
        ))}
      </div>
    </div>
  )
    }
