"""
app.py  –  Attendance360 Professional Dashboard
A polished, SaaS-grade Streamlit dashboard for the AI Face Recognition Attendance System.
"""

import os
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st

from config import EXPORTS_DIR
from database import (
    init_db,
    get_all_students,
    get_attendance_for_date,
    get_all_attendance,
)

# ── Page config must be FIRST ──────────────────────────────────────────────────
st.set_page_config(
    page_title="FaceAttend – AI Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Lock sidebar open: hide only the collapse (X) button inside the sidebar ── */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
section[data-testid="stSidebar"] {
    min-width: 268px !important;
    max-width: 268px !important;
    transform: none !important;
    visibility: visible !important;
}
/* Also hide the collapsed-state arrow (appears when sidebar is fully closed) */
[data-testid="collapsedControl"] button { opacity: 0 !important; pointer-events: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ─── Variables ─── */
:root {
    --navy:       #0a0e1a;
    --card:       #111827;
    --card2:      #1a2235;
    --border:     #1f2d45;
    --blue:       #3b82f6;
    --blue-glow:  rgba(59,130,246,0.18);
    --green:      #22c55e;
    --red:        #ef4444;
    --amber:      #f59e0b;
    --purple:     #8b5cf6;
    --cyan:       #06b6d4;
    --text:       #f1f5f9;
    --muted:      #64748b;
    --muted2:     #94a3b8;
    --white:      #ffffff;
    --sidebar-w:  260px;
}

/* ─── Reset ─── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: var(--navy) !important;
    color: var(--text) !important;
}

/* ─── Hide Streamlit chrome ─── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] { background: var(--navy); }
[data-testid="stSidebar"] {
    background: #0d1526 !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ─── Sidebar branding ─── */
.sidebar-brand {
    padding: 28px 24px 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}
.sidebar-logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--blue), var(--purple));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 14px rgba(59,130,246,0.4);
}
.sidebar-logo-text {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--white);
    letter-spacing: -0.3px;
}
.sidebar-logo-sub {
    font-size: 0.7rem;
    color: var(--muted);
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ─── Sidebar nav links ─── */
.sidebar-nav { padding: 8px 12px; }
.sidebar-section-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 12px 12px 6px;
}
.nav-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--muted2);
    cursor: pointer;
    transition: all 0.18s ease;
    margin-bottom: 2px;
    text-decoration: none;
}
.nav-link:hover { background: rgba(59,130,246,0.1); color: var(--white); }
.nav-link.active {
    background: linear-gradient(90deg, rgba(59,130,246,0.2), rgba(139,92,246,0.1));
    color: var(--white);
    border: 1px solid rgba(59,130,246,0.25);
    font-weight: 600;
}
.nav-link .icon { font-size: 1rem; min-width: 20px; }

/* ─── Sidebar status ─── */
.sidebar-status {
    margin: 16px 16px 0;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 10px;
    padding: 12px 14px;
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--green);
    border-radius: 50%;
    margin-right: 6px;
    animation: blink 2s infinite;
}
@keyframes blink {
    0%,100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.status-text { font-size: 0.78rem; font-weight: 600; color: var(--green); }
.status-sub { font-size: 0.72rem; color: var(--muted); margin-top: 3px; }

/* ─── Sidebar footer ─── */
.sidebar-footer {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 16px;
    border-top: 1px solid var(--border);
    background: #0d1526;
}
.sidebar-user {
    display: flex;
    align-items: center;
    gap: 10px;
}
.sidebar-avatar {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--blue), var(--purple));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 700; color: white;
}
.sidebar-user-name { font-size: 0.82rem; font-weight: 600; color: var(--text); }
.sidebar-user-role { font-size: 0.7rem; color: var(--muted); }

