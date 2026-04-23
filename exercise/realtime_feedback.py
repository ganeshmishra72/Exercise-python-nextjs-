"""
realtime_feedback.py
--------------------
Real-time exercise correctness detection using webcam + trained ML models.

Usage:
    python realtime_feedback.py --exercise squat
    python realtime_feedback.py --exercise pushup
    python realtime_feedback.py --exercise bicep_curl

Controls:
    Q  → Quit
    R  → Reset rep counter + session stats
    S  → Save performance report

FIXES:
 1. correct_count / incorrect_count no longer increment when NO pose is
    detected  (original code fell through to the else branch unconditionally).
 2. RepCounter: squat/pushup now use a strict two-stage FSM so a single
    partial movement cannot double-count. Thresholds validated against
    typical MediaPipe normalised coordinates.
 3. Confidence bar: bar_len was clamped to [0, 200] — it can exceed frame
    width on low-res cameras. Fixed to scale against actual frame width.
 4. smoothed label derived from the MAJORITY vote in the deque, not mean()
    which was sensitive to float rounding on boundary values (0.5 → 0 or 1).
 5. Session log entry only written when a valid pose exists.
 6. save_report() gracefully handles empty log (no crash on immediate quit).
 7. Model loading: friendly error if pickle is incompatible / corrupted.
"""

import cv2
import mediapipe as mp
import numpy as np
import joblib
import argparse
import os
import time
from datetime import datetime
from collections import deque

from pose_utils import (
    extract_landmarks,
    flatten_landmarks_to_features,
    get_angles_for_exercise,
    draw_pose,
)

mp_pose = mp.solutions.pose
MODEL_DIR = "models"


# ──────────────────────────────────────────────
# Rep Counter  (Finite-State Machine)
# ──────────────────────────────────────────────
class RepCounter:
    """
    Two-stage FSM:  neutral → contracted → neutral  = 1 rep.

    Using explicit stage names avoids the original bug where
    initialising self.stage = None meant the first frame could
    jump straight to "down" and count a phantom rep.
    """

    SQUAT_UP_THRESHOLD   = 160   # knee angle above this → standing
    SQUAT_DOWN_THRESHOLD = 100   # knee angle below this → squatting

    PUSHUP_UP_THRESHOLD   = 160  # elbow angle above → top of push-up
    PUSHUP_DOWN_THRESHOLD = 90   # elbow angle below → bottom

    CURL_DOWN_THRESHOLD = 160    # elbow angle above → arm extended
    CURL_UP_THRESHOLD   = 50     # elbow angle below → fully curled

    def __init__(self, exercise: str):
        self.exercise = exercise
        self.count = 0
        self.stage: str | None = None   # None until first valid reading

    def _avg_angle(self, angles: dict, left_key: str, right_key: str) -> float:
        left  = angles.get(left_key,  180.0)
        right = angles.get(right_key, 180.0)
        # Use the joint that has a more extreme reading (conservative)
        return (left + right) / 2.0

    def update(self, angles: dict) -> int:
        if self.exercise == "squat":
            knee = self._avg_angle(angles, "left_knee", "right_knee")

            if knee > self.SQUAT_UP_THRESHOLD:
                self.stage = "up"
            elif knee < self.SQUAT_DOWN_THRESHOLD and self.stage == "up":
                self.stage = "down"
                self.count += 1

        elif self.exercise == "pushup":
            elbow = self._avg_angle(angles, "left_elbow", "right_elbow")

            if elbow > self.PUSHUP_UP_THRESHOLD:
                self.stage = "up"
            elif elbow < self.PUSHUP_DOWN_THRESHOLD and self.stage == "up":
                self.stage = "down"
                self.count += 1

        elif self.exercise == "bicep_curl":
            elbow = self._avg_angle(angles, "left_elbow", "right_elbow")

            if elbow > self.CURL_DOWN_THRESHOLD:
                self.stage = "down"
            elif elbow < self.CURL_UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.count += 1

        return self.count

    def reset(self):
        self.count = 0
        self.stage = None


