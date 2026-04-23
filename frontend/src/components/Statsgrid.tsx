'use client'

import { SessionState } from '@/app/dashboard/page'
import styles from './Statsgrid.module.css'

interface Props {
  session: SessionState
  onReset: () => void
}

function FormGauge({ pct }: { pct: number }) {
  const r = 40
  const circ = 2 * Math.PI * r
  const dash = (pct / 100) * circ
  const color = pct >= 80 ? 'var(--correct)' : pct >= 50 ? 'var(--warn)' : 'var(--incorrect)'

  return (
    <svg width="100" height="100" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r={r} fill="none" stroke="var(--bg-raised)" strokeWidth="8" />
      <circle
        cx="50" cy="50" r={r} fill="none"
        stroke={color} strokeWidth="8"
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
        transform="rotate(-90 50 50)"
        style={{ transition: 'stroke-dasharray 0.6s ease, stroke 0.3s' }}
      />
      <text x="50" y="55" textAnchor="middle"
        fill={color} fontSize="18" fontFamily="var(--font-display)" letterSpacing="1">
        {Math.round(pct)}%
      </text>
    </svg>
  )
}

export default function StatsGrid({ session, onReset }: Props) {
  const total = session.correctFrames + session.incorrectFrames
  const formPct = total > 0 ? (session.correctFrames / total) * 100 : 0
  const elapsedStr = formatTime(session.elapsed)

  return (
    <section className={styles.grid}>
      {/* Reps */}
      <div className={styles.card}>
        <span className={styles.cardLabel}>Total Reps</span>
        <span className={styles.bigNum} style={{ color: 'var(--accent)' }}>
          {session.reps}
        </span>
        <span className={styles.sub}>{session.exercise.replace('_', ' ')}</span>
      </div>

      {/* Form score gauge */}
      <div className={`${styles.card} ${styles.gaugeCard}`}>
        <span className={styles.cardLabel}>Form Score</span>
        <FormGauge pct={formPct} />
        <span className={styles.sub}>{total} frames analysed</span>
      </div>

      {/* Correct */}
      <div className={styles.card}>
        <span className={styles.cardLabel}>Correct Frames</span>
        <span className={styles.bigNum} style={{ color: 'var(--correct)' }}>
          {session.correctFrames.toLocaleString()}
        </span>
        <BarFill value={session.correctFrames} total={total} color="var(--correct)" />
      </div>

      {/* Incorrect */}
      <div className={styles.card}>
        <span className={styles.cardLabel}>Incorrect Frames</span>
        <span className={styles.bigNum} style={{ color: 'var(--incorrect)' }}>
          {session.incorrectFrames.toLocaleString()}
        </span>
        <BarFill value={session.incorrectFrames} total={total} color="var(--incorrect)" />
      </div>

      {/* Elapsed */}
      <div className={styles.card}>
        <span className={styles.cardLabel}>Session Time</span>
        <span className={styles.bigNum} style={{ fontFamily: 'var(--font-mono)', fontSize: 36 }}>
          {elapsedStr}
        </span>
        <span className={styles.sub}>hh:mm:ss</span>
      </div>

      {/* Avg confidence */}
      <div className={`${styles.card} ${styles.resetCard}`}>
        <span className={styles.cardLabel}>Avg Confidence</span>
        <span className={styles.bigNum} style={{ color: 'var(--warn)' }}>
          {session.log.length > 0
            ? `${(session.log.reduce((s, e) => s + e.confidence, 0) / session.log.length * 100).toFixed(1)}%`
            : '—'}
        </span>
        <button className={styles.resetBtn} onClick={onReset}>↺ Reset Session</button>
      </div>
    </section>
  )
}

function BarFill({ value, total, color }: { value: number; total: number; color: string }) {
  const pct = total > 0 ? (value / total) * 100 : 0
  return (
    <div style={{ width: '100%', height: 6, background: 'var(--bg-raised)', borderRadius: 3, marginTop: 8 }}>
      <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 3, transition: 'width 0.5s ease' }} />
    </div>
  )
}

function formatTime(seconds: number) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  return [h, m, s].map(n => String(n).padStart(2, '0')).join(':')
}