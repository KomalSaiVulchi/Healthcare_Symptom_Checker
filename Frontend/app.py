# Frontend/app.py
import os
import json
from datetime import datetime

import requests
import streamlit as st

# Resolve backend URLs from Streamlit secrets (preferred), env vars, or localhost
def _get_base_url() -> str:
    base = None
    try:
        base = st.secrets.get("BASE_API_URL")  # e.g. https://your-render.onrender.com
    except Exception:
        base = None
    base = base or os.getenv("BASE_API_URL")
    return base or "http://localhost:8000"

BASE_API_URL = _get_base_url().rstrip("/")
API_URL = os.getenv("API_URL") or f"{BASE_API_URL}/api/diagnose"
LOGS_URL = os.getenv("LOGS_URL") or f"{BASE_API_URL}/api/logs"
FEEDBACK_URL = os.getenv("FEEDBACK_URL") or f"{BASE_API_URL}/api/feedback"
LOCAL_FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "feedback_offline.jsonl")

# Page setup
st.set_page_config(page_title="Symptom Checker", page_icon="🩺", layout="wide")

# Small CSS tweaks for a nicer look
st.markdown(
    """
    <style>
    .result-card {background: #f8fafc; border-radius: 8px; padding: 14px;}
    .muted {color: #6b7280}
    .small {font-size:0.9rem}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_API_URL = _get_base_url().rstrip("/")
API_URL = os.getenv("API_URL") or f"{BASE_API_URL}/api/diagnose"
LOGS_URL = os.getenv("LOGS_URL") or f"{BASE_API_URL}/api/logs"
FEEDBACK_URL = os.getenv("FEEDBACK_URL") or f"{BASE_API_URL}/api/feedback"
LOCAL_FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "feedback_offline.jsonl")


def init_page():
    st.set_page_config(page_title="Symptom Checker", page_icon="🩺", layout="wide")
    if "history" not in st.session_state:
        st.session_state.history = []


def inject_css():
    st.markdown(
        """
        <style>
        .card {background: linear-gradient(180deg,#ffffff,#fbfbff); border:1px solid #e6e9ef; border-radius:12px; padding:18px;}
        .muted {color:#6b7280}
        .small {font-size:0.9rem}
        /* Make main headings red */
        h1, h2, h3, .stHeader, .stSubheader { color: #d32f2f !important; }
        .logo {font-weight:700; font-size:1.25rem}
        .env-badge {background:#eef4ff; border:1px solid #cfe0ff; color:#1e40af; padding:6px 10px; border-radius:8px; display:inline-block; font-size:0.85rem}
        </style>
        """,
        unsafe_allow_html=True,
    )


def local_feedback_count() -> int:
    try:
        with open(LOCAL_FEEDBACK_PATH, "r", encoding="utf-8") as fh:
            return sum(1 for _ in fh)
    except Exception:
        return 0


def sidebar_controls():
    st.sidebar.markdown("<div class='logo'>Healthcare Symptom Checker</div>", unsafe_allow_html=True)
    st.sidebar.write("For educational purposes only — not medical advice.")
    st.sidebar.markdown("---")
    st.sidebar.header("Quick examples")
    examples = {
        "Sore throat": "sore throat, mild fever for 2 days",
        "Cough & fever": "persistent dry cough, fever 38.5C, 4 days",
        "Headache": "severe headache, nausea, blurred vision",
    }
    ex = st.sidebar.selectbox("Load example", ["(none)"] + list(examples.keys()))
    preset = ""
    if ex != "(none)":
        preset = examples[ex]

    st.sidebar.markdown("---")
    st.sidebar.header("Options")
    user_id = st.sidebar.text_input("User ID (optional)", value="anonymous")
    show_confidence = st.sidebar.checkbox("Show confidence", value=True)
    auto_fetch_logs = st.sidebar.checkbox("Auto-fetch logs on load", value=False)
    # show offline feedback count
    fb_count = local_feedback_count()
    if fb_count:
        st.sidebar.warning(f"{fb_count} feedback items saved offline")

    return preset, user_id, show_confidence, auto_fetch_logs


def show_result_card(data, show_confidence=True):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Analysis Result")
    res = data.get("result") or "No result returned."
    st.write(res)
    # allow downloading the result
    st.download_button("Download result", data=res, file_name="symptom_result.txt")
    if show_confidence and data.get("confidence"):
        st.info(f"Confidence: {data.get('confidence')}")
    if data.get("disclaimer"):
        st.caption(data.get("disclaimer"))
    # suggested actions if present
    actions = data.get("actions")
    if actions:
        st.markdown("**Suggested actions:**")
        for a in actions:
            st.write(f"- {a}")
    st.markdown("---")

    # Feedback UI
    st.markdown("### Was this helpful?")
    col1, col2 = st.columns([1, 3])
    with col1:
        rating = st.radio("Rate", options=[5, 4, 3, 2, 1], index=0, format_func=lambda x: f"{x}★")
    with col2:
        feedback_text = st.text_area("Feedback (optional)")

    if st.button("Submit feedback"):
        fb = {
            "time": datetime.utcnow().isoformat(),
            "rating": rating,
            "feedback": feedback_text,
            "result": res,
        }
        ok = submit_feedback(fb)
        if ok:
            st.success("Thanks — feedback submitted.")
        else:
            st.warning("Saved feedback locally (backend unreachable).")

    st.markdown("</div>", unsafe_allow_html=True)


def fetch_and_display_logs():
    try:
        r = requests.get(LOGS_URL, timeout=20)
        if r.status_code == 200:
            logs = r.json().get("logs", [])
            if logs:
                # show latest 10
                for l in logs[:10]:
                    t = l.get("created_at", "")
                    st.write(f"**{t}** — {l.get('symptom')[:120]}")
                    st.caption(l.get("response")[:200] or "")
            else:
                st.info("No logs available.")
        else:
            st.error(f"Logs API error {r.status_code}: {r.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching logs: {e}")


def submit_feedback(feedback: dict) -> bool:
    """Try to POST feedback to the backend. If it fails, save locally and return False."""
    try:
        r = requests.post(FEEDBACK_URL, json=feedback, timeout=8)
        if r.status_code in (200, 201):
            return True
        # fallback to local save
    except requests.exceptions.RequestException:
        pass

    # Ensure folder exists and append as JSON line
    try:
        os.makedirs(os.path.dirname(LOCAL_FEEDBACK_PATH), exist_ok=True)
        with open(LOCAL_FEEDBACK_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(feedback, ensure_ascii=False) + "\n")
    except Exception:
        # if local save fails, there's not much we can do in-app
        return False
    return False


def render_main(preset, user_id, show_confidence, auto_fetch_logs):
    left, right = st.columns([2, 1])

    with left:
        st.header("Describe your symptoms")
        with st.form("symptom_form"):
            symptoms = st.text_area("Symptoms (be concise)", value=preset, height=160)
            age = st.number_input("Age (optional)", min_value=0, max_value=120, value=0)
            chronic = st.text_input("Chronic conditions (optional)")
            submitted = st.form_submit_button("Analyze")

        if submitted:
            if not symptoms or not symptoms.strip():
                st.error("Please enter your symptoms before analyzing.")
            else:
                payload = {
                    "text": symptoms + (f"; age:{age}" if age else "") + (f"; chronic:{chronic}" if chronic else ""),
                    "user_id": user_id,
                }
                with st.spinner("Contacting backend and analyzing..."):
                    try:
                        r = requests.post(API_URL, json=payload, timeout=30)
                        if r.status_code == 200:
                            data = r.json()
                            record = {
                                "time": datetime.utcnow().isoformat(),
                                "symptom": symptoms,
                                "result": data.get("result"),
                            }
                            st.session_state.history.insert(0, record)
                            show_result_card(data, show_confidence)
                        else:
                            st.error(f"Backend error {r.status_code}: {r.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error connecting to backend: {e}")

        # session history quick view
        if st.session_state.history:
            st.markdown("### Recent (this session)")
            for h in st.session_state.history[:5]:
                with st.expander(h["symptom"][:80]):
                    st.write(h["result"] or "(no result)")

    with right:
        st.markdown("### Quick Tips")
        st.write("- Include duration and severity")
        st.write("- Note existing conditions or medications")
        st.write("- Short, comma-separated items work best")

        st.markdown("---")
        st.markdown("### Backend Logs")
        if st.button("Refresh logs"):
            fetch_and_display_logs()


def main():
    init_page()
    inject_css()
    st.markdown(f"<div class='env-badge'>Backend: {BASE_API_URL}</div>", unsafe_allow_html=True)
    preset, user_id, show_confidence, auto_fetch_logs = sidebar_controls()
    render_main(preset, user_id, show_confidence, auto_fetch_logs)
    if auto_fetch_logs:
        fetch_and_display_logs()


if __name__ == "__main__":
    main()
