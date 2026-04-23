'use client'

import Link from 'next/link'

export default function Hero() {
  return (
    <section style={{
      padding: '100px 20px',
      textAlign: 'center',
      background: 'radial-gradient(circle at top, rgba(108,99,255,0.2), transparent)'
    }}>
      <h1 style={{
        fontSize: 56,
        fontWeight: 900,
        marginBottom: 20,
        lineHeight: 1.2
      }}>
        Train Smarter with <br />
        <span style={{ color: '#6c63ff' }}>AI Fitness Coach</span>
      </h1>

      <p style={{
        maxWidth: 700,
        margin: '0 auto',
        fontSize: 18,
        opacity: 0.75,
        marginBottom: 30
      }}>
        Real-time posture detection, rep counting, and instant feedback —
        powered by Computer Vision & Machine Learning.
      </p>

      {/* CTA Buttons */}
      <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
        <Link href="/dashboard">
          <button style={btnPrimary}>🚀 Start Workout</button>
        </Link>

        <button style={btnSecondary}>
          ▶ Watch Demo
        </button>
      </div>

      {/* Banner Card */}
      <div style={{
        marginTop: 60,
        maxWidth: 900,
        marginInline: 'auto',
        padding: 20,
        borderRadius: 16,
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <p style={{ opacity: 0.7 }}>
          🎯 Supports Squats, Pushups, and Bicep Curls with real-time AI feedback
        </p>
      </div>
    </section>
  )
}

const btnPrimary = {
  padding: '14px 28px',
  borderRadius: 10,
  background: '#00e676',
  border: 'none',
  fontWeight: 700,
  cursor: 'pointer'
}

const btnSecondary = {
  padding: '14px 28px',
  borderRadius: 10,
  background: 'transparent',
  border: '1px solid rgba(255,255,255,0.3)',
  color: 'white',
  cursor: 'pointer'
}