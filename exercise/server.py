import cv2
import mediapipe as mp
import numpy as np
import joblib
import time
import os
import asyncio
from collections import deque

from fastapi import FastAPI, WebSocket
from pose_utils import extract_landmarks, flatten_landmarks_to_features, get_angles_for_exercise

app = FastAPI()
mp_pose = mp.solutions.pose

MODEL_DIR = "models"

# Load model
models = {
    "squat": joblib.load(os.path.join(MODEL_DIR, "squat_model.pkl")),
    "pushup": joblib.load(os.path.join(MODEL_DIR, "pushup_model.pkl")),
    "bicep_curl": joblib.load(os.path.join(MODEL_DIR, "bicep_curl_model.pkl")),
}


# ✅ FIXED REP COUNTER
class RepCounter:
    def __init__(self):
        self.count = 0
        self.stage = None
        self.prev_angle = None

    def update(self, angle):
        # Ignore small noise
        if self.prev_angle is not None:
            if abs(angle - self.prev_angle) < 5:
                return self.count

        self.prev_angle = angle

        if angle > 160:
            self.stage = "up"
        elif angle < 100 and self.stage == "up":
            self.stage = "down"
            self.count += 1

        return self.count

import base64
from io import BytesIO
from PIL import Image

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    rep_counter = RepCounter()
    correct_frames = 0
    incorrect_frames = 0

    with mp_pose.Pose() as pose:
        while True:
            data = await ws.receive_json()

            exercise = data.get("exercise", "squat")  # default
            model = models[exercise]

            image_data = data["image"].split(",")[1]
            image_bytes = base64.b64decode(image_data)
            try:
                if "image" not in data:
                    continue

                image_str = data["image"]

                if "," not in image_str:
                    continue

                image_data = image_str.split(",")[1]

                if not image_data:
                    continue

                image_bytes = base64.b64decode(image_data)

                image = Image.open(BytesIO(image_bytes)).convert("RGB")

            except (UnidentifiedImageError, ValueError, OSError) as e:
                print("⚠️ Skipping bad frame:", e)
                continue

            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                landmarks = extract_landmarks(results)

                if landmarks:
                    features = flatten_landmarks_to_features(landmarks).reshape(1, -1)

                    pred = model.predict(features)[0]
                    proba = model.predict_proba(features)[0]

                    label = "CORRECT" if pred == 1 else "INCORRECT"
                    confidence = float(max(proba))

                    angles = get_angles_for_exercise(landmarks, exercise)

                    angle_val = next(iter(angles.values()), 0)
                    reps = rep_counter.update(angle_val)

                    if pred == 1:
                        correct_frames += 1
                    else:
                        incorrect_frames += 1

                    await ws.send_json({
                        "time": time.time(),
                        "label": label,
                        "confidence": confidence,
                        "angles": angles,
                        "reps": reps,
                        "correctFrames": correct_frames,
                        "incorrectFrames": incorrect_frames
                    })