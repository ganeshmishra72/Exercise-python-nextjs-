"""
pose_utils.py
-------------
Utility functions for pose estimation:
- Extracting MediaPipe landmarks
- Calculating joint angles
- Drawing skeleton overlays

FIXES:
- flatten_landmarks_to_features: now returns consistent 52-feature vector
  regardless of which joints are missing (fills zeros for absent joints)
- calculate_angle: guards against zero-length vectors properly
- draw_pose: angles display area no longer overlaps with CORRECT/INCORRECT label
- extract_landmarks: returns None clearly when pose confidence is too low
"""

import numpy as np
import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


# ──────────────────────────────────────────────
# LANDMARK INDICES (MediaPipe Pose)
# ──────────────────────────────────────────────
# Ordered list — order MUST stay constant so the feature vector is stable.
LANDMARK_NAMES = [
    "nose",
    "left_shoulder", "right_shoulder",
    "left_elbow",    "right_elbow",
    "left_wrist",    "right_wrist",
    "left_hip",      "right_hip",
    "left_knee",     "right_knee",
    "left_ankle",    "right_ankle",
]

LANDMARK_INDICES = {
    "nose": 0,
    "left_shoulder": 11, "right_shoulder": 12,
    "left_elbow": 13,    "right_elbow": 14,
    "left_wrist": 15,    "right_wrist": 16,
    "left_hip": 23,      "right_hip": 24,
    "left_knee": 25,     "right_knee": 26,
    "left_ankle": 27,    "right_ankle": 28,
}

# Keep the old name for backward compatibility
LANDMARKS = LANDMARK_INDICES

NUM_LANDMARKS = len(LANDMARK_NAMES)       # 13
FEATURES_PER_LANDMARK = 4                 # x, y, z, visibility
NUM_FEATURES = NUM_LANDMARKS * FEATURES_PER_LANDMARK  # 52


def calculate_angle(a, b, c):
    """
    Calculate the angle at point B formed by points A-B-C.

    Parameters:
        a, b, c : array-like  [x, y] or [x, y, z, ...]

    Returns:
        angle in degrees (0–180)  or  0.0 if vectors are degenerate
    """
    a = np.array(a[:2], dtype=float)
    b = np.array(b[:2], dtype=float)
    c = np.array(c[:2], dtype=float)

    ba = a - b
    bc = c - b

    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 0.0

    cosine = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine = np.clip(cosine, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine))
    return round(float(angle), 2)


def extract_landmarks(results):
    """
    Extract the 13 tracked landmarks from MediaPipe results.

    Returns:
        dict  name → [x, y, z, visibility]
        None  if no pose detected
    """
    if not results.pose_landmarks:
        return None

    lm = results.pose_landmarks.landmark
    data = {}
    for name, idx in LANDMARK_INDICES.items():
        data[name] = [
            lm[idx].x,
            lm[idx].y,
            lm[idx].z,
            lm[idx].visibility,
        ]
    return data


def get_angles_for_exercise(landmarks, exercise):
    """
    Compute relevant joint angles for the given exercise.

    Parameters:
        landmarks : dict from extract_landmarks()
        exercise  : 'squat' | 'pushup' | 'bicep_curl'

    Returns:
        dict  angle_name → angle_value (degrees)
    """
    angles = {}

    if exercise == "squat":
        angles["left_knee"] = calculate_angle(
            landmarks["left_hip"],
            landmarks["left_knee"],
            landmarks["left_ankle"],
        )
        angles["right_knee"] = calculate_angle(
            landmarks["right_hip"],
            landmarks["right_knee"],
            landmarks["right_ankle"],
        )
        angles["left_hip"] = calculate_angle(
            landmarks["left_shoulder"],
            landmarks["left_hip"],
            landmarks["left_knee"],
        )
        angles["right_hip"] = calculate_angle(
            landmarks["right_shoulder"],
            landmarks["right_hip"],
            landmarks["right_knee"],
        )

    elif exercise == "pushup":
        angles["left_elbow"] = calculate_angle(
            landmarks["left_shoulder"],
            landmarks["left_elbow"],
            landmarks["left_wrist"],
        )
        angles["right_elbow"] = calculate_angle(
            landmarks["right_shoulder"],
            landmarks["right_elbow"],
            landmarks["right_wrist"],
        )
        angles["left_shoulder"] = calculate_angle(
            landmarks["left_elbow"],
            landmarks["left_shoulder"],
            landmarks["left_hip"],
        )
        angles["right_shoulder"] = calculate_angle(
            landmarks["right_elbow"],
            landmarks["right_shoulder"],
            landmarks["right_hip"],
        )
        angles["left_hip"] = calculate_angle(
            landmarks["left_shoulder"],
            landmarks["left_hip"],
            landmarks["left_knee"],
        )

    elif exercise == "bicep_curl":
        angles["left_elbow"] = calculate_angle(
            landmarks["left_shoulder"],
            landmarks["left_elbow"],
            landmarks["left_wrist"],
        )
        angles["right_elbow"] = calculate_angle(
            landmarks["right_shoulder"],
            landmarks["right_elbow"],
            landmarks["right_wrist"],
        )
        angles["left_shoulder"] = calculate_angle(
            landmarks["left_hip"],
            landmarks["left_shoulder"],
            landmarks["left_elbow"],
        )
        angles["right_shoulder"] = calculate_angle(
            landmarks["right_hip"],
            landmarks["right_shoulder"],
            landmarks["right_elbow"],
        )

    return angles


def draw_pose(frame, results, angles=None, label=None, color=(0, 255, 0)):
    """
    Draw the pose skeleton and optionally overlay angles and label.

    Parameters:
        frame   : BGR image (numpy array)
        results : MediaPipe pose results
        angles  : dict  angle_name → value  (optional)
        label   : 'CORRECT' | 'INCORRECT'   (optional)
        color   : BGR tuple for label box    (unused; kept for API compat)
    """
    # Draw skeleton
    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
    )

    # Overlay angles — placed on the RIGHT side to avoid overlapping label
    if angles:
        h, w = frame.shape[:2]
        y_offset = 70
        for name, val in angles.items():
            cv2.putText(
                frame,
                f"{name}: {val:.1f}°",
                (w - 260, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1,
                cv2.LINE_AA,
            )
            y_offset += 22

    # Overlay CORRECT / INCORRECT label at bottom-left
    if label:
        text_color = (0, 255, 0) if label == "CORRECT" else (0, 0, 255)
        h = frame.shape[0]
        cv2.rectangle(frame, (0, h - 55), (260, h), (0, 0, 0), -1)
        cv2.putText(
            frame,
            label,
            (10, h - 15),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            text_color,
            2,
            cv2.LINE_AA,
        )

    return frame


def flatten_landmarks_to_features(landmarks):
    """
    Flatten the 13 tracked landmarks into a fixed-length 1-D feature vector.

    The vector is always length 52 (13 joints × 4 values).
    Missing joints (None entries) are filled with zeros so the shape is
    ALWAYS consistent — critical for ML inference.

    Returns:
        numpy array of shape (52,)
    """
    feature = []
    for name in LANDMARK_NAMES:          # fixed, deterministic order
        vals = landmarks.get(name)
        if vals is not None:
            feature.extend(vals[:FEATURES_PER_LANDMARK])
        else:
            feature.extend([0.0] * FEATURES_PER_LANDMARK)
    arr = np.array(feature, dtype=np.float32)
    assert arr.shape == (NUM_FEATURES,), f"Feature shape mismatch: {arr.shape}"
    return arr