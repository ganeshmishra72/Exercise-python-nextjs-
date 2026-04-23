'use client'

import { SessionState } from '@/app/dashboard/page'
import styles from './FeedbackLog.module.css'

interface Props { session: SessionState }

const FEEDBACK_RULES: Record<string, Array<{ test: (a: Record<string, number>) => boolean; msg: string }>> = {
  squat: [
    { test: a => (a['left_knee'] ?? 180) < 80 || (a['right_knee'] ?? 180) < 80, msg: 'Knees too bent — don\'t go below parallel' },
    { test: a => (a['left_hip'] ?? 180) < 50 || (a['right_hip'] ?? 180) < 50, msg: 'Lean back slightly — keep torso upright' },
  ],
  pushup: [
    { test: a => !((a['left_hip'] ?? 180) >= 150 && (a['left_hip'] ?? 180) <= 200), msg: 'Keep your body straight — no sagging hips' },
    { test: a => (a['left_elbow'] ?? 180) < 60 || (a['right_elbow'] ?? 180) < 60, msg: 'Elbow angle too sharp — control the descent' },
  ],
  bicep_curl: [
    { test: a => (a['left_shoulder'] ?? 0) > 40 || (a['right_shoulder'] ?? 0) > 40, msg: 'Keep elbows fixed — don\'t swing shoulders' },
    { test: a => (a['left_elbow'] ?? 0) > 170 && (a['right_elbow'] ?? 0) > 170, msg: 'Full extension — squeeze at the bottom' },
  ],
}

export default function FeedbackLog({ session }: Props) {
  const recent = session.log.slice(-50).reverse()
  const rules  = FEEDBACK_RULES[session.exercise] ?? []

  // Count unique feedback occurrences
  const feedbackCounts: Record<string, number> = {}
  session.log.forEach(entry => {
    if (entry.label === 'INCORRECT') {
      rules.forEach(r => {
        if (r.test(entry.angles)) {
          feedbackCounts[r.msg] = (feedbackCounts[r.msg] ?? 0) + 1
        }
      })
    }
  })

  const sortedFeedback = Object.entries(feedbackCounts).sort((a, b) => b[1] - a[1])

  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Feedback &amp; Frame Log</h3>

      {/* Top issues summary */}
      {sortedFeedback.length > 0 && (
        <div className={styles.issues}>
          <p className={styles.issuesHeader}>Most Frequent Issues</p>
          {sortedFeedback.slice(0, 3).map(([msg, count]) => (
            <div key={msg} className={styles.issueRow}>
              <span className={styles.issueWarn}>⚠</span>
              <span className={styles.issueMsg}>{msg}</span>
              <span className={styles.issueCount}>{count}×</span>
            </div>
          ))}
        </div>
      )}

      {/* Frame log */}
      <div className={styles.logWrap}>
        {recent.length === 0 ? (
          <div className={styles.empty}>No frames recorded yet</div>
        ) : (
          recent.map((entry, i) => {
            const msgs = entry.label === 'INCORRECT'
              ? rules.filter(r => r.test(entry.angles)).map(r => r.msg)
              : []
            return (
              <div key={i} className={`${styles.logRow} ${entry.label === 'CORRECT' ? styles.correct : styles.incorrect}`}>
                <span className={styles.logTime}>{entry.time.toFixed(2)}s</span>
                <span className={`${styles.logLabel} ${entry.label === 'CORRECT' ? styles.labelCorrect : styles.labelIncorrect}`}>
                  {entry.label === 'CORRECT' ? '✓' : '✗'} {entry.label}
                </span>
                <span className={styles.logConf}>{(entry.confidence * 100).toFixed(0)}%</span>
                {msgs.length > 0 && (
                  <span className={styles.logNote}>{msgs[0]}</span>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}