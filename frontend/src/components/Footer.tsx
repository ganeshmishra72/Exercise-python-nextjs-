export default function Footer() {
  return (
    <footer style={{
      marginTop: 60,
      padding: 30,
      textAlign: 'center',
      borderTop: '1px solid rgba(255,255,255,0.1)'
    }}>
      <h3 style={{ marginBottom: 10 }}>⚡ RepSense</h3>

      <p style={{ opacity: 0.6 }}>
        AI-powered exercise posture detection system
      </p>

      <div style={{
        marginTop: 15,
        display: 'flex',
        justifyContent: 'center',
        gap: 20
      }}>
        <a href="#" style={link}>GitHub</a>
        <a href="#" style={link}>LinkedIn</a>
        <a href="#" style={link}>Contact</a>
      </div>

      <p style={{ marginTop: 15, fontSize: 12, opacity: 0.5 }}>
        © 2026 Ganesh Mishra · PCCO308 Project
      </p>
    </footer>
  )
}

const link = {
  color: '#6c63ff',
  textDecoration: 'none'
}