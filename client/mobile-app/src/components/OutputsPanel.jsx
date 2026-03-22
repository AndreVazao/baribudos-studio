import { resolveBackendFileUrl } from "../api.js"

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

function FileLink({ label, path }) {
  const url = resolveBackendFileUrl(path)
  if (!path) return null

  return (
    <div style={{ display: "grid", gap: 4 }}>
      <strong>{label}</strong>
      <div style={{ fontSize: 12, wordBreak: "break-all" }}>{path}</div>
      {url ? (
        <a href={url} target="_blank" rel="noreferrer">
          Abrir / descarregar
        </a>
      ) : (
        <span>Link direto indisponível</span>
      )}
    </div>
  )
}

function ImagePreview({ label, path }) {
  const url = resolveBackendFileUrl(path)
  if (!path || !url) return null

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <strong>{label}</strong>
      <img
        src={url}
        alt={label}
        style={{
          maxWidth: "100%",
          borderRadius: 12,
          border: "1px solid #e5e7eb"
        }}
      />
      <a href={url} target="_blank" rel="noreferrer">
        Abrir / descarregar
      </a>
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

            <ImagePreview label="Capa" path={latestCover} />
            <ImagePreview label="Badge etária" path={latestBadge} />

            {Object.entries(epub).map(([lang, data]) => (
              <FileLink
                key={`epub-${project.id}-${lang}`}
                label={`EPUB (${lang})`}
                path={data?.file_path}
              />
            ))}

            {Object.entries(audiobook).map(([lang, data]) => (
              <FileLink
                key={`audio-${project.id}-${lang}`}
                label={`Audiobook (${lang})`}
                path={data?.file_path}
              />
            ))}

            {Object.entries(video).map(([lang, data]) => (
              <FileLink
                key={`video-${project.id}-${lang}`}
                label={`Vídeo (${lang})`}
                path={data?.file_path}
              />
            ))}
          </div>
        )
      })}
    </Card>
  )
  }
