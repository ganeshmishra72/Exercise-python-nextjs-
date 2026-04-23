'use client'

import { useEffect, useState } from 'react'
import Header from '@/components/Header'
import ExercisePicker from '@/components/Exercisepicker'
import StatsGrid from '@/components/Statsgrid'
import SessionPanel from '@/components/Sessionpanel'
import FeedbackLog from '@/components/Feedbacklog'
import CameraFeed from '@/components/CameraFeed'

export type Exercise = 'squat' | 'pushup' | 'bicep_curl'

export interface SessionEntry {
  time: number
  label: 'CORRECT' | 'INCORRECT'
  confidence: number
  angles: Record<string, number>
}

export interface SessionState {
  exercise: Exercise
  reps: number
  correctFrames: number
  incorrectFrames: number
  log: SessionEntry[]
  isActive: boolean
  elapsed: number
}

const DEFAULT_SESSION = (exercise: Exercise): SessionState => ({
  exercise,
  reps: 0,
  correctFrames: 0,
  incorrectFrames: 0,
  log: [],
  isActive: true,
  elapsed: 0,
})

export default function Page() {
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [exercise, setExercise] = useState<Exercise>('squat')
  const [session, setSession] = useState<SessionState>(DEFAULT_SESSION('squat'))

 useEffect(() => {
  const socket = new WebSocket('ws://localhost:8000/ws')
  setWs(socket)

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)

    setSession(prev => ({
      ...prev,
      reps: data.reps,
      correctFrames: data.correctFrames,
      incorrectFrames: data.incorrectFrames,
      elapsed: data.time,
      log: [
        ...prev.log.slice(-80),
        {
          time: data.time,
          label: data.label,
          confidence: data.confidence,
          angles: data.angles
        }
      ]
    }))
  }

  return () => socket.close()
}, [])
  function handleExerciseChange(ex: Exercise) {
    setExercise(ex)
    setSession(DEFAULT_SESSION(ex))
  }

  function handleReset() {
    setSession(DEFAULT_SESSION(exercise))
  }

  return (
    <main style={{ minHeight: '100vh', padding: 20, maxWidth: 1280, margin: '0 auto' }}>
      
      <Header />

      <ExercisePicker active={exercise} onChange={handleExerciseChange} />

      <StatsGrid session={session} onReset={handleReset} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20, marginTop: 20 }}>
         <CameraFeed ws={ws} exercise={exercise}/>
        <SessionPanel session={session} />
        <FeedbackLog session={session} />
      </div>

    </main>
  )
}