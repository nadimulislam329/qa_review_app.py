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
# Enhanced CSS styling
# -------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite;
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .main-header h1 {
        position: relative;
        z-index: 1;
        font-weight: 700;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        position: relative;
        z-index: 1;
        margin: 0;
        opacity: 0.95;
    }
    
    .question-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .question-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .question-card p {
        margin: 0;
        line-height: 1.6;
    }
    
    .question-card strong {
        color: #667eea;
        font-size: 1.1rem;
    }
    
    .stTextArea textarea {
        border: 2px solid #e0e7ff !important;
        border-radius: 10px !important;
        padding: 15px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        background: white !important;
        color: #2d3748 !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #a0aec0 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    .stTextArea label {
        color: #2d3748 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stSelectbox select {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stMetric"] label {
        color: white !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    .stButton button {
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .stDownloadButton button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
    }
    
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #20c997 0%, #28a745 100%) !important;
    }
    
    h1, h2, h3, h4 {
        font-weight: 700 !important;
        color: #2d3748 !important;
    }
    
    h3 {
        color: #667eea !important;
    }
    
    .stSuccess {
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem;
        }
        
        .question-card {
            padding: 1.5rem;
        }
    }
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
# Helper to load saved reviews
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
# Session state initialization
# -------------------------
if "index" not in st.session_state:
    st.session_state.index = 0

if "remark_counter" not in st.session_state:
    st.session_state.remark_counter = 0

if "rating_counter" not in st.session_state:
    st.session_state.rating_counter = 0

# -------------------------
# Sidebar - Initialize first
# -------------------------
with st.sidebar:
    st.markdown("### 📋 Review Settings")
    reviewer_name = st.text_input(
        "👤 Reviewer Name:", 
        placeholder="Enter your name",
        key="reviewer_name_input"
    )
    reviewer_type = st.selectbox(
        "👥 Reviewer Type:",
        options=["Select Type", "Tax Payer", "Non Tax Payer", "Tax Officer"],
        index=0,
        key="reviewer_type_input"
    )

    # Current time
    current_time = datetime.now(bd_tz).strftime("%Y-%m-%d %I:%M:%S %p")
    st.info(f"📅 {current_time}")

    st.markdown("---")
    st.markdown("### 🎯 Quick Navigation")

    jump_to = st.number_input(
        "Jump to question:",
        min_value=1,
        max_value=len(df),
        value=st.session_state.index + 1,
        step=1,
        key="jump_to_input"
    )

    st.markdown("---")
    
    # Keyboard shortcuts info
    with st.expander("⌨️ Keyboard Shortcuts"):
        st.markdown("""
        - **Alt + ←**: Previous Question
        - **Alt + →**: Next Question
        - **Alt + S**: Save Review
        - **Alt + 1-5**: Quick Rating
        """)

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

# -------------------------
# Save function (defined after sidebar)
# -------------------------
def save_review():
    """Save current rating and remark for current index to OUTPUT_FILE."""
    # Get current values from session state
    reviewer_name = st.session_state.get('reviewer_name_input', '')
    reviewer_type = st.session_state.get('reviewer_type_input', 'Select Type')
    
    # Validate reviewer info
    if not reviewer_name or reviewer_type == "Select Type":
        st.error("⚠️ Please enter your name and select reviewer type in the sidebar!")
        return False

    # Get rating and remark
    rating_key = f"rating_{st.session_state.index}_{st.session_state.rating_counter}"
    remark_key = f"remark_{st.session_state.index}_{st.session_state.remark_counter}"
    
    rating = st.session_state.get(rating_key, None)
    remark = st.session_state.get(remark_key, "")
    
    has_rating = rating is not None and str(rating).strip() != ""
    has_remark = remark is not None and str(remark).strip() != ""

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

        # Expand df_out if needed
        if len(df_out) < len(df):
            extra = pd.DataFrame([[""] * len(df_out.columns)] * (len(df) - len(df_out)), columns=df_out.columns)
            df_out = pd.concat([df_out, extra], ignore_index=True)

        # Save rating if present
        rating_options = {
            "⭐⭐⭐⭐⭐ Excellent": 5,
            "⭐⭐⭐⭐ Good": 4,
            "⭐⭐⭐ Fair": 3,
            "⭐⭐ Poor": 2,
            "⭐ Very Poor": 1
        }
        
        if has_rating:
            df_out.at[st.session_state.index, 'Rating'] = rating
            df_out.at[st.session_state.index, 'Rating_Value'] = rating_options.get(rating, "")

        # Save remark
        if has_remark:
            df_out.at[st.session_state.index, 'Remarks'] = remark

        # Save metadata
        save_time = datetime.now(bd_tz).strftime("%Y-%m-%d %I:%M:%S %p")
        df_out.at[st.session_state.index, 'Reviewer'] = reviewer_name
        df_out.at[st.session_state.index, 'Reviewer_Type'] = reviewer_type
        df_out.at[st.session_state.index, 'Review_Date'] = save_time

        # Write out
        df_out.to_csv(OUTPUT_FILE, index=False)
        st.session_state._df_saved = df_out
        
        return True
    except Exception as e:
        st.error(f"Error saving review: {e}")
        return False

# Register the save function
st.session_state.save_review_fn = save_review

# -------------------------
# Navigation helpers
# -------------------------
def navigate_to(new_index):
    """Navigate to a specific question index."""
    save_review()
    st.session_state.index = max(0, min(len(df) - 1, new_index))
    st.session_state.remark_counter += 1
    st.session_state.rating_counter += 1

