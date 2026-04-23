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
/

├── exercise/ # Backend (FastAPI + ML)

├── frontend/ # Next.js UI

## ▶️ Run Locally

### Backend
cd exercise
pip install -r requirements.txt
uvicorn server:app --reload

### Run Frontend
cd frontend
npm install
npm run dev

🎯 Supported Exercises
Squats
Push-ups
Bicep Curls

📌 Future Improvements
🔊 Voice feedback (AI coach)
🧍 Skeleton overlay visualization
📱 Mobile responsiveness
☁️ Cloud deployment

## 📥 Clone & Setup Project

To get a copy of this project on your local machine, run:
git clone https://github.com/YOUR_USERNAME/exercise-ai.git
cd your folder name


### ScreenShot
<img width="1892" height="902" alt="image" src="https://github.com/user-attachments/assets/13309b18-7c60-4b18-bb92-b64e4e324bf7" />

<img width="1883" height="933" alt="image" src="https://github.com/user-attachments/assets/944b4a01-46b7-406d-97a7-9dc0c6adc0e6" />

