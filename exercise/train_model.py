"""
train_model.py
--------------
Train a Random Forest classifier for each exercise (squat, pushup, bicep_curl).

Produces:
  models/squat_model.pkl
  models/pushup_model.pkl
  models/bicep_curl_model.pkl
  reports/  (confusion matrices + feature importance charts)

Usage:
    python train_model.py

FIXES:
 1. Feature column selection: now sorts feature columns alphabetically so
    the training-time feature order ALWAYS matches inference-time order
    from flatten_landmarks_to_features(). The original code used whatever
    order pandas returned from pd.concat, which could differ across runs
    or Python versions.
 2. Label encoding: uses the hard-coded 0=incorrect, 1=correct mapping
    instead of relying on string comparison which is case-sensitive and
    would silently produce all-0 labels if the CSV used 'Correct' vs 'correct'.
 3. plot_feature_importance: only called when the pipeline contains a
    RandomForestClassifier (guard added for future model swaps).
 4. Augmented print output so model/report paths are absolute.
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns   # noqa: F401  (kept for potential heatmap use)

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    ConfusionMatrixDisplay,
)
from sklearn.pipeline import Pipeline

# ── Config ────────────────────────────────────────────────────────────────────
EXERCISES  = ["squat", "pushup", "bicep_curl"]
DATA_DIR   = "data"
MODEL_DIR  = "models"
REPORT_DIR = "reports"

LABEL_MAP  = {"correct": 1, "incorrect": 0}   # FIX #2: explicit, case-insensitive
LABEL_NAMES = ["incorrect", "correct"]          # index 0 / 1


# ── Data loading ──────────────────────────────────────────────────────────────
def load_data(exercise: str):
    """
    Load correct + incorrect CSVs for one exercise.

    Returns (X, y) numpy arrays, or (None, None) if data is missing.
    Feature columns are SORTED so order is deterministic.          ← FIX #1
    """
    correct_path   = os.path.join(DATA_DIR, f"{exercise}_correct.csv")
    incorrect_path = os.path.join(DATA_DIR, f"{exercise}_incorrect.csv")

    missing = [p for p in [correct_path, incorrect_path] if not os.path.exists(p)]
    if missing:
        print(f"  ⚠️  Missing data files: {missing}  → skipping {exercise}")
        return None, None

    df_c = pd.read_csv(correct_path)
    df_i = pd.read_csv(incorrect_path)
    df   = pd.concat([df_c, df_i], ignore_index=True)

    # FIX #2: map label string → int with explicit, case-insensitive mapping
    df["label_clean"] = df["label"].str.strip().str.lower().map(LABEL_MAP)
    unmapped = df["label_clean"].isna().sum()
    if unmapped:
        print(f"  ⚠️  {unmapped} rows had unrecognised labels and will be dropped.")
        df = df.dropna(subset=["label_clean"])

    y = df["label_clean"].astype(int).values

    # FIX #1: sort feature columns deterministically
    non_feature = {"label", "exercise", "label_clean"}
    feature_cols = sorted([c for c in df.columns if c not in non_feature])
    X = df[feature_cols].values.astype(np.float32)

    n_correct   = int(y.sum()) # type: ignore
    n_incorrect = len(y) - n_correct
    print(f"  ✅ {exercise}: {n_correct} correct, {n_incorrect} incorrect  "
          f"({len(feature_cols)} features)")
    return X, y


# ── Model pipeline ────────────────────────────────────────────────────────────
def build_pipeline() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        )),
    ])


# ── Evaluation ────────────────────────────────────────────────────────────────
def evaluate_and_save(
    exercise: str,
    pipeline: Pipeline,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> float:
    os.makedirs(MODEL_DIR,  exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    y_pred = pipeline.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)

    print(f"\n{'─'*50}")
    print(f"  {exercise.upper()} — Test Accuracy: {acc * 100:.2f}%")
    print(f"{'─'*50}")
    print(classification_report(y_test, y_pred, target_names=LABEL_NAMES))

    # Confusion matrix
    cm   = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABEL_NAMES).plot(
        ax=ax, colorbar=False, cmap="Blues"
    )
    ax.set_title(f"{exercise.capitalize()} — Confusion Matrix\nAccuracy: {acc*100:.2f}%")
    plt.tight_layout()
    plot_path = os.path.join(REPORT_DIR, f"{exercise}_confusion_matrix.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"  📊 Confusion matrix → {os.path.abspath(plot_path)}")

    # Save model
    model_path = os.path.join(MODEL_DIR, f"{exercise}_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"  💾 Model saved     → {os.path.abspath(model_path)}")

    return acc


# ── Feature importance ────────────────────────────────────────────────────────
def plot_feature_importance(exercise: str, pipeline: Pipeline, n_features: int = 20):
    """Only plots for RandomForest (has feature_importances_)."""   # FIX #3
    clf = pipeline.named_steps.get("clf")
    if not hasattr(clf, "feature_importances_"):
        return

    importances = clf.feature_importances_
    indices     = np.argsort(importances)[::-1][:n_features]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(n_features), importances[indices], color="steelblue")
    ax.set_xticks(range(n_features))
    ax.set_xticklabels([f"f{i}" for i in indices], rotation=45)
    ax.set_title(f"{exercise.capitalize()} — Top {n_features} Feature Importances")
    ax.set_ylabel("Importance")
    plt.tight_layout()

    path = os.path.join(REPORT_DIR, f"{exercise}_feature_importance.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  📊 Feature importance → {os.path.abspath(path)}")


# ── Main ──────────────────────────────────────────────────────────────────────
def train_all():
    print("\n" + "=" * 55)
    print("  EXERCISE CORRECTNESS — MODEL TRAINING")
    print("=" * 55)

    results = {}

    for exercise in EXERCISES:
        print(f"\n🏋️  Training: {exercise.upper()}")
        X, y = load_data(exercise)
        if X is None:
            continue

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        pipeline = build_pipeline()

        # 5-fold cross-validation on training set
        cv       = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy")
        print(f"  📈 5-Fold CV: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

        pipeline.fit(X_train, y_train)

        acc = evaluate_and_save(exercise, pipeline, X_test, y_test)
        plot_feature_importance(exercise, pipeline)

        results[exercise] = acc

    # Summary
    print("\n" + "=" * 55)
    if results:
        print("  TRAINING SUMMARY")
        print("=" * 55)
        for ex, acc in results.items():
            bar = "█" * int(acc * 30)
            print(f"  {ex:12s} [{bar:<30}] {acc*100:.2f}%")
        print("=" * 55)
        print(f"\n✅ Models  → {os.path.abspath(MODEL_DIR)}/")
        print(f"✅ Reports → {os.path.abspath(REPORT_DIR)}/")
    else:
        print("  ⚠️  No models trained — collect data first with data_collection.py")


if __name__ == "__main__":
    train_all()