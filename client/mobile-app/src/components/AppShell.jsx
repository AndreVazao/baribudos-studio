export default function AppShell({ children }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        position: "relative",
        overflow: "hidden",
        backgroundColor: "#f3f4f6"
      }}
    >
      <div
        style={{
          position: "fixed",
          inset: 0,
          backgroundImage: 'url("/brand/studio-baribudos-family-background.png")',
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          transform: "scale(1.03)"
        }}
      />

      <div
        style={{
          position: "fixed",
          inset: 0,
          background: "linear-gradient(180deg, rgba(245,238,214,0.55) 0%, rgba(47,94,46,0.20) 100%)"
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          padding: 16,
          display: "grid",
          gap: 16
        }}
      >
        {children}
      </div>
    </div>
  )
}
