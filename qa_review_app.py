# qa_review_app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# -------------------------
# Page configuration
# -------------------------
st.set_page_config(
    page_title="QA Review Interface",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Simple, beautiful CSS
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

:root {
  --primary: #6366f1;
  --primary-600: #4f46e5;
  --muted: #6b7280;
  --card: #ffffff;
  --bg: #f7f9fc;
}

* { font-family: 'Inter', sans-serif; }

body {
  background: var(--bg);
}

/* Header */
.main-header {
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  padding: 1.6rem;
  border-radius: 12px;
  margin-bottom: 1.6rem;
  color: white;
  box-shadow: 0 6px 20px rgba(99,102,241,0.12);
}

.main-header h1 { margin: 0; font-weight: 700; }
.main-header p { margin: .25rem 0 0 0; opacity: 0.95; }

/* Question Card */
.question-card {
  background: var(--card);
  padding: 1.4rem;
  border-radius: 10px;
  border: 1px solid #e6eef8;
  box-shadow: 0 4px 18px rgba(15,23,42,0.04);
  margin: 1rem 0;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: white !important;
  border-right: 1px solid #eef2ff !important;
}

/* Textarea */
.stTextArea textarea {
  border: 1px solid #e6eef8 !important;
  border-radius: 8px !important;
  padding: 12px !important;
  font-size: 15px !important;
  background: white !important;
}

.stTextArea textarea:focus {
  outline: none !important;
  box-shadow: 0 0 0 4px rgba(99,102,241,0.08) !important;
  border-color: var(--primary) !important;
}

/* Buttons */
.stButton button {
  border-radius: 8px !important;
  padding: 0.55rem 1.1rem !important;
  background: var(--primary) !important;
  color: white !important;
  border: none !important;
  font-weight: 600 !important;
}
.stButton button:hover { background: var(--primary-600) !important; }

/* Download */
.stDownloadButton button { background: #16a34a !important; color: white !important; border-radius: 8px !important; }

/* Metric */
[data-testid="stMetric"] { background: #eef2ff; border-radius: 10px; padding: .7rem; }

/* Minor text */
.small-muted { color: var(--muted); font-size: .95rem; }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------
st.markdown("""
  <div class="main-header">
    <h1>🧠 QA Review Interface</h1>
    <p>✨ Evaluate model responses against gold standard answers — clean & simple</p>
  </div>
""", unsafe_allow_html=True)

# -------------------------
# Timezone and file paths
# -------------------------
bd_tz = pytz.timezone('Asia/Dhaka')
OUTPUT_FILE = "qa_dataset_with_remarks.csv"
INPUT_FILE = "qa_dataset - Sheet1.csv"

# -------------------------
# Data loader with caching
# -------------------------
@st.cache_data
def load_data(input_path):
    try:
        df_local = pd.read_csv(input_path)
        required_cols = ['Question', 'Answer', 'Gold Answer']
        missing = [c for c in required_cols if c not in df_local.columns]
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")
        return df_local
    except FileNotFoundError:
        raise
    except Exception:
        raise

# Try load
try:
    df = load_data(INPUT_FILE)
except FileNotFoundError:
    st.error(f"❌ Input file not found: {INPUT_FILE}. Please upload or place it in the app folder.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# -------------------------
# Helper to load saved reviews (if any)
# -------------------------
def load_existing_reviews(path):
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            return None
    return None

df_saved = load_existing_reviews(OUTPUT_FILE)

# -------------------------
# Sidebar: reviewer info, navigation, reset
# -------------------------
with st.sidebar:
    st.markdown("### 📋 Review Settings")
    reviewer_name = st.text_input("👤 Reviewer Name:", placeholder="Enter your name")
    reviewer_type = st.selectbox(
        "👥 Reviewer Type:",
        options=["Select Type", "Tax Payer", "Non Tax Payer", "Tax Officer"],
        index=0
    )

    # Current time
    current_time = datetime.now(bd_tz).strftime("%Y-%m-%d %I:%M:%S %p")
    st.info(f"📅 {current_time}")

    st.markdown("---")
    st.markdown("### 🎯 Quick Navigation")

    # Jump input: keep it simple; do not override session index on refresh automatically
    jump_to = st.number_input(
        "Jump to question:",
        min_value=1,
        max_value=len(df),
        value=1,
        step=1
    )

    if st.button("Go", use_container_width=True):
        # Save current review (if any) before jumping
        try:
            # Use save on-demand via common function defined later — call via st.session_state wrapper
            if 'save_review_fn' in st.session_state:
                st.session_state.save_review_fn()
        except Exception:
            pass
        st.session_state.index = int(jump_to) - 1
        # bump counters so unique keys update
        st.session_state.remark_counter = st.session_state.get('remark_counter', 0) + 1
        st.session_state.rating_counter = st.session_state.get('rating_counter', 0) + 1
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("### 📖 Instructions")
    st.markdown("""
    1. Read the question carefully.  
    2. Compare Model Answer with Gold Answer.  
    3. Rate the model's answer and add remarks.  
    4. Use Previous / Next to navigate.  
    5. Use Reset button to return to question 1.
    """)

    st.markdown("---")
    st.markdown("### ⚙️ Actions")
    # Reset behavior: saves current question, then reset index to 0
    if st.button("🔁 Reset to First Question (save current)"):
        # attempt to save current review before resetting
        try:
            if 'save_review_fn' in st.session_state:
                st.session_state.save_review_fn()
        except Exception:
            pass
        st.session_state.index = 0
        st.session_state.remark_counter = st.session_state.get('remark_counter', 0) + 1
        st.session_state.rating_counter = st.session_state.get('rating_counter', 0) + 1
        st.experimental_rerun()

# -------------------------
# Session state initialization
# -------------------------
# Index: keep in session so navigation across button clicks works.
if "index" not in st.session_state:
    # By default start at 0 (Q1)
    st.session_state.index = 0

if "remark_counter" not in st.session_state:
    st.session_state.remark_counter = 0

if "rating_counter" not in st.session_state:
    st.session_state.rating_counter = 0

# Attach save function placeholder into session_state (so sidebar can call it)
# Real function defined below; we will assign it to st.session_state.save_review_fn after definition.

# -------------------------
# Validation: require reviewer info
# -------------------------
if not reviewer_name or reviewer_type == "Select Type":
    st.markdown("""
        <div style="background:#fff8f0;border-left:4px solid #ffb020;padding:12px;border-radius:8px;">
            ⚠️ <strong>Please enter your name and select reviewer type in the sidebar before reviewing.</strong>
        </div>
    """, unsafe_allow_html=True)

# -------------------------
# Progress bar & current row
# -------------------------
progress = (st.session_state.index + 1) / len(df)
st.progress(progress)
st.caption(f"📊 Progress: {st.session_state.index + 1} of {len(df)} questions")

# Safe bounds for index
if st.session_state.index < 0:
    st.session_state.index = 0
if st.session_state.index >= len(df):
    st.session_state.index = len(df) - 1

row = df.iloc[st.session_state.index]

# -------------------------
# Load existing rating/remark for current question (if saved)
# -------------------------
existing_rating = None
existing_remark = ""
if df_saved is not None:
    # Ensure saved df has at least as many rows as original; if not, we will expand when saving
    if st.session_state.index < len(df_saved):
        if 'Rating' in df_saved.columns:
            saved_rating = df_saved.iloc[st.session_state.index].get('Rating', "")
            if pd.notna(saved_rating) and saved_rating != "":
                existing_rating = saved_rating
        if 'Remarks' in df_saved.columns:
            saved_remark = df_saved.iloc[st.session_state.index].get('Remarks', "")
            if pd.notna(saved_remark) and saved_remark != "":
                existing_remark = saved_remark

# -------------------------
# Top bar: Question title and reviewed metric
# -------------------------
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"### 📝 Question {st.session_state.index + 1}")
with col2:
    # Count reviewed
    reviewed_count = 0
    if df_saved is not None and len(df_saved) > 0:
        for i in range(min(len(df), len(df_saved))):
            has_rating = False
            has_remark = False
            if 'Rating' in df_saved.columns:
                rv = df_saved.iloc[i].get('Rating', "")
                if pd.notna(rv) and str(rv).strip() != "":
                    has_rating = True
            if 'Remarks' in df_saved.columns:
                rm = df_saved.iloc[i].get('Remarks', "")
                if pd.notna(rm) and str(rm).strip() != "":
                    has_remark = True
            if has_rating or has_remark:
                reviewed_count += 1
    st.metric("✅ Reviewed", f"{reviewed_count}/{len(df)}")

# -------------------------
# Question card
# -------------------------
st.markdown(f"""
    <div class="question-card">
      <p style="margin:0;"><strong>❓ Question:</strong></p>
      <p style="margin-top: .6rem; font-size:1.05rem; color:#0f172a;">{row['Question']}</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------
# Show Model & Gold answers
# -------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🤖 Model Answer")
    st.info(row['Answer'])
with col2:
    st.markdown("#### ✅ Gold Answer")
    st.success(row['Gold Answer'])

# -------------------------
# Rating UI
# -------------------------
st.markdown("---")
st.markdown("### ⭐ Rate the Model Answer")

rating_options = {
    "⭐⭐⭐⭐⭐ Excellent": 5,
    "⭐⭐⭐⭐ Good": 4,
    "⭐⭐⭐ Fair": 3,
    "⭐⭐ Poor": 2,
    "⭐ Very Poor": 1
}

default_index = 0
if existing_rating:
    keys = list(rating_options.keys())
    if existing_rating in keys:
        default_index = keys.index(existing_rating)

# Use dynamic keys so radio resets when we jump
rating_key = f"rating_{st.session_state.index}_{st.session_state.rating_counter}"
rating = st.radio(
    "Select a rating:",
    options=list(rating_options.keys()),
    index=default_index,
    key=rating_key,
    horizontal=True
)

# -------------------------
# Remarks UI
# -------------------------
st.markdown("---")
st.markdown("### 💭 Your Remarks")

remark_key = f"remark_{st.session_state.index}_{st.session_state.remark_counter}"
remark = st.text_area(
    "Add your evaluation remarks here:",
    value=existing_remark,
    height=150,
    key=remark_key,
    placeholder="✍️ Write your observations, corrections, or comments..."
)

# -------------------------
# Save function
# -------------------------
def save_review():
    """Save current rating and remark for current index to OUTPUT_FILE."""
    # Validate reviewer info
    if not reviewer_name or reviewer_type == "Select Type":
        st.error("⚠️ Please enter your name and select reviewer type in the sidebar!")
        return False

    # Treat rating as present if it's a non-empty string
    has_rating = rating is not None and str(rating).strip() != ""
    has_remark = remark is not None and str(remark).strip() != ""

    # If nothing to save, just update metadata? we'll still write reviewer info
    try:
        # Load or create saved frame
        if os.path.exists(OUTPUT_FILE):
            df_out = pd.read_csv(OUTPUT_FILE)
        else:
            df_out = df.copy()
            # initialize cols
            df_out['Rating'] = ""
            df_out['Rating_Value'] = ""
            df_out['Remarks'] = ""
            df_out['Reviewer'] = ""
            df_out['Reviewer_Type'] = ""
            df_out['Review_Date'] = ""

        # Ensure columns exist
        for col in ['Rating', 'Rating_Value', 'Remarks', 'Reviewer', 'Reviewer_Type', 'Review_Date']:
            if col not in df_out.columns:
                df_out[col] = ""

        # Expand df_out to at least len(df) rows if needed
        if len(df_out) < len(df):
            # append empty rows
            extra = pd.DataFrame([[""] * len(df_out.columns)] * (len(df) - len(df_out)), columns=df_out.columns)
            df_out = pd.concat([df_out, extra], ignore_index=True)

        # Save rating if present
        if has_rating:
            df_out.at[st.session_state.index, 'Rating'] = rating
            df_out.at[st.session_state.index, 'Rating_Value'] = rating_options.get(rating, "")

        # Save remark
        if has_remark:
            df_out.at[st.session_state.index, 'Remarks'] = remark

        # Save metadata (always set)
        save_time = datetime.now(bd_tz).strftime("%Y-%m-%d %I:%M:%S %p")
        df_out.at[st.session_state.index, 'Reviewer'] = reviewer_name
        df_out.at[st.session_state.index, 'Reviewer_Type'] = reviewer_type
        df_out.at[st.session_state.index, 'Review_Date'] = save_time

        # Write out
        df_out.to_csv(OUTPUT_FILE, index=False)
        # Update df_saved in memory so UI shows latest stats
        st.session_state._df_saved = df_out
        return True
    except Exception as e:
        st.error(f"Error saving review: {e}")
        return False

# Register the save function in session so sidebar can call it
st.session_state.save_review_fn = save_review

# -------------------------
# Navigation helpers
# -------------------------
def save_and_navigate(direction):
    """Save current and move prev/next if save success (or even if nothing to save)."""
    # Try to save current review, but don't block navigation if save fails
    _ = save_review()
    # bump counters to refresh keys
    st.session_state.remark_counter = st.session_state.get('remark_counter', 0) + 1
    st.session_state.rating_counter = st.session_state.get('rating_counter', 0) + 1

    if direction == "prev":
        st.session_state.index = max(0, st.session_state.index - 1)
    elif direction == "next":
        st.session_state.index = min(len(df) - 1, st.session_state.index + 1)
    return True

# -------------------------
# Navigation buttons
# -------------------------
st.markdown("---")
if st.session_state.index == len(df) - 1:
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.index == 0)):
            save_and_navigate("prev")
            st.experimental_rerun()
    with col2:
        if st.button("💾 Save & Finish", use_container_width=True):
            saved = save_review()
            if saved:
                st.success("✅ Review saved successfully!")
            st.experimental_rerun()
else:
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.index == 0)):
            save_and_navigate("prev")
            st.experimental_rerun()
    with col2:
        if st.button("Next ➡️", use_container_width=True):
            save_and_navigate("next")
            st.experimental_rerun()

# -------------------------
# Download section
# -------------------------
st.markdown("---")
col1, col2 = st.columns([2, 1])
with col2:
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
        st.info("No reviews saved yet. Start reviewing!")

# -------------------------
# Show review statistics (based on saved file)
# -------------------------
# Prefer in-memory updated df if present
df_to_stats = st.session_state.get('_df_saved', df_saved)

if df_to_stats is not None:
    with col1:
        with st.expander("📊 Review Statistics"):
            if 'Rating_Value' in df_to_stats.columns:
                ratings = pd.to_numeric(df_to_stats['Rating_Value'], errors='coerce').dropna()
                if len(ratings) > 0:
                    avg_rating = ratings.mean()
                    st.metric("Average Rating", f"{avg_rating:.2f} ⭐")
                    rating_dist = df_to_stats['Rating'].value_counts()
                    st.write("**Rating Distribution:**")
                    for rating_label, count in rating_dist.items():
                        if pd.notna(rating_label) and rating_label != "":
                            st.write(f"- {rating_label}: {count}")

            if 'Reviewer_Type' in df_to_stats.columns:
                st.markdown("---")
                reviewer_types = df_to_stats['Reviewer_Type'].value_counts()
                if len(reviewer_types) > 0:
                    st.write("**Reviews by Type:**")
                    for rtype, count in reviewer_types.items():
                        if pd.notna(rtype) and rtype != "":
                            st.write(f"- {rtype}: {count}")

# -------------------------
# End of file
# -------------------------