/* ─── Top bar ─── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 32px;
    border-bottom: 1px solid var(--border);
    background: rgba(13,21,38,0.95);
    backdrop-filter: blur(12px);
    margin-bottom: 0;
}
.topbar-left { }
.topbar-page-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--white);
    letter-spacing: -0.3px;
}
.topbar-breadcrumb {
    font-size: 0.76rem;
    color: var(--muted);
    margin-top: 1px;
}
.topbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.topbar-time {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--muted2);
    font-variant-numeric: tabular-nums;
}
.topbar-badge {
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.3);
    color: var(--green);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* ─── Main content area ─── */
.main-content { padding: 28px 32px; }

/* ─── KPI Cards ─── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 28px;
}
.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.blue  { border-left: 3px solid var(--blue); }
.kpi-card.green { border-left: 3px solid var(--green); }
.kpi-card.red   { border-left: 3px solid var(--red); }
.kpi-card.purple{ border-left: 3px solid var(--purple); }
.kpi-card.amber { border-left: 3px solid var(--amber); }
.kpi-card.cyan  { border-left: 3px solid var(--cyan); }

.kpi-glow {
    position: absolute;
    top: -20px; right: -20px;
    width: 80px; height: 80px;
    border-radius: 50%;
    opacity: 0.12;
}
.kpi-card.blue  .kpi-glow { background: var(--blue); }
.kpi-card.green .kpi-glow { background: var(--green); }
.kpi-card.red   .kpi-glow { background: var(--red); }
.kpi-card.purple .kpi-glow { background: var(--purple); }

.kpi-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 14px;
}
.kpi-icon-wrap {
    width: 40px; height: 40px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.kpi-card.blue  .kpi-icon-wrap { background: rgba(59,130,246,0.15); }
.kpi-card.green .kpi-icon-wrap { background: rgba(34,197,94,0.12); }
.kpi-card.red   .kpi-icon-wrap { background: rgba(239,68,68,0.12); }
.kpi-card.purple .kpi-icon-wrap { background: rgba(139,92,246,0.12); }

.kpi-trend {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
}
.kpi-trend.up   { background: rgba(34,197,94,0.1);  color: var(--green); }
.kpi-trend.down { background: rgba(239,68,68,0.1);  color: var(--red); }
.kpi-trend.neu  { background: rgba(100,116,139,0.1); color: var(--muted2); }

.kpi-value {
    font-size: 2.4rem;
    font-weight: 900;
    color: var(--white);
    line-height: 1;
    letter-spacing: -1px;
    margin-bottom: 4px;
}
.kpi-label {
    font-size: 0.78rem;
    color: var(--muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.kpi-sublabel {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--border);
}
.kpi-sublabel b { color: var(--muted2); }

/* ─── Section layouts ─── */
.section-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 22px;
}
.section-card-header {
    padding: 18px 24px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.section-card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--white);
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-card-title .dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--blue);
    animation: blink 2s infinite;
}
.section-card-body { padding: 20px 24px; }
.section-badge {
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.2);
    color: #93c5fd;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 6px;
}

/* ─── Attendance row cards ─── */
.att-row {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 6px;
    background: var(--card2);
    border: 1px solid var(--border);
    transition: background 0.15s;
}
.att-row:hover { background: #1f2d45; }
.att-avatar {
    width: 38px; height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--blue), var(--purple));
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700; color: white;
    flex-shrink: 0; margin-right: 14px;
}
.att-name { font-size: 0.9rem; font-weight: 600; color: var(--white); }
.att-roll { font-size: 0.75rem; color: var(--muted); margin-top: 1px; }
.att-time {
    margin-left: auto;
    font-size: 0.8rem;
    color: var(--muted2);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 12px;
}
.att-status-pill {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.25);
    color: var(--green);
    letter-spacing: 0.3px;
}
.att-status-pill.absent {
    background: rgba(239,68,68,0.1);
    border-color: rgba(239,68,68,0.25);
    color: var(--red);
}
.att-confidence {
    font-size: 0.72rem;
    color: var(--muted);
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 2px 8px;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 2px;
    border-bottom: 1px solid var(--border);
    padding: 0 0 0 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 10px 20px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--blue) !important;
    font-weight: 700 !important;
    border-bottom: 2px solid var(--blue) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }

