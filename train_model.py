"""
train_model.py

Walks through dataset/<label_id>_<roll_no>/*.jpg, trains an LBPH face
recognizer on all captured samples, and saves:
- trainer/trainer.yml   (the trained model)
- trainer/labels.json   (label_id -> name, used to display results)

Run this after registering one or more students, and again any time you
register someone new.

Usage:
    python train_model.py
"""

import os
import cv2
import numpy as np

from config import DATASET_DIR
from database import init_db, get_all_students
from face_utils import create_recognizer, save_label_map


def train_model():
    init_db()
    students = get_all_students()
    if not students:
        print("No students registered yet. Run register_student.py first.")
        return

    faces = []
    labels = []
    label_to_name = {}

    for label_id, roll_no, name, _ in students:
        student_dir = os.path.join(DATASET_DIR, f"{label_id}_{roll_no}")
        if not os.path.isdir(student_dir):
            print(f"Warning: no captured images found for {name} ({roll_no}), skipping.")
            continue

        label_to_name[label_id] = name
        image_count = 0
        for filename in os.listdir(student_dir):
            if not filename.lower().endswith((".jpg", ".png")):
                continue
            img_path = os.path.join(student_dir, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            faces.append(img)
            labels.append(label_id)
            image_count += 1

        print(f"Loaded {image_count} samples for {name} ({roll_no})")

    if not faces:
        print("No face samples found across any student. Nothing to train.")
        return

    recognizer = create_recognizer()
    recognizer.train(faces, np.array(labels))
    recognizer.write(os.path.join("trainer", "trainer.yml"))
    save_label_map(label_to_name)

    print(f"\nTraining complete. Trained on {len(faces)} images across {len(label_to_name)} students.")
    print("Model saved to trainer/trainer.yml")


if __name__ == "__main__":
    train_model()
