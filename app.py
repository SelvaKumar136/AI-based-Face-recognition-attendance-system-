"""
app.py

Streamlit dashboard for the Face Recognition Attendance System.
View today's attendance, browse full history, see registered students,
and export records to CSV.

Usage:
    streamlit run app.py
"""

import os
from datetime import date

import pandas as pd
import streamlit as st

from config import EXPORTS_DIR
from database import (
    init_db,
    get_all_students,
    get_attendance_for_date,
    get_all_attendance,
)

st.set_page_config(page_title="Face Recognition Attendance", page_icon="🎓", layout="wide")

init_db()

st.title("🎓 AI-Based Face Recognition Attendance System")

tab1, tab2, tab3 = st.tabs(["📅 Today's Attendance", "📋 Full History", "👥 Registered Students"])

with tab1:
    today = date.today().strftime("%Y-%m-%d")
    st.subheader(f"Attendance — {today}")
    rows = get_attendance_for_date(today)

    if rows:
        df = pd.DataFrame(rows, columns=["Roll No", "Name", "Date", "Time", "Confidence (distance)"])
        st.dataframe(df, use_container_width=True)
        st.metric("Present Today", len(df))

        csv_path = os.path.join(EXPORTS_DIR, f"attendance_{today}.csv")
        df.to_csv(csv_path, index=False)
        with open(csv_path, "rb") as f:
            st.download_button("⬇ Download Today's CSV", f, file_name=f"attendance_{today}.csv")
    else:
        st.info("No attendance marked yet today. Run `mark_attendance.py` to start logging.")

with tab2:
    st.subheader("Full Attendance History")
    rows = get_all_attendance()
    if rows:
        df = pd.DataFrame(rows, columns=["Roll No", "Name", "Date", "Time", "Confidence (distance)"])
        st.dataframe(df, use_container_width=True)

        csv_path = os.path.join(EXPORTS_DIR, "attendance_full_history.csv")
        df.to_csv(csv_path, index=False)
        with open(csv_path, "rb") as f:
            st.download_button("⬇ Download Full History CSV", f, file_name="attendance_full_history.csv")
    else:
        st.info("No attendance records yet.")

with tab3:
    st.subheader("Registered Students")
    students = get_all_students()
    if students:
        df = pd.DataFrame(students, columns=["Label ID", "Roll No", "Name", "Registered On"])
        st.dataframe(df, use_container_width=True)
        st.metric("Total Registered Students", len(df))
    else:
        st.info("No students registered yet. Run `register_student.py` to add one.")

st.caption("Pipeline: Haar Cascade (face detection) → LBPH (face recognition) → SQLite (attendance log)")
