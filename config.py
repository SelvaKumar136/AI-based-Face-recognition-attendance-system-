"""
Central configuration for the Face Recognition Attendance System.
Keeping all paths/constants in one place makes the project easier to
explain in an interview and easier to tweak later.
"""

import os
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(BASE_DIR, "dataset")      # captured face images, per student
TRAINER_DIR = os.path.join(BASE_DIR, "trainer")       # trained LBPH model + label map
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")       # CSV exports from the dashboard
DB_PATH = os.path.join(BASE_DIR, "attendance.db")

TRAINER_MODEL_PATH = os.path.join(TRAINER_DIR, "trainer.yml")
LABELS_PATH = os.path.join(TRAINER_DIR, "labels.json")

# Haar Cascade shipped with opencv-python — no extra download needed
HAAR_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# Number of face samples to capture per student during registration
SAMPLES_PER_STUDENT = 150

# LBPH prediction returns a "distance" — LOWER means more confident match.
# Anything above this threshold is treated as "Unknown".
CONFIDENCE_THRESHOLD = 75

# Resize every captured face to this size before training/recognition
FACE_SIZE = (200, 200)

for d in (DATASET_DIR, TRAINER_DIR, EXPORTS_DIR):
    os.makedirs(d, exist_ok=True)
