# AI-Based Face Recognition Attendance System

A real-time attendance system that detects and recognizes faces via webcam
and automatically logs attendance to a database — no manual sign-in sheets.

## How it works (pipeline)

```
Webcam Frame
   │
   ▼
1. Face Detection  → Haar Cascade (cv2.CascadeClassifier)
   │  finds bounding boxes of faces in the frame
   ▼
2. Preprocessing   → crop to face → grayscale → resize (200x200)
   │                 → histogram equalization (normalizes lighting)
   ▼
3. Face Recognition → LBPH (Local Binary Patterns Histogram)
   │  cv2.face.LBPHFaceRecognizer_create()
   │  compares the face against the trained model,
   │  returns (predicted_label_id, distance)
   ▼
4. Decision         → if distance < threshold → known student
   │                  else → "Unknown"
   ▼
5. Attendance Log   → SQLite (one row per student per day — no duplicates)
   ▼
6. Dashboard         → Streamlit app to view / export attendance as CSV
```

## Tech Stack

| Component         | Tool/Library                          |
|--------------------|----------------------------------------|
| Face detection     | OpenCV Haar Cascade                    |
| Face recognition   | OpenCV LBPH (`opencv-contrib-python`)  |
| Database           | SQLite                                 |
| Dashboard          | Streamlit + Pandas                     |

## Project Structure

```
face_attendance_system/
├── config.py            # paths, thresholds, constants
├── database.py          # SQLite schema + queries
├── face_utils.py         # shared detection/recognition helpers
├── register_student.py  # CLI: capture face samples for a new student
├── train_model.py       # trains the LBPH model on captured samples
├── mark_attendance.py   # live webcam attendance marking
├── app.py               # Streamlit dashboard
├── requirements.txt
├── dataset/             # captured face images (created at runtime)
├── trainer/             # trained model + label map (created at runtime)
└── exports/             # CSV exports from the dashboard
```

## Setup

```bash
pip install -r requirements.txt
```

> Note: this project needs a webcam connected to whichever machine you run
> it on. It will NOT work inside a sandboxed/cloud environment without
> camera access — run it on your laptop/PC.

## Usage

**1. Register a student** (run once per person):
```bash
python register_student.py
```
Enter roll number and name, then look at the webcam while it captures ~60
face samples.

**2. Train the model** (run after registering one or more students):
```bash
python train_model.py
```

**3. Run live attendance:**
```bash
python mark_attendance.py
```
Recognized faces are boxed in green with their name; unrecognized faces are
boxed in red as "Unknown". Each student is marked present only once per day.
Press `q` to quit.

**4. View the dashboard:**
```bash
streamlit run app.py
```
Shows today's attendance, full history, and registered students, with CSV
export buttons.

## Design Decisions Worth Knowing for a Viva/Interview

- **Why Haar Cascade + LBPH instead of a deep learning model
  (FaceNet/dlib)?** It's lightweight, doesn't need GPU or a heavy `dlib`
  install (which is a common pain point on Windows), and is fast enough for
  real-time use on a normal laptop. The tradeoff is it's less robust to
  extreme pose/lighting variation than a deep embedding model — a good
  "future improvement" to mention.
- **Why mark attendance only once per day?** Prevents duplicate spam if a
  student walks past the camera multiple times in one session.
- **Why store raw face images in `dataset/` instead of just embeddings?**
  Makes it possible to retrain with a different/better algorithm later
  without needing to recapture data.
- **Known limitations:** no liveness detection (a printed photo could fool
  it), accuracy drops in poor lighting, and one face is trained on a single
  fixed-size grayscale crop rather than learned embeddings.

## Possible Extensions (good talking points)

- Add liveness detection (blink detection) to prevent photo spoofing
- Switch to a deep-learning embedding model (e.g., `face_recognition`/dlib
  or FaceNet) for higher accuracy
- Email/SMS alert to admin for unrecognized faces
- Multi-camera support across multiple classrooms/entry points