/* ─── Progress bar ─── */
.progress-wrap {
    background: var(--border);
    border-radius: 8px;
    height: 7px;
    overflow: hidden;
    margin-top: 8px;
}
.progress-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.4s ease;
}
.progress-fill.blue   { background: linear-gradient(90deg, var(--blue), #60a5fa); }
.progress-fill.green  { background: linear-gradient(90deg, var(--green), #4ade80); }
.progress-fill.amber  { background: linear-gradient(90deg, var(--amber), #fbbf24); }
.progress-fill.purple { background: linear-gradient(90deg, var(--purple), #a78bfa); }

/* ─── Empty State ─── */
.empty-wrap {
    text-align: center;
    padding: 52px 20px;
    color: var(--muted);
}
.empty-icon { font-size: 3rem; margin-bottom: 12px; }
.empty-title { font-size: 1rem; font-weight: 700; color: var(--muted2); margin-bottom: 6px; }
.empty-desc { font-size: 0.82rem; }
.empty-cmd {
    display: inline-block;
    background: var(--card2);
    border: 1px solid var(--border);
    color: #93c5fd;
    padding: 4px 12px;
    border-radius: 6px;
    font-family: monospace;
    font-size: 0.8rem;
    margin-top: 8px;
}

/* ─── Download button ─── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e3a5f, #162440) !important;
    color: #60a5fa !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 7px 18px !important;
    transition: all 0.2s !important;
    font-family: 'Inter', sans-serif !important;
}
.stDownloadButton > button:hover {
    background: var(--blue) !important;
    color: white !important;
    border-color: var(--blue) !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.35) !important;
}

/* ─── Text input ─── */
.stTextInput input {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 9px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
}
.stDateInput input {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 9px !important;
}

/* ─── Selectbox ─── */
.stSelectbox select {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 9px !important;
}

/* ─── Dataframe ─── */
.stDataFrame { border-radius: 10px !important; }
[data-testid="stDataFrame"] > div {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* ─── Sidebar radio override ─── */
.stRadio > label { display: none !important; }
.stRadio > div { flex-direction: column !important; gap: 4px !important; }
.stRadio > div > label {
    background: transparent !important;
    border: none !important;
    padding: 9px 14px !important;
    border-radius: 10px !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
    color: var(--muted2) !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}
.stRadio > div > label:hover {
    background: rgba(59,130,246,0.1) !important;
    color: var(--white) !important;
}
.stRadio > div [aria-checked="true"] {
    background: linear-gradient(90deg, rgba(59,130,246,0.18), rgba(139,92,246,0.08)) !important;
    color: var(--white) !important;
    font-weight: 600 !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
}

/* ─── Charts label override ─── */
[data-testid="stVegaLiteChart"] {
    border-radius: 12px;
    overflow: hidden;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--navy); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
""", unsafe_allow_html=True)

# ── DATA ───────────────────────────────────────────────────────────────────────
today_str = date.today().strftime("%Y-%m-%d")
today_display = date.today().strftime("%A, %B %d %Y")
now_str = datetime.now().strftime("%I:%M %p")

today_rows = get_attendance_for_date(today_str)
all_rows   = get_all_attendance()
students   = get_all_students()

total_students = len(students)
present_today  = len(today_rows)
absent_today   = total_students - present_today
att_pct        = int((present_today / total_students * 100) if total_students > 0 else 0)
total_records  = len(all_rows)
unique_days    = len(set(r[2] for r in all_rows)) if all_rows else 0

# Build sets for quick lookup
present_names  = set(r[1] for r in today_rows)
present_rolls  = set(r[0] for r in today_rows)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon" style="font-size:22px;background:linear-gradient(135deg,#2563eb,#7c3aed);">🎓</div>
            <div>
                <div class="sidebar-logo-text">FaceAttend</div>
                <div class="sidebar-logo-sub">AI Attendance System</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)

    page = st.radio("nav", [
        "📊  Dashboard",
        "📅  Today's Attendance",
        "📋  History & Reports",
        "👤  Students",
    ], label_visibility="hidden")

    st.markdown(f"""
    <div class="sidebar-status">
        <div><span class="status-dot"></span><span class="status-text">System Online</span></div>
        <div class="status-sub">AI Recognition Active &nbsp;·&nbsp; {now_str}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">Quick Stats</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding:0 4px;">
        <div style="font-size:0.78rem;color:#64748b;margin-bottom:4px;padding:6px 10px;">
            Today's Attendance Rate
        </div>
        <div style="padding:0 10px 10px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-size:0.8rem;color:#94a3b8;font-weight:600;">{att_pct}% present</span>
                <span style="font-size:0.78rem;color:#64748b;">{present_today}/{total_students}</span>
            </div>
            <div class="progress-wrap"><div class="progress-fill {'green' if att_pct >= 75 else 'amber' if att_pct >= 50 else 'blue'}" style="width:{att_pct}%"></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;width:260px;padding:16px;border-top:1px solid #1f2d45;background:#0d1526;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:0.82rem;font-weight:700;color:white;">A</div>
            <div>
                <div style="font-size:0.82rem;font-weight:600;color:#f1f5f9;">Administrator</div>
                <div style="font-size:0.7rem;color:#64748b;">Full Access</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── TOPBAR ─────────────────────────────────────────────────────────────────────
page_labels = {
    "📊  Dashboard":           ("🎓 FaceAttend — Overview",         "Home / Dashboard"),
    "📅  Today's Attendance":  ("Today's Attendance",               "Home / Attendance / Today"),
    "📋  History & Reports":   ("History & Reports",                "Home / Attendance / History"),
    "👤  Students":            ("Student Directory",                "Home / Students"),
}
page_title, breadcrumb = page_labels.get(page, ("Dashboard", "Home"))

st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-page-title">{page_title}</div>
        <div class="topbar-breadcrumb">{breadcrumb}</div>
    </div>
    <div class="topbar-right">
        <div class="topbar-time">🕐 {now_str} &nbsp;·&nbsp; {date.today().strftime('%b %d, %Y')}</div>
        <div class="topbar-badge"><span style="width:7px;height:7px;background:#22c55e;border-radius:50%;display:inline-block;"></span> Live</div>
    </div>
</div>
<div class="main-content">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊  Dashboard":

    # KPI Grid
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card blue">
            <div class="kpi-glow"></div>
            <div class="kpi-top">
                <div class="kpi-icon-wrap">👥</div>
                <div class="kpi-trend neu">Total</div>
            </div>
            <div class="kpi-value">{total_students}</div>
            <div class="kpi-label">Registered Students</div>
            <div class="kpi-sublabel">Enrolled in system</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-glow"></div>
            <div class="kpi-top">
                <div class="kpi-icon-wrap">✅</div>
                <div class="kpi-trend up">Today</div>
            </div>
            <div class="kpi-value">{present_today}</div>
            <div class="kpi-label">Present Today</div>
            <div class="kpi-sublabel"><b>{att_pct}%</b> attendance rate</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-glow"></div>
            <div class="kpi-top">
                <div class="kpi-icon-wrap">⛔</div>
                <div class="kpi-trend {'down' if absent_today > 0 else 'up'}">{absent_today}</div>
            </div>
            <div class="kpi-value">{absent_today}</div>
            <div class="kpi-label">Absent Today</div>
            <div class="kpi-sublabel">Not yet checked in</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-glow"></div>
            <div class="kpi-top">
                <div class="kpi-icon-wrap">📋</div>
                <div class="kpi-trend neu">All time</div>
            </div>
            <div class="kpi-value">{total_records}</div>
            <div class="kpi-label">Total Records</div>
            <div class="kpi-sublabel">Across <b>{unique_days}</b> session days</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Full-width Present / Absent named board ──────────────────────────────
    absent_students_list = [(lid, r, n, reg) for lid, r, n, reg in students if n not in present_names]

    col_p, col_a = st.columns(2, gap="large")

    with col_p:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-card-header">
                <div class="section-card-title">
                    <span class="dot" style="background:#22c55e;"></span>
                    Present Today
                </div>
                <div class="section-badge" style="background:rgba(34,197,94,0.1);border-color:rgba(34,197,94,0.25);color:#22c55e;">
                    {present_today} student{'s' if present_today != 1 else ''}
                </div>
            </div>
        """, unsafe_allow_html=True)

        if today_rows:
            for roll, name, dt, tm, conf in today_rows:
                initials = "".join([w[0].upper() for w in name.split()[:2]])
                conf_str = f"{conf:.1f}" if conf else "—"
                st.markdown(f"""
                <div class="att-row" style="margin:0 16px 8px;">
                    <div class="att-avatar" style="background:linear-gradient(135deg,#16a34a,#22c55e);">{initials}</div>
                    <div style="flex:1;">
                        <div class="att-name">{name}</div>
                        <div class="att-roll">Roll: {roll} &nbsp;·&nbsp; Checked in {tm}</div>
                    </div>
                    <span class="att-status-pill">✓ Present</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-wrap" style="padding:30px 16px;">
                <div class="empty-icon" style="font-size:2rem;">📷</div>
                <div class="empty-title">No check-ins yet</div>
                <div class="empty-desc">Run <span class="empty-cmd">mark_attendance.py</span></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div></div>", unsafe_allow_html=True)

    with col_a:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-card-header">
                <div class="section-card-title">
                    <span class="dot" style="background:#ef4444;animation:none;"></span>
                    Absent Today
                </div>
                <div class="section-badge" style="background:rgba(239,68,68,0.1);border-color:rgba(239,68,68,0.25);color:#ef4444;">
                    {absent_today} student{'s' if absent_today != 1 else ''}
                </div>
            </div>
        """, unsafe_allow_html=True)

        if absent_students_list:
            for lid, roll, name, reg in absent_students_list:
                initials = "".join([w[0].upper() for w in name.split()[:2]])
                st.markdown(f"""
                <div class="att-row" style="margin:0 16px 8px;">
                    <div class="att-avatar" style="background:linear-gradient(135deg,#b91c1c,#ef4444);">{initials}</div>
                    <div style="flex:1;">
                        <div class="att-name">{name}</div>
                        <div class="att-roll">Roll: {roll} &nbsp;·&nbsp; Enrolled {reg[:10]}</div>
                    </div>
                    <span class="att-status-pill absent">✗ Absent</span>
                </div>
                """, unsafe_allow_html=True)
        elif total_students == 0:
            st.markdown("""
            <div class="empty-wrap" style="padding:30px 16px;">
                <div class="empty-icon" style="font-size:2rem;">👤</div>
                <div class="empty-title">No students enrolled</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-wrap" style="padding:30px 16px;">
                <div class="empty-icon" style="font-size:2rem;">🎉</div>
                <div class="empty-title">100% Attendance!</div>
                <div class="empty-desc">All students are present today.</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div></div>", unsafe_allow_html=True)

    # ── Rate card + Pipeline row ───────────────────────────────────────────────
    col_rate, col_pipe = st.columns([1, 1], gap="large")

    with col_rate:
        prog_color = 'green' if att_pct >= 75 else 'amber' if att_pct >= 50 else 'blue'
        rate_color = '#22c55e' if att_pct >= 75 else '#f59e0b' if att_pct >= 50 else '#ef4444'
        st.markdown(f"""
        <div class="section-card">
            <div class="section-card-header">
                <div class="section-card-title"><span class="dot" style="background:#22c55e"></span> Today's Rate</div>
                <div class="section-badge">{today_display[:10]}</div>
            </div>
            <div style="text-align:center;padding:20px 24px 24px;">
                <div style="font-size:3rem;font-weight:900;color:{rate_color};letter-spacing:-2px;line-height:1;">{att_pct}%</div>
                <div style="color:#64748b;font-size:0.82rem;margin:6px 0 16px;">Attendance Rate</div>
                <div class="progress-wrap" style="height:8px;">
                    <div class="progress-fill {prog_color}" style="width:{att_pct}%"></div>
                </div>
                <div style="display:flex;justify-content:space-around;margin-top:18px;">
                    <div style="text-align:center;">
                        <div style="font-size:1.4rem;font-weight:800;color:#22c55e;">{present_today}</div>
                        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">Present</div>
                    </div>
                    <div style="width:1px;background:#1f2d45;"></div>
                    <div style="text-align:center;">
                        <div style="font-size:1.4rem;font-weight:800;color:#ef4444;">{absent_today}</div>
                        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">Absent</div>
                    </div>
                    <div style="width:1px;background:#1f2d45;"></div>
                    <div style="text-align:center;">
                        <div style="font-size:1.4rem;font-weight:800;color:#3b82f6;">{total_students}</div>
                        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">Total</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_pipe:
        st.markdown("""
        <div class="section-card">
            <div class="section-card-header">
                <div class="section-card-title">⚙️ AI Pipeline</div>
            </div>
            <div style="padding:16px 20px;">
        """, unsafe_allow_html=True)

        pipeline = [
            ("📷", "Webcam Capture",   "Live video input",         "#3b82f6"),
            ("🔍", "Haar Cascade",     "Face detection & bbox",    "#8b5cf6"),
            ("🧠", "LBPH Recognizer",  "Feature match & classify", "#06b6d4"),
            ("🗄️", "SQLite Database",  "Deduplicated log storage", "#22c55e"),
        ]
        for icon, title, desc, color in pipeline:
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #1f2d45;">
                <div style="width:32px;height:32px;background:rgba({r},{g},{b},0.12);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:0.95rem;flex-shrink:0;">{icon}</div>
                <div>
                    <div style="font-size:0.83rem;font-weight:600;color:#f1f5f9;">{title}</div>
                    <div style="font-size:0.72rem;color:#64748b;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TODAY'S ATTENDANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📅  Today's Attendance":

    # KPI row
    st.markdown(f"""
    <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr);">
        <div class="kpi-card green">
            <div class="kpi-glow"></div>
            <div class="kpi-top"><div class="kpi-icon-wrap">✅</div><div class="kpi-trend up">+{present_today}</div></div>
            <div class="kpi-value">{present_today}</div>
            <div class="kpi-label">Present Today</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-glow"></div>
            <div class="kpi-top"><div class="kpi-icon-wrap">⛔</div><div class="kpi-trend down">{absent_today}</div></div>
            <div class="kpi-value">{absent_today}</div>
            <div class="kpi-label">Absent</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-glow"></div>
            <div class="kpi-top"><div class="kpi-icon-wrap">📊</div><div class="kpi-trend {'up' if att_pct>=75 else 'neu'}">{att_pct}%</div></div>
            <div class="kpi-value">{att_pct}%</div>
            <div class="kpi-label">Attendance Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_p, tab_a = st.tabs(["✅  Present", "⛔  Absent"])

    with tab_p:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        if today_rows:
            for roll, name, dt, tm, conf in today_rows:
                initials = "".join([w[0].upper() for w in name.split()[:2]])
                conf_str = f"{conf:.1f}" if conf else "—"
                st.markdown(f"""
                <div class="att-row">
                    <div class="att-avatar">{initials}</div>
                    <div>
                        <div class="att-name">{name}</div>
                        <div class="att-roll">Roll No: {roll}</div>
                    </div>
                    <div class="att-time">
                        <span class="att-confidence">Confidence: {conf_str}</span>
                        <span style="color:#64748b;">{tm}</span>
                        <span class="att-status-pill">Present ✓</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            df = pd.DataFrame(today_rows, columns=["Roll No", "Name", "Date", "Time", "Confidence"])
            csv_path = os.path.join(EXPORTS_DIR, f"attendance_{today_str}.csv")
            df.to_csv(csv_path, index=False)
            with open(csv_path, "rb") as f:
                st.download_button("⬇  Export Today's Attendance (CSV)", f,
                                   file_name=f"attendance_{today_str}.csv", mime="text/csv")
        else:
            st.markdown("""
            <div class="empty-wrap">
                <div class="empty-icon">📷</div>
                <div class="empty-title">No one marked present yet</div>
                <div class="empty-desc">Run the attendance script to start recognizing faces</div>
                <div class="empty-cmd">python mark_attendance.py</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_a:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        absent_students = [(lid, r, n, reg) for lid, r, n, reg in students if n not in present_names]
        if absent_students:
            for lid, roll, name, reg in absent_students:
                initials = "".join([w[0].upper() for w in name.split()[:2]])
                st.markdown(f"""
                <div class="att-row">
                    <div class="att-avatar" style="background:linear-gradient(135deg,#ef4444,#f97316);">{initials}</div>
                    <div>
                        <div class="att-name">{name}</div>
                        <div class="att-roll">Roll No: {roll}</div>
                    </div>
                    <div class="att-time">
                        <span style="color:#64748b;font-size:0.75rem;">Registered: {reg[:10]}</span>
                        <span class="att-status-pill absent">Absent</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            if total_students == 0:
                st.markdown('<div class="empty-wrap"><div class="empty-icon">👤</div><div class="empty-title">No students registered</div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-wrap"><div class="empty-icon">🎉</div><div class="empty-title">100% Attendance!</div><div class="empty-desc">All students are present today.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY & REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋  History & Reports":

    st.markdown(f"""
    <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr);">
        <div class="kpi-card blue">
            <div class="kpi-top"><div class="kpi-icon-wrap">📋</div><div class="kpi-trend neu">All</div></div>
            <div class="kpi-value">{total_records}</div>
            <div class="kpi-label">Total Records</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-top"><div class="kpi-icon-wrap">📆</div><div class="kpi-trend neu">&nbsp;</div></div>
            <div class="kpi-value">{unique_days}</div>
            <div class="kpi-label">Session Days</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-top"><div class="kpi-icon-wrap">👥</div><div class="kpi-trend neu">&nbsp;</div></div>
            <div class="kpi-value">{total_students}</div>
            <div class="kpi-label">Students Enrolled</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filters row
    st.markdown("""
    <div class="section-card">
        <div class="section-card-header">
            <div class="section-card-title">🔎 Search & Filter</div>
        </div>
        <div style="padding:16px 20px 0;">
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("Search", placeholder="Search by name or roll number…", label_visibility="collapsed")
    with col2:
        date_from = st.date_input("From", value=None, label_visibility="collapsed")
    with col3:
        date_to   = st.date_input("To", value=None, label_visibility="collapsed")
    st.markdown("</div></div>", unsafe_allow_html=True)

    if all_rows:
        df_all = pd.DataFrame(all_rows, columns=["Roll No", "Name", "Date", "Time", "Confidence"])
        df_all["Confidence"] = df_all["Confidence"].apply(lambda x: f"{x:.1f}" if x else "—")
        filtered = df_all.copy()

        if search:
            filtered = filtered[
                filtered["Name"].str.contains(search, case=False) |
                filtered["Roll No"].str.contains(search, case=False)
            ]
        if date_from:
            filtered = filtered[filtered["Date"] >= str(date_from)]
        if date_to:
            filtered = filtered[filtered["Date"] <= str(date_to)]

        st.markdown("""
        <div class="section-card">
            <div class="section-card-header">
                <div class="section-card-title"><span class="dot" style="background:#8b5cf6"></span> Records</div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="section-badge" style="float:right">{len(filtered)} results</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        filtered["Status"] = "Present"
        st.dataframe(
            filtered[["Roll No", "Name", "Date", "Time", "Confidence", "Status"]],
            width="stretch",
            height=min(500, 60 + len(filtered) * 40),
            hide_index=True,
        )

        col_dl1, col_dl2, _ = st.columns([1, 1, 4])
        with col_dl1:
            csv_path = os.path.join(EXPORTS_DIR, "attendance_full_history.csv")
            df_all.to_csv(csv_path, index=False)
            with open(csv_path, "rb") as f:
                st.download_button("⬇  Export All CSV", f, file_name="attendance_full_history.csv", mime="text/csv")
        with col_dl2:
            if len(filtered) < len(df_all):
                csv_bytes = filtered.to_csv(index=False).encode()
                st.download_button("⬇  Export Filtered", csv_bytes, file_name="attendance_filtered.csv", mime="text/csv")

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-wrap">
            <div class="empty-icon">📋</div>
            <div class="empty-title">No Records Yet</div>
            <div class="empty-desc">History will appear after attendance is logged</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: STUDENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤  Students":

    st.markdown(f"""
    <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr);">
        <div class="kpi-card blue">
            <div class="kpi-top"><div class="kpi-icon-wrap">👥</div><div class="kpi-trend neu">Total</div></div>
            <div class="kpi-value">{total_students}</div>
            <div class="kpi-label">Enrolled Students</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-top"><div class="kpi-icon-wrap">✅</div><div class="kpi-trend up">Today</div></div>
            <div class="kpi-value">{present_today}</div>
            <div class="kpi-label">Present Today</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-top"><div class="kpi-icon-wrap">⛔</div><div class="kpi-trend down">&nbsp;</div></div>
            <div class="kpi-value">{absent_today}</div>
            <div class="kpi-label">Absent Today</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if students:
        st.markdown("""
        <div class="section-card">
            <div class="section-card-header">
                <div class="section-card-title"><span class="dot" style="background:#22c55e"></span> Student Directory</div>
            </div>
            <div style="padding:16px 20px 8px;">
        """, unsafe_allow_html=True)

        for label_id, roll_no, name, registered_on in students:
            initials = "".join([w[0].upper() for w in name.split()[:2]])
            is_present = name in present_names
            status_html = '<span class="att-status-pill">Present ✓</span>' if is_present else '<span class="att-status-pill absent">Absent</span>'
            avatar_color = "linear-gradient(135deg,#3b82f6,#8b5cf6)" if is_present else "linear-gradient(135deg,#ef4444,#f97316)"

            # Total attendance count for student
            student_records = sum(1 for r in all_rows if r[0] == roll_no)

            st.markdown(f"""
            <div class="att-row" style="margin-bottom:8px;">
                <div class="att-avatar" style="background:{avatar_color};">{initials}</div>
                <div style="flex:1;">
                    <div class="att-name">{name}</div>
                    <div class="att-roll">Roll No: {roll_no} &nbsp;·&nbsp; ID #{label_id} &nbsp;·&nbsp; Enrolled {registered_on[:10]}</div>
                </div>
                <div class="att-time">
                    <div style="text-align:center;">
                        <div style="font-size:1.1rem;font-weight:800;color:#f1f5f9;">{student_records}</div>
                        <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">Sessions</div>
                    </div>
                    {status_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        df_s = pd.DataFrame(students, columns=["Label ID", "Roll No", "Name", "Registered On"])
        csv_bytes = df_s.to_csv(index=False).encode()
        st.download_button("⬇  Export Student List (CSV)", csv_bytes, file_name="students.csv", mime="text/csv")
    else:
        st.markdown("""
        <div class="empty-wrap">
            <div class="empty-icon">👤</div>
            <div class="empty-title">No Students Registered</div>
            <div class="empty-desc">Enroll a student to get started</div>
            <div class="empty-cmd">python register_student.py</div>
        </div>
        """, unsafe_allow_html=True)

# ── Close main-content div ─────────────────────────────────────────────────
st.markdown("</div>", unsafe_allow_html=True)
