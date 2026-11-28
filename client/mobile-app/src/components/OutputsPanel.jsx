import { useEffect, useState } from "react"
import { fetchProjectMediaBlob } from "../api.js"

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

function openBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement("a")
  anchor.href = url
  anchor.download = filename || "baribudos-output"
  anchor.rel = "noopener"
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 30000)
}

function FileLink({ label, path, projectId }) {
  const [busy, setBusy] = useState(false)
  if (!path) return null

  async function handleOpen() {
    if (/^https?:\/\//i.test(String(path))) {
      window.open(path, "_blank", "noopener,noreferrer")
      return
    }
    setBusy(true)
    try {
      const blob = await fetchProjectMediaBlob(projectId, path)
      const filename = String(path).replace(/\\/g, "/").split("/").pop()
      openBlob(blob, filename)
    } catch (error) {
      alert(error?.message || "Não foi possível descarregar o ficheiro.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ display: "grid", gap: 4 }}>
      <strong>{label}</strong>
      <div style={{ fontSize: 12 }}>{String(path).replace(/\\/g, "/").split("/").pop()}</div>
      <button type="button" onClick={handleOpen} disabled={busy}>
        {busy ? "A obter ficheiro..." : "Abrir / descarregar"}
      </button>
    </div>
  )
}

function ImagePreview({ label, path, projectId }) {
  const [src, setSrc] = useState("")

  useEffect(() => {
    let active = true
    let objectUrl = ""

    async function load() {
      if (!path) return
      try {
        if (/^https?:\/\//i.test(String(path))) {
          if (active) setSrc(path)
          return
        }
        const blob = await fetchProjectMediaBlob(projectId, path)
        objectUrl = URL.createObjectURL(blob)
        if (active) setSrc(objectUrl)
        else URL.revokeObjectURL(objectUrl)
      } catch {
        if (active) setSrc("")
      }
    }

    setSrc("")
    load()
    return () => {
      active = false
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [projectId, path])

  if (!path) return null

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <strong>{label}</strong>
      {src ? (
        <img
          src={src}
          alt={label}
          style={{
            maxWidth: "100%",
            borderRadius: 12,
            border: "1px solid #e5e7eb"
          }}
        />
      ) : (
        <span>Preview indisponível ou sem autorização.</span>
      )}
    </div>
  )
}

export default function OutputsPanel({ projects }) {
  return (
    <Card title="Preview e Downloads dos Outputs">
      {!projects?.length ? <div>Sem projetos disponíveis.</div> : null}

      {projects?.map((project) => {
        const outputs = project?.outputs || {}
        const epub = outputs?.epub || {}
        const audiobook = outputs?.audiobook || {}
        const video = outputs?.video || {}
        const covers = project?.outputs?.covers || {}
        const latestCover = covers?.file_path || project?.cover_image || ""
        const latestBadge = covers?.badge_file_path || ""

        return (
          <div
            key={project.id}
            style={{
              display: "grid",
              gap: 12,
              padding: 12,
              border: "1px solid #e5e7eb",
              borderRadius: 12,
              background: "rgba(255,255,255,0.55)"
            }}
          >
            <div>
              <strong>{project.title}</strong>
              <div>Saga: {project.saga_name}</div>
              <div>Língua base: {project.language}</div>
            </div>

            <ImagePreview label="Capa" path={latestCover} projectId={project.id} />
            <ImagePreview label="Badge etária" path={latestBadge} projectId={project.id} />

            {Object.entries(epub).map(([lang, data]) => (
              <FileLink
                key={`epub-${project.id}-${lang}`}
                label={`EPUB (${lang})`}
                path={data?.file_path}
                projectId={project.id}
              />
            ))}

            {Object.entries(audiobook).map(([lang, data]) => (
              <FileLink
                key={`audio-${project.id}-${lang}`}
                label={`Audiobook (${lang})`}
                path={data?.file_path}
                projectId={project.id}
              />
            ))}

            {Object.entries(video).map(([lang, data]) => (
              <FileLink
                key={`video-${project.id}-${lang}`}
                label={`Vídeo (${lang})`}
                path={data?.file_path}
                projectId={project.id}
              />
            ))}
          </div>
        )
      })}
    </Card>
  )
}
