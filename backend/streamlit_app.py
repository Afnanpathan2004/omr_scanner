"""
Streamlit UI for OMR Checker using the mock processor (no OpenCV required).
"""

import os
import uuid
import json
from pathlib import Path

import streamlit as st

# Import mock processor (avoids OpenCV dependency)
from mock_omr_utils import OMRProcessor

# Resolve directories relative to this file
BASE_DIR = Path(__file__).parent
ANSWER_KEYS_DIR = BASE_DIR / "answer_keys"
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"

for d in (ANSWER_KEYS_DIR, UPLOAD_DIR, RESULTS_DIR):
    d.mkdir(exist_ok=True)

st.set_page_config(page_title="OMR Checker", page_icon="✅", layout="centered")
st.title("OMR Checker (Streamlit)")
st.caption("Upload an OMR sheet image, select an answer key, and get instant results.")

# Load available answer keys
answer_keys = sorted([p.stem for p in ANSWER_KEYS_DIR.glob("*.json")])
if not answer_keys:
    st.warning("No answer keys found in 'backend/answer_keys/'. Add JSON files like exam1.json.")

selected_key = st.selectbox(
    "Select answer key",
    options=answer_keys if answer_keys else [""],
    index=0 if answer_keys else 0,
    disabled=not answer_keys,
)

uploaded = st.file_uploader("Upload OMR image (jpg/png)", type=["jpg", "jpeg", "png"], accept_multiple_files=False)

if uploaded is not None:
    st.image(uploaded, caption="Uploaded image preview", use_container_width=True)

col1, col2 = st.columns([1, 1])
with col1:
    run_btn = st.button("Process OMR", type="primary", disabled=uploaded is None or not answer_keys)
with col2:
    clear_btn = st.button("Clear")

if clear_btn:
    st.experimental_rerun()

if run_btn:
    try:
        # Persist upload to disk
        suffix = Path(uploaded.name).suffix.lower()
        unique_name = f"{uuid.uuid4()}{suffix}"
        file_path = UPLOAD_DIR / unique_name
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())

        # Load answer key JSON
        key_path = ANSWER_KEYS_DIR / f"{selected_key}.json"
        if not key_path.exists():
            st.error(f"Answer key '{selected_key}' not found at {key_path}")
            st.stop()
        with open(key_path, "r", encoding="utf-8") as f:
            answer_key = json.load(f)

        # Process with mock OMR processor
        processor = OMRProcessor()
        result = processor.process_omr_sheet(str(file_path), answer_key)

        # Optionally clean up uploaded file to keep folder tidy
        try:
            os.remove(file_path)
        except Exception:
            pass

        # Display results
        st.subheader("Score")
        m1, m2, m3 = st.columns(3)
        m1.metric("Correct", f"{result.score}")
        m2.metric("Total", f"{result.total}")
        m3.metric("Percentage", f"{result.percentage}%")

        st.subheader("Question-wise Result")
        # Build a simple table (without requiring pandas)
        table_rows = []
        for q in sorted(result.correct_answers.keys(), key=lambda x: int(x)):
            table_rows.append(
                {
                    "Q#": q,
                    "Marked": result.marked_answers.get(q, ""),
                    "Correct": result.correct_answers.get(q, ""),
                    "Status": result.result.get(q, "")
                }
            )
        st.table(table_rows)

        with st.expander("Raw Result JSON"):
            st.json(result.dict())

    except Exception as e:
        st.error(f"Failed to process OMR: {e}")
