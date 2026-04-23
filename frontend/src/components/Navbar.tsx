'use client'

import Link from 'next/link'

export default function Navbar() {
  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '16px 24px',
      borderBottom: '1px solid rgba(255,255,255,0.1)'
    }}>
      {/* Logo */}
      <div style={{ fontSize: 22, fontWeight: 700 }}>
        ⚡ RepSense
      </div>

      {/* Button */}
      <Link href="/dashboard">
        <button style={{
          padding: '10px 18px',
          borderRadius: 8,
          background: '#6c63ff',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          fontWeight: 600
        }}>
          Go to Dashboard →
        </button>
      </Link>
    </nav>
  )
}