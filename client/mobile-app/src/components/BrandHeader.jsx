export default function BrandHeader() {
  return (
    <div
      style={{
        position: "relative",
        zIndex: 2,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 16,
        padding: 16,
        border: "1px solid rgba(255,255,255,0.25)",
        borderRadius: 16,
        background: "rgba(255,255,255,0.82)",
        backdropFilter: "blur(8px)",
        boxShadow: "0 10px 24px rgba(0,0,0,0.10)"
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <img
          src="/brand/baribudos-studio-logo.png"
          alt="Baribudos Studio"
          style={{
            height: 56,
            width: "auto",
            objectFit: "contain"
          }}
        />
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", justifyContent: "flex-end" }}>
        <img
          src="/brand/os-baribudos-logo.png"
          alt="Os Baribudos"
          style={{
            height: 48,
            width: "auto",
            objectFit: "contain"
          }}
        />
        <img
          src="/brand/historia-que-protege-selo.png"
          alt="História que Protege"
          style={{
            height: 48,
            width: "auto",
            objectFit: "contain"
          }}
        />
      </div>
    </div>
  )
  }