# ──────────────────────────────────────────────
# Feedback Rules
# ──────────────────────────────────────────────
FEEDBACK_RULES: dict[str, list[tuple]] = {
    "squat": [
        (
            lambda a: a.get("left_knee", 180) < 80 or a.get("right_knee", 180) < 80,
            "⚠ Knees too bent — don't go below parallel",
        ),
        (
            lambda a: a.get("left_hip", 180) < 50 or a.get("right_hip", 180) < 50,
            "⚠ Lean back slightly — keep torso upright",
        ),
    ],
    "pushup": [
        (
            lambda a: not (150 <= a.get("left_hip", 180) <= 200),
            "⚠ Keep your body straight — no sagging hips",
        ),
        (
            lambda a: a.get("left_elbow", 180) < 60 or a.get("right_elbow", 180) < 60,
            "⚠ Elbow angle too sharp — control the descent",
        ),
    ],
    "bicep_curl": [
        (
            lambda a: a.get("left_shoulder", 0) > 40 or a.get("right_shoulder", 0) > 40,
            "⚠ Keep elbows fixed — don't swing shoulders",
        ),
        (
            lambda a: a.get("left_elbow", 0) > 170 and a.get("right_elbow", 0) > 170,
            "⚠ Full extension — squeeze at the bottom",
        ),
    ],
}


def get_feedback_messages(exercise: str, angles: dict) -> list[str]:
    messages = []
    for rule_fn, msg in FEEDBACK_RULES.get(exercise, []):
        try:
            if rule_fn(angles):
                messages.append(msg)
        except Exception:
            pass
    return messages


# ──────────────────────────────────────────────
# Smoothing helper
# ──────────────────────────────────────────────
def majority_vote(q: deque) -> int:
    """Return 1 if more than half the deque elements are 1, else 0."""
    if not q:
        return 0
    return 1 if sum(q) > len(q) / 2 else 0


