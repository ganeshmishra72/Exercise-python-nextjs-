"""
data_collection.py
------------------
Collect labeled pose data from your webcam.

Usage:
    python data_collection.py --exercise squat --label correct   --samples 200
    python data_collection.py --exercise squat --label incorrect --samples 200
    python data_collection.py --exercise pushup --label correct  --samples 200
    ... (repeat for all exercise/label combinations)

Controls:
    SPACE  → Start / Pause recording
    Q      → Quit and save

FIXES:
 - Feature columns are written in the same sorted order that train_model.py
   expects, eliminating a potential column-order mismatch between collection
   sessions on different Python versions.
 - Added a minimum-visibility filter so frames where MediaPipe is uncertain
   are not recorded (reduces noise in training data).
"""

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import argparse
import os

from pose_utils import (
    extract_landmarks,
    flatten_landmarks_to_features,
    draw_pose,
    LANDMARK_NAMES,
    FEATURES_PER_LANDMARK,
    NUM_FEATURES,
)

mp_pose = mp.solutions.pose

# Minimum mean landmark visibility to accept a frame
MIN_VISIBILITY = 0.5


def _make_column_names() -> list[str]:
    """Return the 52 feature-column names in the same order as flatten_landmarks_to_features."""
    cols = []
    for name in LANDMARK_NAMES:
        cols += [f"{name}_x", f"{name}_y", f"{name}_z", f"{name}_vis"]
    return cols

FEATURE_COLUMNS = _make_column_names()


def collect(exercise: str, label: str, num_samples: int, output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{exercise}_{label}.csv")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("❌ Cannot open webcam. Check camera connection.")

    collected: list[np.ndarray] = []
    recording = False

    print(f"\n{'='*55}")
    print(f"  Exercise : {exercise.upper()}")
    print(f"  Label    : {label.upper()}")
    print(f"  Target   : {num_samples} samples")
    print(f"  Press SPACE to start/pause  |  Q to quit & save")
    print(f"{'='*55}\n")

    with mp_pose.Pose(
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            landmarks = extract_landmarks(results)

            if results.pose_landmarks:
                draw_pose(frame, results)

            # UI overlay
            status_color = (0, 200, 0) if recording else (0, 100, 255)
            status_text  = "● RECORDING" if recording else "❚❚ PAUSED  (SPACE to start)"
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 40), (0, 0, 0), -1)
            cv2.putText(frame, status_text, (10, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            cv2.putText(frame, f"Collected: {len(collected)} / {num_samples}",
                        (frame.shape[1] - 260, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Collect sample only when recording AND pose is confident
            if recording and landmarks is not None:
                # Mean visibility filter
                vis_values = [landmarks[n][3] for n in LANDMARK_NAMES]
                if np.mean(vis_values) >= MIN_VISIBILITY:
                    features = flatten_landmarks_to_features(landmarks)
                    collected.append(features)

                    if len(collected) >= num_samples:
                        print(f"✅ Collected {num_samples} samples. Saving...")
                        break

            cv2.imshow(f"Data Collection — {exercise} [{label}]", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord(" "):
                recording = not recording
            elif key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    if collected:
        # Build DataFrame with named feature columns (sorted, deterministic)
        df = pd.DataFrame(np.array(collected), columns=FEATURE_COLUMNS)
        df["label"]    = label
        df["exercise"] = exercise

        # Append to existing file if present
        if os.path.exists(csv_path):
            existing = pd.read_csv(csv_path)
            df = pd.concat([existing, df], ignore_index=True)

        df.to_csv(csv_path, index=False)
        print(f"💾 Saved {len(collected)} samples → {csv_path}")
    else:
        print("⚠️  No samples collected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect pose data for exercise correctness")
    parser.add_argument("--exercise", required=True,
                        choices=["squat", "pushup", "bicep_curl"])
    parser.add_argument("--label", required=True,
                        choices=["correct", "incorrect"])
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--output_dir", type=str, default="data")
    args = parser.parse_args()

    collect(args.exercise, args.label, args.samples, args.output_dir)