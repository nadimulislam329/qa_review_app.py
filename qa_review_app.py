import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# Page configuration
st.set_page_config(page_title="QA Review Interface", page_icon="🧠", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .question-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .stTextArea textarea {
        border: 2px solid #667eea;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div class="main-header">
        <h1>🧠 QA Review Interface</h1>
        <p style='font-size: 1.1rem; margin: 0;'>Evaluate model responses against gold standard answers</p>
    </div>
""", unsafe_allow_html=True)

# Set timezone to Bangladesh
bd_tz = pytz.timezone('Asia/Dhaka')

# Sidebar for reviewer info and settings
with st.sidebar:
    st.header("📋 Review Settings")
    reviewer_name = st.text_input("Reviewer Name:", placeholder="Enter your name")

    # Show current time in Bangladesh timezone
    current_time = datetime.now(bd_tz).strftime("%Y-%m-%d %I:%M:%S %p")
    st.info(f"📅 {current_time}")

    st.markdown("---")
    st.subheader("📖 Instructions")
    st.markdown("""
    1. Read the question carefully
    2. Compare Model Answer with Gold Answer
    3. Add your remarks
    4. Navigate using Previous/Next
    5. Remarks are auto-saved!
    """)

# Define file paths
OUTPUT_FILE = "qa_dataset_with_remarks.csv"

# Load data
df = pd.read_csv("qa_dataset - Sheet1.csv")

if "index" not in st.session_state:
    st.session_state.index = 0

if "remark_counter" not in st.session_state:
    st.session_state.remark_counter = 0

# Progress bar
progress = (st.session_state.index + 1) / len(df)
st.progress(progress)
st.caption(f"Progress: {st.session_state.index + 1} of {len(df)} questions")

# Question Display
row = df.iloc[st.session_state.index]

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"### 📝 Question {st.session_state.index + 1}")
with col2:
    # Count saved remarks
    remarks_count = 0
    if os.path.exists(OUTPUT_FILE):
        try:
            df_saved = pd.read_csv(OUTPUT_FILE)
            if 'Remarks' in df_saved.columns:
                # Count non-empty remarks
                remarks_count = df_saved['Remarks'].apply(lambda x: isinstance(x, str) and x.strip() != "").sum()
        except Exception as e:
            pass

    st.metric("Reviewed", f"{remarks_count}/{len(df)}")

# Question Card
st.markdown(f"""
    <div class="question-card">
        <p style="margin: 0; font-size: 1.1rem; color: #333;"><strong>❓ Question:</strong></p>
        <p style="margin-top: 0.5rem; font-size: 1rem; color: #555;">{row['Question']}</p>
    </div>
""", unsafe_allow_html=True)

# Answers in columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🤖 Model Answer")
    st.info(row['Answer'])

with col2:
    st.markdown("#### ✅ Gold Answer")
    st.success(row['Gold Answer'])

# Remarks section
st.markdown("---")
st.markdown("### 💭 Your Remarks")

# Use a unique key that changes each time we want to clear the text area
remark = st.text_area(
    "Add your evaluation remarks here:",
    "",
    height=150,
    key=f"remark_{st.session_state.index}_{st.session_state.remark_counter}",
    placeholder="Write your observations, corrections, or comments..."
)

def save_remark():
    """Save the current remark to CSV"""
    if remark.strip() != "":
        try:
            if os.path.exists(OUTPUT_FILE):
                df_saved = pd.read_csv(OUTPUT_FILE)
            else:
                df_saved = df.copy()
                df_saved['Remarks'] = ""
                df_saved['Reviewer'] = ""
                df_saved['Review_Date'] = ""

            # Get the ACTUAL time when saving in Bangladesh timezone with 12-hour format
            save_time = datetime.now(bd_tz).strftime("%Y-%m-%d %I:%M:%S %p")

            # Update the remark for current question
            df_saved.at[st.session_state.index, 'Remarks'] = remark
            df_saved.at[st.session_state.index, 'Reviewer'] = reviewer_name if reviewer_name else "Anonymous"
            df_saved.at[st.session_state.index, 'Review_Date'] = save_time

            # Save to CSV
            df_saved.to_csv(OUTPUT_FILE, index=False)
            return True
        except Exception as e:
            st.error(f"Error saving: {e}")
            return False
    return False

def save_and_navigate(direction):
    # Save current remark
    save_remark()

    # Increment counter to force new text area
    st.session_state.remark_counter += 1

    # Navigate
    if direction == "prev":
        st.session_state.index = max(0, st.session_state.index - 1)
    elif direction == "next":
        st.session_state.index = min(len(df) - 1, st.session_state.index + 1)

# Navigation buttons
st.markdown("---")

# If it's the last question, show a Save button
if st.session_state.index == len(df) - 1:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Previous", use_container_width=True):
            save_and_navigate("prev")
            st.rerun()


    with col3:
        if st.button("💾 Save & Finish", use_container_width=True, type="primary"):
            if save_remark():
                # Increment counter to create a new empty text area
                st.session_state.remark_counter += 1
                st.success("✅ Remark saved successfully!")
                st.rerun()
            else:
                st.warning("⚠️ No remark to save")
else:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.index == 0)):
            save_and_navigate("prev")
            st.rerun()


    with col3:
        if st.button("Next ➡️", use_container_width=True):
            save_and_navigate("next")
            st.rerun()
# Download section
st.markdown("---")
st.markdown("### 📥 Download Results")

col1, col2 = st.columns([3, 1])

with col1:
    st.write("Download the completed review with all remarks")

with col3:
    if os.path.exists(OUTPUT_FILE):
        try:
            df_download = pd.read_csv(OUTPUT_FILE)
            csv = df_download.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"qa_review_remarks_{datetime.now(bd_tz).strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        st.info("No remarks saved yet. Start reviewing!")
