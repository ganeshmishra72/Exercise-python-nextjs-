# 🏋️ RepSense – AI Fitness Trainer

RepSense is a real-time AI-powered fitness application that analyzes exercise form using computer vision and machine learning. It tracks body posture, counts repetitions, and provides instant feedback to improve workout performance.

---

## 🚀 Features

- 🎯 Real-time posture detection using MediaPipe
- 🔢 Automatic rep counting (Squats, Push-ups, Bicep Curls)
- 📊 Live performance analytics (Correct vs Incorrect frames)
- 📐 Joint angle tracking and visualization
- ⚡ Instant feedback for form correction
- 📷 Live camera feed integration
- 🔌 WebSocket-based real-time communication

---

## 🧠 Tech Stack

### Frontend
- Next.js (React)
- TypeScript
- WebSockets
- Custom UI components

### Backend
- FastAPI (Python)
- OpenCV
- MediaPipe Pose
- Scikit-learn (ML Model)

---

## ⚙️ How It Works

1. Camera captures live video feed
2. Frames are sent to backend via WebSocket
3. MediaPipe extracts body landmarks
4. ML model classifies posture (Correct / Incorrect)
5. Angles and reps are calculated
6. Data is sent back to frontend in real-time
7. UI updates analytics, logs, and feedback

---

## 📂 Project Structure
