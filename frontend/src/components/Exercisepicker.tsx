'use client'

import { Exercise } from '@/app/dashboard/page'
import styles from './Exercisepicker.module.css'

const EXERCISES: { id: Exercise; label: string; icon: string; joints: string }[] = [
  { id: 'squat',      label: 'Squat',      icon: '🏋️', joints: 'Knee · Hip' },
  { id: 'pushup',     label: 'Push-Up',    icon: '💪', joints: 'Elbow · Shoulder · Hip' },
  { id: 'bicep_curl', label: 'Bicep Curl', icon: '🦾', joints: 'Elbow · Shoulder' },
]

interface Props {
  active: Exercise
  onChange: (e: Exercise) => void
}

export default function ExercisePicker({ active, onChange }: Props) {
  return (
    <section className={styles.section}>
      <h2 className={styles.sectionTitle}>Select Exercise</h2>
      <div className={styles.grid}>
        {EXERCISES.map(ex => (
          <button
            key={ex.id}
            className={`${styles.card} ${active === ex.id ? styles.active : ''}`}
            onClick={() => onChange(ex.id)}
          >
            <span className={styles.icon}>{ex.icon}</span>
            <span className={styles.label}>{ex.label}</span>
            <span className={styles.joints}>{ex.joints}</span>
            {active === ex.id && <span className={styles.activeDot} />}
          </button>
        ))}
      </div>
    </section>
  )
}