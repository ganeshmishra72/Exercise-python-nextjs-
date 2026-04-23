export default function HowItWorks() {
  const steps = [
    'Open dashboard',
    'Start camera',
    'Perform exercise',
    'Get AI feedback instantly'
  ]

  return (
    <section style={{ padding: '60px 20px', textAlign: 'center' }}>
      <h2 style={{ fontSize: 32, marginBottom: 40 }}>How It Works</h2>

      <div style={{
        display: 'flex',
        justifyContent: 'center',
        flexWrap: 'wrap',
        gap: 20
      }}>
        {steps.map((s, i) => (
          <div key={i} style={stepCard}>
            <h3>Step {i + 1}</h3>
            <p>{s}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

const stepCard = {
  padding: 20,
  minWidth: 180,
  borderRadius: 10,
  background: 'rgba(255,255,255,0.05)'
}