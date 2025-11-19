import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# Page configuration
st.set_page_config(
    page_title="QA Review Interface", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
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
    }
    
    .main-header p {
        position: relative;
        z-index: 1;
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
    
    .rating-container {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e0e7ff;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
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

# Header Section
st.markdown("""
    <div class="main-header">
        <h1>🧠 QA Review Interface</h1>
        <p style='font-size: 1.1rem; margin: 0;'>✨ Evaluate model responses against gold standard answers with style</p>
    </div>
""", unsafe_allow_html=True)

# Set timezone to Bangladesh
bd_tz = pytz.timezone('Asia/Dhaka')

# Define file paths
OUTPUT_FILE = "qa_dataset_with_remarks.csv"
INPUT_FILE = "qa_dataset - Sheet1.csv"

# Validate and load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(INPUT_FILE)
        required_cols = ['Question', 'Answer', 'Gold Answer']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            st.error(f"❌ Missing required columns: {', '.join(missing)}")
            st.stop()
        return df
    except FileNotFoundError:
        st.error(f"❌ Input file not found: {INPUT_FILE}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

df = load_data()

# Load existing reviews
def load_existing_reviews():
    if os.path.exists(OUTPUT_FILE):
        try:
            return pd.read_csv(OUTPUT_FILE)
        except:
            return None
    return None

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Review Settings")
    reviewer_name = st.text_input("👤 Reviewer Name:", placeholder="Enter your name")
    
    # Reviewer Type Selection
    reviewer_type = st.selectbox(
        "👥 Reviewer Type:",
        options=["Select Type", "Tax Payer", "Non Tax Payer", "Tax Officer"],
        index=0
    )
    
    current_time = datetime.now(bd_tz).strftime("%Y-%m-%d %I:%M:%S %p")
    st.info(f"📅 {current_time}")
    
    st.markdown("---")
    
    # Jump to question feature
    st.markdown("### 🎯 Quick Navigation")
    jump_to = st.number_input(
        "Jump to question:",
        min_value=1,
        max_value=len(df),
        value=st.session_state.get('index', 0) + 1,
        step=1
    )
    if st.button("Go", use_container_width=True):
        st.session_state.index = jump_to - 1
        st.session_state.remark_counter += 1
        st.session_state.rating_counter += 1
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 Instructions")
    st.markdown("""
    1. 📖 Read the question carefully
    2. 🔍 Compare Model Answer with Gold Answer
    3. ⭐ Rate the model's answer
    4. ✍️ Add your remarks
    5. ⬅️➡️ Navigate using Previous/Next
    6. 💾 Everything is auto-saved!
    """)
    
    st.markdown("---")
    st.markdown("### ⭐ Rating Guide")
    st.markdown("""
    - **Excellent**: Perfect answer
    - **Good**: Minor issues
    - **Fair**: Some problems
    - **Poor**: Major issues
    - **Very Poor**: Completely wrong
    """)

# Initialize session state
if "index" not in st.session_state:
    st.session_state.index = 0

if "remark_counter" not in st.session_state:
    st.session_state.remark_counter = 0

if "rating_counter" not in st.session_state:
    st.session_state.rating_counter = 0

# Progress bar
progress = (st.session_state.index + 1) / len(df)
st.progress(progress)
st.caption(f"📊 Progress: {st.session_state.index + 1} of {len(df)} questions")

# Question Display
row = df.iloc[st.session_state.index]

# Load existing review for current question
df_saved = load_existing_reviews()
existing_rating = None
existing_rating_key = None
existing_remark = ""

if df_saved is not None and st.session_state.index < len(df_saved):
    if 'Rating' in df_saved.columns:
        saved_rating = df_saved.iloc[st.session_state.index]['Rating']
        if pd.notna(saved_rating) and saved_rating != "":
            existing_rating = saved_rating
    if 'Remarks' in df_saved.columns:
        saved_remark = df_saved.iloc[st.session_state.index]['Remarks']
        if pd.notna(saved_remark):
            existing_remark = saved_remark

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"### 📝 Question {st.session_state.index + 1}")
with col2:
    # Count how many questions have been reviewed (have either rating or remark)
    reviewed_count = 0
    if df_saved is not None:
        for i in range(len(df)):
            has_rating = False
            has_remark = False
            
            if i < len(df_saved):
                if 'Rating' in df_saved.columns:
                    rating_val = df_saved.iloc[i]['Rating']
                    has_rating = pd.notna(rating_val) and str(rating_val).strip() != ""
                
                if 'Remarks' in df_saved.columns:
                    remark_val = df_saved.iloc[i]['Remarks']
                    has_remark = pd.notna(remark_val) and str(remark_val).strip() != ""
            
            if has_rating or has_remark:
                reviewed_count += 1
    
    st.metric("✅ Reviewed", f"{reviewed_count}/{len(df)}")

# Question Card
st.markdown(f"""
    <div class="question-card">
        <p><strong>❓ Question:</strong></p>
        <p style="margin-top: 0.8rem; font-size: 1.05rem; color: #2d3748;">{row['Question']}</p>
    </div>
""", unsafe_allow_html=True)

# Answers
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🤖 Model Answer")
    st.info(row['Answer'])

with col2:
    st.markdown("#### ✅ Gold Answer")
    st.success(row['Gold Answer'])

# Rating Section
st.markdown("---")
st.markdown("### ⭐ Rate the Model Answer")

# Rating options with emojis
rating_options = {
    "⭐⭐⭐⭐⭐ Excellent": 5,
    "⭐⭐⭐⭐ Good": 4,
    "⭐⭐⭐ Fair": 3,
    "⭐⭐ Poor": 2,
    "⭐ Very Poor": 1
}

# Set default index based on existing rating
default_index = None
if existing_rating:
    rating_keys = list(rating_options.keys())
    if existing_rating in rating_keys:
        default_index = rating_keys.index(existing_rating)

rating = st.radio(
    "Select a rating:",
    options=list(rating_options.keys()),
    index=default_index,
    key=f"rating_{st.session_state.index}_{st.session_state.rating_counter}",
    horizontal=True
)

# Remarks section
st.markdown("---")
st.markdown("### 💭 Your Remarks")

remark = st.text_area(
    "Add your evaluation remarks here:",
    value=existing_remark,
    height=150,
    key=f"remark_{st.session_state.index}_{st.session_state.remark_counter}",
    placeholder="✍️ Write your observations, corrections, or comments..."
)

def save_review():
    """Save the current rating and remark to CSV"""
    has_rating = rating is not None
    has_remark = remark.strip() != ""
    
    if has_rating or has_remark:
        try:
            if os.path.exists(OUTPUT_FILE):
                df_saved = pd.read_csv(OUTPUT_FILE)
            else:
                df_saved = df.copy()
                df_saved['Rating'] = ""
                df_saved['Rating_Value'] = ""
                df_saved['Remarks'] = ""
                df_saved['Reviewer'] = ""
                df_saved['Reviewer_Type'] = ""
                df_saved['Review_Date'] = ""
            
            # Ensure all columns exist
            for col in ['Rating', 'Rating_Value', 'Remarks', 'Reviewer', 'Reviewer_Type', 'Review_Date']:
                if col not in df_saved.columns:
                    df_saved[col] = ""
            
            save_time = datetime.now(bd_tz).strftime("%Y-%m-%d %I:%M:%S %p")
            
            # Save rating
            if has_rating:
                df_saved.at[st.session_state.index, 'Rating'] = rating
                df_saved.at[st.session_state.index, 'Rating_Value'] = rating_options[rating]
            
            # Save remark
            if has_remark:
                df_saved.at[st.session_state.index, 'Remarks'] = remark
            
            # Save metadata
            df_saved.at[st.session_state.index, 'Reviewer'] = reviewer_name if reviewer_name else "Anonymous"
            df_saved.at[st.session_state.index, 'Reviewer_Type'] = reviewer_type if reviewer_type != "Select Type" else ""
            df_saved.at[st.session_state.index, 'Review_Date'] = save_time
            
            df_saved.to_csv(OUTPUT_FILE, index=False)
            return True
        except Exception as e:
            st.error(f"Error saving: {e}")
            return False
    return False

def save_and_navigate(direction):
    save_review()
    st.session_state.remark_counter += 1
    st.session_state.rating_counter += 1
    
    if direction == "prev":
        st.session_state.index = max(0, st.session_state.index - 1)
    elif direction == "next":
        st.session_state.index = min(len(df) - 1, st.session_state.index + 1)

# Navigation buttons
st.markdown("---")

if st.session_state.index == len(df) - 1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⬅️ Previous", use_container_width=True):
            save_and_navigate("prev")
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Finish", use_container_width=True, type="primary"):
            if save_review():
                st.session_state.remark_counter += 1
                st.session_state.rating_counter += 1
                st.success("✅ Review saved successfully!")
                st.rerun()
            else:
                st.warning("⚠️ No rating or remark to save")
else:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.index == 0)):
            save_and_navigate("prev")
            st.rerun()
    
    with col2:
        if st.button("Next ➡️", use_container_width=True):
            save_and_navigate("next")
            st.rerun()

# Download section
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

# Show review statistics
if df_saved is not None:
    with col1:
        with st.expander("📊 Review Statistics"):
            if 'Rating_Value' in df_saved.columns:
                ratings = df_saved['Rating_Value'].dropna()
                if len(ratings) > 0:
                    ratings_numeric = pd.to_numeric(ratings, errors='coerce').dropna()
                    if len(ratings_numeric) > 0:
                        avg_rating = ratings_numeric.mean()
                        st.metric("Average Rating", f"{avg_rating:.2f} ⭐")
                        
                        rating_dist = df_saved['Rating'].value_counts()
                        st.write("**Rating Distribution:**")
                        for rating_label, count in rating_dist.items():
                            if pd.notna(rating_label) and rating_label != "":
                                st.write(f"- {rating_label}: {count}")
