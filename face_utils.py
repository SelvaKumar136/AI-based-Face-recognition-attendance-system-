"""
Shared computer-vision helpers.

Pipeline used throughout the project:
1. Detection -> Haar Cascade finds face bounding boxes in a frame
2. Preprocessing -> crop to the face, convert to grayscale, resize to a
   fixed size (LBPH needs consistent dimensions)
3. Recognition -> LBPH (Local Binary Patterns Histogram) recognizer
   compares the face against trained data and returns
   (predicted_label_id, distance). Lower distance = more confident.
"""

import os
import json
import cv2
import numpy as np

from config import HAAR_CASCADE_PATH, FACE_SIZE, TRAINER_MODEL_PATH, LABELS_PATH

_face_detector = cv2.CascadeClassifier(HAAR_CASCADE_PATH)


def detect_faces(gray_frame):
    """Return a list of (x, y, w, h) bounding boxes for faces found in a grayscale frame."""
    return _face_detector.detectMultiScale(
        gray_frame,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80),
    )


def preprocess_face(gray_frame, box):
    x, y, w, h = box
    face = gray_frame[y:y + h, x:x + w]
    face = cv2.resize(face, FACE_SIZE)
    face = cv2.equalizeHist(face)  # normalizes lighting variation
    return face


def create_recognizer():
    return cv2.face.LBPHFaceRecognizer_create()


def load_recognizer():
    if not os.path.exists(TRAINER_MODEL_PATH):
        return None
    recognizer = create_recognizer()
    recognizer.read(TRAINER_MODEL_PATH)
    return recognizer


def save_label_map(label_to_name):
    with open(LABELS_PATH, "w") as f:
        json.dump(label_to_name, f)


def load_label_map():
    if not os.path.exists(LABELS_PATH):
        return {}
    with open(LABELS_PATH) as f:
        return {int(k): v for k, v in json.load(f).items()}