# -------------------------
# Sidebar navigation buttons (continued)
# -------------------------
with st.sidebar:
    if st.button("🔄 Go to Question", use_container_width=True, key="jump_button"):
        navigate_to(int(jump_to) - 1)
    
    if st.button("🔁 Reset to First Question", use_container_width=True):
        navigate_to(0)
    
    # Bulk save button
    if st.button("💾 Save All Progress", use_container_width=True, type="primary"):
        if save_review():
            st.success("All progress saved!")

# -------------------------
# Progress bar & current row
# -------------------------
progress = (st.session_state.index + 1) / len(df)
st.progress(progress)

# Enhanced progress caption with percentage
progress_pct = int(progress * 100)
st.caption(f"📊 Progress: {st.session_state.index + 1} of {len(df)} questions ({progress_pct}%)")

# Safe bounds for index
if st.session_state.index < 0:
    st.session_state.index = 0
if st.session_state.index >= len(df):
    st.session_state.index = len(df) - 1

row = df.iloc[st.session_state.index]

# -------------------------
# Load existing rating/remark
# -------------------------
existing_rating = None
existing_remark = ""
if df_saved is not None and st.session_state.index < len(df_saved):
    if 'Rating' in df_saved.columns:
        saved_rating = df_saved.iloc[st.session_state.index].get('Rating', "")
        if pd.notna(saved_rating) and saved_rating != "":
            existing_rating = saved_rating
    if 'Remarks' in df_saved.columns:
        saved_remark = df_saved.iloc[st.session_state.index].get('Remarks', "")
        if pd.notna(saved_remark) and saved_remark != "":
            existing_remark = saved_remark

# -------------------------
# Top bar with metrics
# -------------------------
col1, col2, col3 = st.columns([2, 1, 1])
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

with col3:
    # Show if current question is already reviewed
    is_reviewed = False
    if df_saved is not None and st.session_state.index < len(df_saved):
        if 'Rating' in df_saved.columns or 'Remarks' in df_saved.columns:
            rating_val = df_saved.iloc[st.session_state.index].get('Rating', "")
            remark_val = df_saved.iloc[st.session_state.index].get('Remarks', "")
            if (pd.notna(rating_val) and str(rating_val).strip() != "") or \
               (pd.notna(remark_val) and str(remark_val).strip() != ""):
                is_reviewed = True
    
    if is_reviewed:
        st.metric("📌 Status", "Reviewed")
    else:
        st.metric("📌 Status", "Pending")

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
# Show Model & Gold answers side by side
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
# Quick save button
# -------------------------
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("💾 Quick Save (Alt+S)", use_container_width=True, type="primary"):
        if save_review():
            st.success("✅ Review saved!")

# -------------------------
# Navigation buttons
# -------------------------
st.markdown("---")
if st.session_state.index == len(df) - 1:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.index == 0), key="prev_final"):
            navigate_to(st.session_state.index - 1)
    with col2:
        if st.button("💾 Save & Finish", use_container_width=True, key="save_finish"):
            if save_review():
                st.balloons()
                st.success("✅ All reviews completed!")
    with col3:
        st.empty()
else:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.index == 0), key="prev_btn"):
            navigate_to(st.session_state.index - 1)
   
    with col3:
        if st.button("Next ➡️", use_container_width=True, key="next_btn"):
            navigate_to(st.session_state.index + 1)

# -------------------------
# Download and statistics section
# -------------------------
st.markdown("---")
st.markdown("### 📊 Review Summary & Export")

col1, col2 = st.columns([2, 1])

# Statistics in expandable section
with col1:
    df_to_stats = st.session_state.get('_df_saved', df_saved)
    if df_to_stats is not None:
        with st.expander("📈 Detailed Statistics", expanded=False):
            # Rating statistics
            if 'Rating_Value' in df_to_stats.columns:
                ratings = pd.to_numeric(df_to_stats['Rating_Value'], errors='coerce').dropna()
                if len(ratings) > 0:
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Average Rating", f"{ratings.mean():.2f} ⭐")
                    with col_b:
                        st.metric("Total Rated", len(ratings))
                    with col_c:
                        st.metric("Completion", f"{int(len(ratings)/len(df)*100)}%")
                    
                    st.markdown("**Rating Distribution:**")
                    rating_dist = df_to_stats['Rating'].value_counts()
                    for rating_label, count in rating_dist.items():
                        if pd.notna(rating_label) and rating_label != "":
                            pct = int(count / len(df) * 100)
                            st.write(f"- {rating_label}: {count} ({pct}%)")

            # Reviewer statistics
            if 'Reviewer_Type' in df_to_stats.columns:
                st.markdown("---")
                st.markdown("**Reviews by Reviewer Type:**")
                reviewer_types = df_to_stats['Reviewer_Type'].value_counts()
                for rtype, count in reviewer_types.items():
                    if pd.notna(rtype) and rtype != "" and rtype != "Select Type":
                        st.write(f"- {rtype}: {count}")

# Download button
with col2:
    if os.path.exists(OUTPUT_FILE):
        try:
            df_download = pd.read_csv(OUTPUT_FILE)
            csv = df_download.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Reviews CSV",
                data=csv,
                file_name=f"qa_review_{datetime.now(bd_tz).strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        st.info("💡 No reviews saved yet. Start reviewing to enable download!")

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🧠 QA Review Interface | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)