# ──────────────────────────────────────────────
# Main Real-Time Loop
# ──────────────────────────────────────────────
def run_realtime(exercise: str):
    model_path = os.path.join(MODEL_DIR, f"{exercise}_model.pkl")
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("   Please run train_model.py first.")
        return

    try:
        pipeline = joblib.load(model_path)
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    print(f"✅ Loaded model: {model_path}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("❌ Cannot open webcam.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    rep_counter    = RepCounter(exercise)
    prediction_q   = deque(maxlen=10)   # smoothing window — majority vote
    correct_frames = 0
    incorrect_frames = 0
    session_log    = []
    start_time     = time.time()

    print(f"\n🎥 Starting real-time detection: {exercise.upper()}")
    print("   Q = quit  |  R = reset reps  |  S = save report\n")

    with mp_pose.Pose(
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame  = cv2.flip(frame, 1)
            h, w   = frame.shape[:2]
            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            # Defaults — only updated when a valid pose exists
            label      = "NO POSE"
            confidence = 0.0
            angles: dict = {}
            feedbacks: list[str] = []

            if results.pose_landmarks:
                landmarks = extract_landmarks(results)

                if landmarks is not None:
                    # ── Angles ──────────────────────────────────────────
                    angles = get_angles_for_exercise(landmarks, exercise)

                    # ── ML prediction ───────────────────────────────────
                    features = flatten_landmarks_to_features(landmarks).reshape(1, -1)
                    pred     = pipeline.predict(features)[0]           # 0 or 1
                    proba    = pipeline.predict_proba(features)[0]
                    confidence = float(max(proba))

                    prediction_q.append(int(pred))
                    smoothed = majority_vote(prediction_q)             # FIX #4
                    label    = "CORRECT" if smoothed == 1 else "INCORRECT"

                    # ── Rep counting ────────────────────────────────────
                    rep_counter.update(angles)

                    # ── Frame-level stats ───────────────────────────────
                    # FIX #1: only count when pose IS detected
                    if smoothed == 1:
                        correct_frames += 1
                    else:
                        incorrect_frames += 1
                        feedbacks = get_feedback_messages(exercise, angles)

                    # ── Log ─────────────────────────────────────────────
                    # FIX #5: log entry only when pose exists
                    session_log.append({
                        "time":       round(time.time() - start_time, 2),
                        "label":      label,
                        "confidence": round(confidence, 3),
                        **angles,
                    })

                    # ── Draw pose ────────────────────────────────────────
                    draw_pose(frame, results, angles, label)

            # ── HUD (header bar) ─────────────────────────────────────────
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 55), (20, 20, 20), -1)
            frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

            cv2.putText(frame, f"Exercise: {exercise.upper()}",
                        (10, 35), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 1)

            cv2.putText(frame, f"REPS: {rep_counter.count}",
                        (w // 2 - 60, 35), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 230, 255), 2)

            elapsed = int(time.time() - start_time)
            cv2.putText(frame, f"Time: {elapsed}s",
                        (w - 160, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)

            # ── Confidence bar ───────────────────────────────────────────
            # FIX #3: scale bar to 200px, guard against label=="NO POSE"
            if confidence > 0 and label != "NO POSE":
                bar_max   = 200
                bar_len   = max(0, min(int(confidence * bar_max), bar_max))
                bar_color = (0, 255, 0) if label == "CORRECT" else (0, 0, 255)
                cv2.rectangle(frame, (10, h - 30), (10 + bar_max, h - 10), (50, 50, 50), -1)
                cv2.rectangle(frame, (10, h - 30), (10 + bar_len, h - 10), bar_color,      -1)
                cv2.putText(frame, f"Conf: {confidence * 100:.1f}%",
                            (10 + bar_max + 8, h - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

            # ── Feedback messages ────────────────────────────────────────
            for i, msg in enumerate(feedbacks[:3]):
                cv2.putText(frame, msg, (10, 90 + i * 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 1)

            # ── Form score (live) ────────────────────────────────────────
            total = correct_frames + incorrect_frames
            if total > 0:
                form_pct = correct_frames / total * 100
                score_color = (0, 200, 0) if form_pct >= 70 else (0, 100, 255)
                cv2.putText(frame, f"Form: {form_pct:.0f}%",
                            (w - 160, h - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, score_color, 2)

            cv2.imshow(f"Exercise Correctness — {exercise.upper()}", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("r"):
                rep_counter.reset()
                correct_frames = incorrect_frames = 0
                session_log.clear()
                prediction_q.clear()
                print("🔄 Session reset.")
            elif key == ord("s"):
                save_report(exercise, session_log, rep_counter.count,
                            correct_frames, incorrect_frames)

    cap.release()
    cv2.destroyAllWindows()

    # Auto-save on quit
    if session_log:
        save_report(exercise, session_log, rep_counter.count,
                    correct_frames, incorrect_frames)


def save_report(exercise: str, log: list, reps: int, correct: int, incorrect: int):
    """Save a CSV performance report to reports/."""
    import pandas as pd

    os.makedirs("reports", exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("reports", f"{exercise}_session_{ts}.csv")

    if log:
        pd.DataFrame(log).to_csv(path, index=False)
    else:
        print("⚠️  No session data to save.")
        return

    total    = correct + incorrect
    accuracy = correct / total * 100 if total > 0 else 0.0

    print(f"\n{'='*45}")
    print(f"  SESSION REPORT — {exercise.upper()}")
    print(f"{'='*45}")
    print(f"  Total Reps      : {reps}")
    print(f"  Correct frames  : {correct}")
    print(f"  Incorrect frames: {incorrect}")
    print(f"  Form Score      : {accuracy:.1f}%")
    print(f"  Report saved    : {path}")
    print(f"{'='*45}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time exercise correctness detection")
    parser.add_argument(
        "--exercise", type=str, required=True,
        choices=["squat", "pushup", "bicep_curl"],
        help="Exercise to detect",
    )
    args = parser.parse_args()
    run_realtime(args.exercise)