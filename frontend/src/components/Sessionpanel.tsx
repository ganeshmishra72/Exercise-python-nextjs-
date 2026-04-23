'use client'

import { SessionState } from '@/app/dashboard/page'
import styles from './Sessionpanel.module.css'

interface Props { session: SessionState }

export default function SessionPanel({ session }: Props) {
  const last = session.log.slice(-30)
  const angleKeys = last.length > 0 ? Object.keys(last[0].angles) : []

  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Live Angle Monitor</h3>

      {last.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <AngleChart log={last} angleKeys={angleKeys} />
          <AngleTable log={last} angleKeys={angleKeys} />
        </>
      )}
    </div>
  )
}

function EmptyState() {
  return (
    <div className={styles.empty}>
      <span style={{ fontSize: 40 }}>📐</span>
      <p>No session data yet.<br />Start recording to see angles.</p>
    </div>
  )
}

const COLORS = ['#6c63ff','#00e676','#ff4d6d','#ffb300','#00bcd4']

function AngleChart({ log, angleKeys }: { log: SessionState['log']; angleKeys: string[] }) {
  const W = 500, H = 140, PAD = { top: 10, right: 10, bottom: 30, left: 38 }
  const iW = W - PAD.left - PAD.right
  const iH = H - PAD.top - PAD.bottom

   const allVals = log.flatMap(e =>
  angleKeys.map(k => {
    const v = e.angles?.[k]
    return typeof v === 'number' && !isNaN(v) ? v : 0
  })
)

// Prevent empty / invalid data
const safeMin = allVals.length ? Math.min(...allVals) : 0
const safeMax = allVals.length ? Math.max(...allVals) : 180

const minV = Math.max(0, safeMin - 10)
const maxV = Math.min(200, safeMax + 10)

// Prevent division by zero
const range = maxV - minV || 1

  const xScale = (i: number) => (i / (log.length - 1)) * iW
const yScale = (v: number) => {
  if (isNaN(v)) return iH
  return iH - ((v - minV) / range) * iH
}

  return (
    <div className={styles.chartWrap}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto' }}>
        <g transform={`translate(${PAD.left},${PAD.top})`}>
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map(t => {
            const y = t * iH
            const val = Math.round(maxV - t * (maxV - minV))
            return (
              <g key={t}>
                <line x1={0} y1={y} x2={iW} y2={y} stroke="rgba(255,255,255,0.05)" strokeWidth={1} />
                <text x={-6} y={y + 4} fill="rgba(255,255,255,0.3)" fontSize={9} textAnchor="end">{val}°</text>
              </g>
            )
          })}

          {/* Correct/Incorrect background bands */}
          {log.map((e, i) => {
            if (i === log.length - 1) return null
            const x1 = xScale(i), x2 = xScale(i + 1)
            return (
              <rect key={i} x={x1} y={0} width={x2 - x1} height={iH}
                fill={e.label === 'CORRECT' ? 'rgba(0,230,118,0.04)' : 'rgba(255,77,109,0.04)'} />
            )
          })}

          {/* Lines per joint */}
          {angleKeys.slice(0, 5).map((key, ki) => {
            const pts = log.map((e, i) => {
  const val = e.angles?.[key]
  const safeVal = typeof val === 'number' && !isNaN(val) ? val : 0

  return `${xScale(i)},${yScale(safeVal)}`
})
            return (
              <polyline key={key} points={pts.join(' ')}
                fill="none" stroke={COLORS[ki % COLORS.length]}
                strokeWidth={1.5} strokeOpacity={0.85} strokeLinecap="round" strokeLinejoin="round" />
            )
          })}

          {/* X axis */}
          <line x1={0} y1={iH} x2={iW} y2={iH} stroke="rgba(255,255,255,0.1)" strokeWidth={1} />
          <text x={iW / 2} y={iH + 20} fill="rgba(255,255,255,0.3)" fontSize={9} textAnchor="middle">Last 30 frames</text>
        </g>
      </svg>

      {/* Legend */}
      <div className={styles.legend}>
        {angleKeys.slice(0, 5).map((key, ki) => (
          <span key={key} className={styles.legendItem}>
            <span className={styles.legendDot} style={{ background: COLORS[ki % COLORS.length] }} />
            {key.replace('_', ' ')}
          </span>
        ))}
      </div>
    </div>
  )
}

function AngleTable({ log, angleKeys }: { log: SessionState['log']; angleKeys: string[] }) {
  const latest = log[log.length - 1]
  if (!latest) return null

  return (
    <div className={styles.table}>
      {angleKeys.map(key => {
        const val = typeof latest.angles[key] === 'number' && !isNaN(latest.angles[key])
  ? latest.angles[key]
  : 0
        const barPct = Math.min(100, (val / 180) * 100)
        return (
          <div key={key} className={styles.row}>
            <span className={styles.rowKey}>{key.replace('_', ' ')}</span>
            <div className={styles.rowBar}>
              <div className={styles.rowFill} style={{ width: `${barPct}%` }} />
            </div>
            <span className={styles.rowVal}>{val.toFixed(1)}°</span>
          </div>
        )
      })}
    </div>
  )
}