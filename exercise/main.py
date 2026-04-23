"""
main.py
-------
Main launcher for the Exercise Correctness Detection system.
Provides a simple menu to navigate all features.

Usage:
    python main.py
"""

import os
import sys
import subprocess


MENU = """
╔══════════════════════════════════════════════════════╗
║     EXERCISE CORRECTNESS VIA POSE ESTIMATION         ║
║     Group 21 | PCCO308 | Sanjivani COE               ║
╠══════════════════════════════════════════════════════╣
║  1. Collect Training Data                            ║
║  2. Train ML Models                                  ║
║  3. Run Real-Time Detection                          ║
║  4. Exit                                             ║
╚══════════════════════════════════════════════════════╝
"""

EXERCISES = {
    "1": "squat",
    "2": "pushup",
    "3": "bicep_curl",
}

LABELS = {
    "1": "correct",
    "2": "incorrect",
}


def choose_exercise():
    print("\n  Select Exercise:")
    for k, v in EXERCISES.items():
        print(f"    {k}. {v}")
    choice = input("  Enter choice: ").strip()
    return EXERCISES.get(choice)


def collect_data():
    print("\n── DATA COLLECTION ──")
    exercise = choose_exercise()
    if not exercise:
        print("Invalid choice.")
        return

    print("\n  Select Label:")
    for k, v in LABELS.items():
        print(f"    {k}. {v}")
    lc = input("  Enter choice: ").strip()
    label = LABELS.get(lc)
    if not label:
        print("Invalid choice.")
        return

    samples = input("  Number of samples [default: 200]: ").strip()
    samples = int(samples) if samples.isdigit() else 200

    subprocess.run([
        sys.executable, "data_collection.py",
        "--exercise", exercise,
        "--label", label,
        "--samples", str(samples),
    ])


def train_models():
    print("\n── MODEL TRAINING ──")
    subprocess.run([sys.executable, "train_model.py"])


def run_detection():
    print("\n── REAL-TIME DETECTION ──")
    exercise = choose_exercise()
    if not exercise:
        print("Invalid choice.")
        return
    subprocess.run([
        sys.executable, "realtime_feedback.py",
        "--exercise", exercise,
    ])


def main():
    while True:
        print(MENU)
        choice = input("  Enter choice (1-4): ").strip()

        if choice == "1":
            collect_data()
        elif choice == "2":
            train_models()
        elif choice == "3":
            run_detection()
        elif choice == "4":
            print("\n  Goodbye! 👋\n")
            break
        else:
            print("  ⚠️  Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
