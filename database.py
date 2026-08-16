"""
SQLite data layer for the attendance system.

Two tables:
- students:   one row per registered person
- attendance: one row per check-in (never updated, only inserted —
               keeps a true historical log instead of overwriting status)
"""

import sqlite3
from datetime import datetime, date
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            label_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no     TEXT UNIQUE NOT NULL,
            name        TEXT NOT NULL,
            registered_on TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            label_id    INTEGER NOT NULL,
            date        TEXT NOT NULL,
            time        TEXT NOT NULL,
            confidence  REAL,
            FOREIGN KEY (label_id) REFERENCES students(label_id)
        )
    """)
    conn.commit()
    conn.close()


def add_student(roll_no, name):
    """Insert a new student and return their integer label_id
    (this label_id is what the LBPH recognizer is trained on)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (roll_no, name, registered_on) VALUES (?, ?, ?)",
        (roll_no, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    label_id = cur.lastrowid
    conn.close()
    return label_id


def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT label_id, roll_no, name, registered_on FROM students ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_student_by_label(label_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT label_id, roll_no, name FROM students WHERE label_id = ?", (label_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_student_by_roll(roll_no):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT label_id, roll_no, name FROM students WHERE roll_no = ?", (roll_no,))
    row = cur.fetchone()
    conn.close()
    return row


def already_marked_today(label_id):
    today = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM attendance WHERE label_id = ? AND date = ? LIMIT 1",
        (label_id, today),
    )
    row = cur.fetchone()
    conn.close()
    return row is not None


def mark_attendance(label_id, confidence):
    """Insert an attendance record, but only once per student per day."""
    if already_marked_today(label_id):
        return False
    now = datetime.now()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO attendance (label_id, date, time, confidence) VALUES (?, ?, ?, ?)",
        (label_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), confidence),
    )
    conn.commit()
    conn.close()
    return True


def get_attendance_for_date(target_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.roll_no, s.name, a.date, a.time, a.confidence
        FROM attendance a JOIN students s ON a.label_id = s.label_id
        WHERE a.date = ?
        ORDER BY a.time
    """, (target_date,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_attendance():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.roll_no, s.name, a.date, a.time, a.confidence
        FROM attendance a JOIN students s ON a.label_id = s.label_id
        ORDER BY a.date DESC, a.time DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
