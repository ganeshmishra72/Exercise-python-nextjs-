export default function Features() {
  const items = [
    { icon: '🎯', title: 'Real-Time Detection', desc: 'Instant posture tracking using AI' },
    { icon: '📊', title: 'Live Analytics', desc: 'Track reps, accuracy & performance' },
    { icon: '⚡', title: 'Instant Feedback', desc: 'Fix mistakes immediately' },
    { icon: '🧠', title: 'ML Powered', desc: 'Trained models for accurate results' },
  ]

  return (
    <section style={{ padding: '60px 20px' }}>
      <h2 style={{ textAlign: 'center', fontSize: 32, marginBottom: 40 }}>
        Features
      </h2>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px,1fr))',
        gap: 20,
        maxWidth: 1000,
        margin: '0 auto'
      }}>
        {items.map((f, i) => (
          <div key={i} style={card}>
            <div style={{ fontSize: 30 }}>{f.icon}</div>
            <h3>{f.title}</h3>
            <p style={{ opacity: 0.7 }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

const card = {
  padding: 20,
  borderRadius: 12,
  background: 'rgba(255,255,255,0.05)',
  border: '1px solid rgba(255,255,255,0.1)'
}