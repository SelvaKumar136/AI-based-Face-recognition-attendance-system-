"""
register_student.py

Run this once per new student. It:
1. Asks for roll number + name
2. Adds them to the SQLite database (gets back a unique label_id)
3. Opens the webcam and captures face samples, saving them under
   dataset/<label_id>_<roll_no>/

Usage:
    python register_student.py
"""

import os
import cv2

from config import DATASET_DIR, SAMPLES_PER_STUDENT
from database import init_db, add_student, get_student_by_roll
from face_utils import detect_faces, preprocess_face


def register_student():
    init_db()

    roll_no = input("Enter Roll Number: ").strip()
    if not roll_no:
        print("Roll number is required.")
        return

    existing = get_student_by_roll(roll_no)
    if existing:
        label_id, roll_no, name = existing
        print(f"\nFound existing student: {name} ({roll_no}) with label_id={label_id}")
    else:
        name = input("Enter Full Name: ").strip()
        if not name:
            print("Name is required for new registration.")
            return
        label_id = add_student(roll_no, name)
        print(f"\nRegistered new student {name} ({roll_no}) with label_id={label_id}")

    student_dir = os.path.join(DATASET_DIR, f"{label_id}_{roll_no}")
    os.makedirs(student_dir, exist_ok=True)

    # Count existing images to continue numbering seamlessly
    existing_files = [f for f in os.listdir(student_dir) if f.lower().endswith((".jpg", ".png"))]
    start_count = len(existing_files)
    target_count = start_count + SAMPLES_PER_STUDENT

    print(f"Existing samples: {start_count}. Capturing {SAMPLES_PER_STUDENT} more (Target: {target_count}).")
    print("Opening webcam... Look at the camera. Move your head slightly for varied angles.")
    print("Press 'q' at any time to stop early.\n")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not access webcam. Check your camera connection/permissions.")
        return

    count = start_count
    while count < target_count:
        ok, frame = cap.read()
        if not ok:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray)

        for box in faces:
            face = preprocess_face(gray, box)
            count += 1
            sample_path = os.path.join(student_dir, f"{count}.jpg")
            cv2.imwrite(sample_path, face)

            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Samples: {count}/{target_count}",
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            break  # only take one face per frame to avoid duplicates from background faces

        cv2.imshow("Registering Face - press q to stop", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"\nDone. Captured {count} samples for {name}.")
    print("Next step: run `python train_model.py` to (re)train the recognizer.")


if __name__ == "__main__":
    register_student()
