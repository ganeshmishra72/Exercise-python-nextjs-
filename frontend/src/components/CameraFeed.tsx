'use client'

import { useEffect, useRef } from 'react'

interface Props {
  ws: WebSocket | null
  exercise: string
}

export default function CameraFeed({ ws, exercise }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Start camera
  useEffect(() => {
    async function startCamera() {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    }

    startCamera()
  }, [])

  // Send frames
  useEffect(() => {
    const interval = setInterval(() => {
      if (!videoRef.current || !canvasRef.current || !ws) return

      const video = videoRef.current
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')

      if (!ctx) return
      if (!video.videoWidth || !video.videoHeight) return  // ✅ fix

      canvas.width = video.videoWidth
      canvas.height = video.videoHeight

      ctx.drawImage(video, 0, 0)

      const imageData = canvas.toDataURL('image/jpeg', 0.6)

      // ✅ avoid sending bad frames
      if (!imageData || imageData.length < 1000) return

      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          image: imageData,
          exercise   // ✅ fix
        }))
      }

    }, 100) // 10 FPS

    return () => clearInterval(interval)
  }, [ws, exercise])

  return (
    <div style={{ position: 'relative' }}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{
          width: '100%',
          borderRadius: 12
        }}
      />

      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  )
}