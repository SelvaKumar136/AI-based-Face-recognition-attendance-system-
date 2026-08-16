"""
mark_attendance.py

The main "attendance" entry point. Opens the webcam, continuously detects
and recognizes faces, and logs attendance to the database — but only once
per student per day, so walking past the camera repeatedly doesn't create
duplicate entries.

Usage:
    python mark_attendance.py
"""

import cv2

from config import CONFIDENCE_THRESHOLD
from database import init_db, mark_attendance, already_marked_today, get_student_by_label
from face_utils import detect_faces, preprocess_face, load_recognizer, load_label_map


def run_attendance():
    init_db()
    recognizer = load_recognizer()
    label_map = load_label_map()

    if recognizer is None:
        print("No trained model found. Run register_student.py then train_model.py first.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not access webcam. Check your camera connection/permissions.")
        return

    print("Attendance system running. Press 'q' to quit.\n")
    marked_this_session = set()  # avoid spamming console for the same face every frame

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray)

        for box in faces:
            x, y, w, h = box
            face = preprocess_face(gray, box)
            label_id, distance = recognizer.predict(face)

            if distance < CONFIDENCE_THRESHOLD and label_id in label_map:
                name = label_map[label_id]
                color = (0, 255, 0)
                status_text = name

                if label_id not in marked_this_session:
                    was_new = mark_attendance(label_id, distance)
                    marked_this_session.add(label_id)
                    if was_new:
                        print(f"Attendance marked: {name} (confidence distance={distance:.1f})")
                    else:
                        print(f"{name} already marked present today.")
            else:
                color = (0, 0, 255)
                status_text = "Unknown"

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, status_text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Attendance System - press q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_attendance()
