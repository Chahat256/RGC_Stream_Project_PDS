"""
RGC Stream - Web Series Management System
Complete conversion from Flask to Streamlit for CS-GY 6083 Project Part II
Integrates with CGR database schema from Part I

Team: RGC
- Chahat Kothari (ck3999)
- Greeshma Hedvikar (gh2461)
- Rujuta Joshi (rj2719)
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from contextlib import contextmanager
import time
import os

import base64

def load_image_base64(image_path):
    """Load local image and convert to base64 string for HTML embedding."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="RGC Stream - Web Series Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - MODERN PROFESSIONAL DARK THEME
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
    
    * { margin: 0; padding: 0; }
    
    /* Modern color scheme */
    :root {
        --primary: #0099ff;
        --secondary: #3895d3;
        --accent: #9933ff;
        --bg-dark: #070d1a;
        --bg-card: #0f1f35;
        --bg-light: #151f2f;
        --text-primary: #f0f4f9;
        --text-secondary: #b0b8c5;
        --border: #1a2a45;
        --success: #00d9a3;
        --warning: #ffa726;
    }
    
    html, body {
        background-color: var(--bg-dark);
        color: var(--text-primary);
    }
    
    .main {
        background: linear-gradient(135deg, var(--bg-dark) 0%, #0a1520 100%);
        color: var(--text-primary);
    }
    
    h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: var(--text-primary);
        letter-spacing: -0.5px;
        margin-bottom: 1rem;
    }
    
    h2 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
        color: var(--text-primary);
        margin-bottom: 0.8rem;
    }
    
    h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.2rem;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    p, div, span, label {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        font-weight: 400;
    }
    
    /* Logo Styling */
    .streamvault-logo {
        font-family: 'Poppins', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 50%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
        text-align: center;
        margin: 2rem 0;
        filter: drop-shadow(0 10px 30px rgba(0, 153, 255, 0.2));
    }
    
    /* Carousel Styles */
    .carousel-container {
        position: relative;
        padding-top:25px;
        width: 100%;
        height: 460px;
        overflow: hidden;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), 
        border: 1px solid var(--border);
    }
    
    .carousel-track {
        display: flex;
        animation: scroll 50s linear infinite;
        width: fit-content;
    }
    
    .carousel-item {
        min-width: 280px;
        height: 420px;
        margin: 0 10px;
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(135deg, var(--bg-light) 0%, var(--bg-card) 100%);
        border: 1px solid var(--border);
    }
    
    .carousel-item:hover {
        transform: translateY(-12px) scale(1.05);
        box-shadow: 0 25px 50px rgba(0, 153, 255, 0.3);
        border-color: var(--accent);
    }
    
    .carousel-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.6s ease;
    }
    
    .carousel-item:hover img {
        transform: scale(1.1);
    }
    
    .carousel-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, transparent 0%, rgba(7, 13, 26, 0.95) 60%, rgba(7, 13, 26, 0.99) 100%);
        padding: 20px;
        color: white;
    }
    
    .carousel-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 8px 0;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
    }
    
    @keyframes scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    
    /* Series Card */
    .series-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-light) 100%);
        border-radius: 14px;
        padding: 1.6rem;
        margin: 1.2rem 0;
        border: 1px solid var(--border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .series-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0, 153, 255, 0.2), 
                    0 0 30px rgba(153, 51, 255, 0.15);
        border-color: var(--accent);
        background: linear-gradient(135deg, var(--bg-light) 0%, var(--bg-card) 100%);
    }
    
    /* Metrics */
    .stMetric {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-light) 100%) !important;
        padding: 1.4rem !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        border-color: var(--secondary) !important;
        box-shadow: 0 8px 25px rgba(0, 153, 255, 0.15) !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: var(--bg-dark) !important;
        border: none !important;
        padding: 0.7rem 2.2rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(0, 153, 255, 0.25) !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, var(--accent) 0%, var(--primary) 100%) !important;
        color: white !important;
        box-shadow: 0 10px 35px rgba(0, 153, 255, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: var(--bg-light) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        padding: 0.7rem 1rem !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(0, 153, 255, 0.1) !important;
        background-color: var(--bg-card) !important;
    }
    
    /* Dataframe */
    .dataframe {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    
    /* Language Badges */
    .language-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.3rem 0.2rem;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0, 153, 255, 0.2);
    }
    
    .language-badge.dubbing {
        background: linear-gradient(135deg, var(--accent) 0%, #6b3cc9 100%);
    }
    
    /* Settings Card */
    .settings-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-light) 100%);
        border-radius: 14px;
        padding: 1.6rem;
        margin: 1.5rem 0;
        border: 1px solid var(--border);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        padding: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--bg-light) !important;
        padding: 0.6rem 1.4rem !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
        border-color: var(--primary) !important;
        box-shadow: 0 6px 20px rgba(0, 153, 255, 0.3) !important;
    }
    
    /* Forms & Expanders */
    .stExpander {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        background: var(--bg-card) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-dark) 0%, var(--bg-card) 100%);
    }
    
    [data-testid="stSidebar"] > div > div > div {
        background: transparent;
    }
    
    /* Radio Buttons */
    .stRadio [role="radiogroup"] {
        gap: 1rem;
    }
    
    .stRadio > label {
        font-weight: 500 !important;
        color: var(--text-primary) !important;
    }
    
    /* Divider */
    hr {
        border: 1px solid var(--border) !important;
        margin: 2rem 0 !important;
    }
    
    /* Billing Card */
    .billing-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-light) 100%);
        border-left: 4px solid var(--primary);
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    
    .billing-card:hover {
        border-left-color: var(--accent);
        box-shadow: 0 6px 20px rgba(0, 153, 255, 0.15);
        transform: translateX(4px);
    }
    
    .billing-card.upcoming {
        border-left-color: var(--warning);
    }
    
    .billing-card.paid {
        border-left-color: var(--success);
    }
    
    /* Error, Warning, Info, Success messages */
    .stAlert {
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--bg-light) !important;
        padding: 1.2rem !important;
    }
    
    [data-testid="stAlert"] {
        background-color: var(--bg-light) !important;
    }
    
    /* Markdown text improvements */
    .stMarkdown {
        line-height: 1.6;
    }
    
    .stMarkdown strong {
        color: var(--primary);
        font-weight: 600;
    }
    
    /* Links */
    a {
        color: var(--primary) !important;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    a:hover {
        color: var(--secondary) !important;
        text-decoration: underline;
    }
    
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CAROUSEL DATA - Top 10 Series with Poster URLs
# ============================================================================
CAROUSEL_SERIES = [
{"name": "Stranger Things", "image": "https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/479dc087874857.62b25a3de4723.jpg", "rating": "4.8"},
{"name": "Money Heist", "image": "https://c7.alamy.com/comp/2BERHY0/poster-money-heist-part-4-2020-credit-netflix-the-hollywood-archive-2BERHY0.jpg", "rating": "4.7"},
{"name": "Sacred Games", "image": "https://m.media-amazon.com/images/I/615QP26qFeL._AC_SL1500_.jpg", "rating": "4.6"},
{"name": "Dark", "image": "https://m.media-amazon.com/images/I/A11DlZLBe7S._AC_SL1500_.jpg", "rating": "4.9"},
{"name": "The Witcher", "image": "https://m.media-amazon.com/images/M/MV5BMDEwOWVlY2EtMWI0ZC00OWVmLWJmZGItYTk3YjYzN2Y0YmFkXkEyXkFqcGdeQXVyMTUzMTg2ODkz._V1_FMjpg_UX1000_.jpg", "rating": "4.5"},
{"name": "Breaking Bad", "image": "https://m.media-amazon.com/images/M/MV5BYmQ4YWMxYjUtNjZmYi00MDQ1LWFjMjMtNjA5ZDdiYjdiODU5XkEyXkFqcGdeQXVyMTMzNDExODE5._V1_FMjpg_UX1000_.jpg", "rating": "5.0"},
{"name": "Squid Game", "image": "https://m.media-amazon.com/images/M/MV5BYWE3MDVkN2EtNjQ5MS00ZDQ4LTliNzYtMjc2YWMzMDEwMTA3XkEyXkFqcGdeQXVyMTEzMTI1Mjk3._V1_FMjpg_UX1000_.jpg", "rating": "4.8"},
{"name": "The Crown", "image": "https://images.squarespace-cdn.com/content/v1/670d2df8bf4f7719f5f20d98/145a5f2b-4c78-4957-a299-6ddd19920e83/Crowns5.jpg", "rating": "4.6"},
{"name": "Narcos", "image": "https://c7.alamy.com/comp/PMAG6N/wagner-moura-stars-in-narcos-poster-PMAG6N.jpg", "rating": "4.7"},
{"name": "Attack on Titan", "image": "https://m.media-amazon.com/images/I/61t9ie31jgL._AC_SL1001_.jpg", "rating": "4.9"},
]
\

# ============================================================================
# DATABASE CONFIGURATION & CONNECTION
# ============================================================================
@st.cache_resource
def get_database_connection():
    """
    Create database connection with security best practices
    IMPORTANT: Update credentials below before running
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='RGC',
            user='', # UPDATE THIS
            password='',  # UPDATE THIS
            port=3306,
            autocommit=False
        )
        return connection
    except Error as e:
        st.error(f"❌ Database Connection Error: {e}")
        st.info("💡 Please update database credentials in code (lines 121-126)")
        return None

# ============================================================================
# SECURITY FUNCTIONS
# ============================================================================
#password hashing
def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = "streamvault_salt_2025"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

#second layer of defense against sql injections
def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return text
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()

def execute_query(query, params=None, fetch=True, commit=False):
    """Execute query with prepared statements to prevent SQL injection"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if commit:
            conn.commit()
            result = cursor.rowcount
        elif fetch:
            result = cursor.fetchall()
        else:
            result = True
            
        cursor.close()
        return result
    except Error as e:
        if conn:
            conn.rollback()
        st.error(f"Database Error: {e}")
        return None

# concurrency example with transaction management
@contextmanager
def transaction():
    """Transaction context manager with automatic rollback"""
    conn = get_database_connection()
    if not conn:
        yield None
        return
        
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        yield cursor
        conn.commit()
    except Error as e:
        conn.rollback()
        st.error(f"Transaction Error: {e}")
        raise
    finally:
        cursor.close()

# ============================================================================
# USER MANAGEMENT & AUTHENTICATION
# ============================================================================
def create_users_table():
    """Create users table if it doesn't exist"""
    query = """
    CREATE TABLE IF NOT EXISTS RGC_USERS (
        USER_ID VARCHAR(30) PRIMARY KEY,
        USERNAME VARCHAR(50) UNIQUE NOT NULL,
        PASSWORD_HASH VARCHAR(64) NOT NULL,
        USER_TYPE ENUM('VIEWER', 'PRODUCER', 'ADMIN') NOT NULL,
        EMAIL VARCHAR(100) NOT NULL,
        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        LINKED_ACCOUNT VARCHAR(30),
        INDEX idx_username (USERNAME)
    )
    """
    execute_query(query, commit=True)

def register_user(username, password, email, user_type, linked=None):
    """Register new user with encrypted password"""
    username = sanitize_input(username)
    email = sanitize_input(email)
    
    user_id = f"U{datetime.now().strftime('%Y%m%d%H%M%S')}"
    pwd_hash = hash_password(password)
    
    query = """
    INSERT INTO RGC_USERS (USER_ID, USERNAME, PASSWORD_HASH, USER_TYPE, EMAIL, LINKED_ACCOUNT)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (user_id, username, pwd_hash, user_type, email, linked), commit=True)

def authenticate_user(username, password):
    """Authenticate user with hashed password comparison"""
    username = sanitize_input(username)
    pwd_hash = hash_password(password)
    
    query = """
    SELECT USER_ID, USERNAME, USER_TYPE, LINKED_ACCOUNT, EMAIL
    FROM RGC_USERS
    WHERE USERNAME = %s AND PASSWORD_HASH = %s
    """
    result = execute_query(query, (username, pwd_hash))
    return result[0] if result else None

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'linked_account' not in st.session_state:
    st.session_state.linked_account = None

create_users_table()

# ============================================================================
# AUTHENTICATION PAGE
# ============================================================================
def show_auth():
    """Login and Registration page"""
    # Centered layout with spacing
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="streamvault-logo">🎬 RGC STREAM</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.1rem; color: var(--text-secondary); font-weight: 500; margin-top: -1rem;">Premium Web Series Platform</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 2rem;">Experience unlimited entertainment</p>', unsafe_allow_html=True)
    
    st.markdown("")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Sign In to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user['USER_ID']
                        st.session_state.username = user['USERNAME']
                        st.session_state.user_type = user['USER_TYPE']
                        st.session_state.linked_account = user['LINKED_ACCOUNT']
                        st.success(f"✅ Welcome, {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.warning("⚠️ Please fill in all fields")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                reg_user = st.text_input("Username", key="r1")
                reg_email = st.text_input("Email", key="r2")
            with col2:
                reg_pass = st.text_input("Password", type="password", key="r3")
                reg_pass2 = st.text_input("Confirm Password", type="password", key="r4")
            
                # reg_type = st.selectbox("Account Type", ["VIEWER", "PRODUCER", "ADMIN"])
            reg_type = "VIEWER"  # Default to VIEWER for simplicity            
            linked = None
            if reg_type == "VIEWER":
                accounts = execute_query("SELECT ACCOUNT_ID, ACC_FNAME, ACC_LNAME FROM RGC_VIEWER LIMIT 20")
                if accounts:
                    acc_opts = ["None"] + [f"{a['ACCOUNT_ID']} - {a['ACC_FNAME']} {a.get('ACC_LNAME', '')}" for a in accounts]
                    selected = st.selectbox("Link to Viewer Account (Optional)", acc_opts)
                    if selected != "None":
                        linked = selected.split(' - ')[0]
            

            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if not reg_user or not reg_email or not reg_pass:
                    st.warning("⚠️ Please fill in all fields")
                elif reg_pass != reg_pass2:
                    st.error("❌ Passwords don't match")
                elif len(reg_pass) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    if register_user(reg_user, reg_pass, reg_email, reg_type, linked):
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error("❌ Registration failed. Username may already exist.")

# ============================================================================
# CONTRACT MANAGEMENT FUNCTIONS - CORRECTED
# ============================================================================
def create_contract_table():
    """Create contracts table if it doesn't exist"""
    query = """
    CREATE TABLE IF NOT EXISTS RGC_CONTRACTS (
        CONTRACT_ID VARCHAR(30) PRIMARY KEY,
        SERIES_ID VARCHAR(10),
        HOUSE_ID VARCHAR(10),
        CONTRACT_TYPE ENUM('PRODUCTION', 'DISTRIBUTION', 'LICENSING', 'TALENT') NOT NULL,
        CONTRACT_VALUE DECIMAL(15, 2),
        START_DATE DATE NOT NULL,
        END_DATE DATE,
        STATUS ENUM('ACTIVE', 'PENDING', 'EXPIRED', 'TERMINATED') DEFAULT 'PENDING',
        PAYMENT_TERMS TEXT,
        MILESTONE_DETAILS JSON,
        CREATED_BY VARCHAR(30),
        CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (SERIES_ID) REFERENCES RGC_WEB_SERIES(SERIES_ID) ON DELETE CASCADE,
        FOREIGN KEY (HOUSE_ID) REFERENCES RGC_PRODUCTION_HOUSE(HOUSE_ID),
        INDEX idx_series (SERIES_ID),
        INDEX idx_house (HOUSE_ID),
        INDEX idx_status (STATUS)
    )
    """
    execute_query(query, commit=True)

def create_payment_table():
    """Create payments table for contract tracking"""
    query = """
    CREATE TABLE IF NOT EXISTS RGC_CONTRACT_PAYMENTS (
        PAYMENT_ID VARCHAR(30) PRIMARY KEY,
        CONTRACT_ID VARCHAR(30),
        PAYMENT_DATE DATE,
        AMOUNT DECIMAL(15, 2),
        PAYMENT_STATUS ENUM('PENDING', 'COMPLETED', 'OVERDUE', 'CANCELLED') DEFAULT 'PENDING',
        PAYMENT_METHOD VARCHAR(50),
        NOTES TEXT,
        FOREIGN KEY (CONTRACT_ID) REFERENCES RGC_CONTRACTS(CONTRACT_ID) ON DELETE CASCADE,
        INDEX idx_contract (CONTRACT_ID),
        INDEX idx_status (PAYMENT_STATUS)
    )
    """
    execute_query(query, commit=True)

def get_contract_analytics(house_id=None):
    """Get contract analytics for dashboard"""
    base_query = """
        SELECT 
            COUNT(*) as total_contracts,
            SUM(CASE WHEN STATUS = 'ACTIVE' THEN 1 ELSE 0 END) as active_contracts,
            SUM(CASE WHEN STATUS = 'PENDING' THEN 1 ELSE 0 END) as pending_contracts,
            SUM(CASE WHEN STATUS = 'EXPIRED' THEN 1 ELSE 0 END) as expired_contracts,
            SUM(IFNULL(CONTRACT_VALUE, 0)) as total_value,
            SUM(CASE WHEN STATUS = 'ACTIVE' THEN IFNULL(CONTRACT_VALUE, 0) ELSE 0 END) as active_value
        FROM RGC_CONTRACTS
    """
    
    if house_id:
        base_query += " WHERE HOUSE_ID = %s"
        return execute_query(base_query, (house_id,))
    return execute_query(base_query)

# ============================================================================
# ASSOCIATION MANAGEMENT (CAST & CREW)
# ============================================================================
def create_association_table():
    """Create cast and crew association table"""
    query = """
    CREATE TABLE IF NOT EXISTS RGC_CAST_CREW (
        ASSOCIATION_ID VARCHAR(30) PRIMARY KEY,
        SERIES_ID VARCHAR(30),
        PERSON_NAME VARCHAR(100) NOT NULL,
        ROLE_TYPE ENUM('ACTOR', 'DIRECTOR', 'WRITER', 'PRODUCER', 'CINEMATOGRAPHER', 'EDITOR', 'OTHER') NOT NULL,
        CHARACTER_NAME VARCHAR(100),
        ROLE_DESCRIPTION TEXT,
        START_DATE DATE,
        END_DATE DATE,
        COMPENSATION DECIMAL(15, 2),
        STATUS ENUM('ACTIVE', 'COMPLETED', 'TERMINATED') DEFAULT 'ACTIVE',
        FOREIGN KEY (SERIES_ID) REFERENCES RGC_WEB_SERIES(SERIES_ID) ON DELETE CASCADE,
        INDEX idx_series (SERIES_ID),
        INDEX idx_person (PERSON_NAME)
    )
    """
    execute_query(query, commit=True)

def show_associations():
    """Manage cast and crew associations"""
    st.title("🎭 Cast & Crew Management")
    
    create_association_table()
    
    tab1, tab2 = st.tabs(["📋 View Associations", "➕ Add Association"])
    
    with tab1:
        st.subheader("Cast & Crew List")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            series_opts = execute_query("SELECT SERIES_ID, SERIES_NAME FROM RGC_WEB_SERIES ORDER BY SERIES_NAME")
            series_names = ["All Series"] + [s['SERIES_NAME'] for s in series_opts] if series_opts else ["All Series"]
            series_filter = st.selectbox("Filter by Series", series_names)
        
        with col2:
            role_filter = st.selectbox("Filter by Role", 
                                      ["All Roles", "ACTOR", "DIRECTOR", "WRITER", "PRODUCER", 
                                       "CINEMATOGRAPHER", "EDITOR", "OTHER"])
        
        # Query associations
        base_query = """
            SELECT a.*, ws.SERIES_NAME
            FROM RGC_CAST_CREW a
            JOIN RGC_WEB_SERIES ws ON a.SERIES_ID = ws.SERIES_ID
        """
        
        where_clauses = []
        params = []
        
        if series_filter != "All Series":
            where_clauses.append("ws.SERIES_NAME = %s")
            params.append(series_filter)
        
        if role_filter != "All Roles":
            where_clauses.append("a.ROLE_TYPE = %s")
            params.append(role_filter)
        
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
        
        base_query += " ORDER BY ws.SERIES_NAME, a.ROLE_TYPE, a.PERSON_NAME"
        
        associations = execute_query(base_query, tuple(params) if params else None)
        
        if associations:
            st.write(f"**Found {len(associations)} associations**")
            
            for assoc in associations:
                role_emoji = {
                    'ACTOR': '🎭',
                    'DIRECTOR': '🎬',
                    'WRITER': '✍️',
                    'PRODUCER': '🎥',
                    'CINEMATOGRAPHER': '📷',
                    'EDITOR': '✂️',
                    'OTHER': '👤'
                }.get(assoc['ROLE_TYPE'], '👤')
                
                status_color = {
                    'ACTIVE': '🟢',
                    'COMPLETED': '🔵',
                    'TERMINATED': '🔴'
                }.get(assoc['STATUS'], '⚪')
                
                with st.expander(f"{role_emoji} {assoc['PERSON_NAME']} - {assoc['ROLE_TYPE']} - {assoc['SERIES_NAME']} {status_color}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Association ID:** {assoc['ASSOCIATION_ID']}")
                        st.write(f"**Series:** {assoc['SERIES_NAME']}")
                        st.write(f"**Role:** {assoc['ROLE_TYPE']}")
                        if assoc['CHARACTER_NAME']:
                            st.write(f"**Character:** {assoc['CHARACTER_NAME']}")
                        st.write(f"**Status:** {assoc['STATUS']}")
                    
                    with col2:
                        st.write(f"**Start Date:** {assoc['START_DATE'] or 'N/A'}")
                        st.write(f"**End Date:** {assoc['END_DATE'] or 'Ongoing'}")
                        if assoc['COMPENSATION']:
                            st.write(f"**Compensation:** ${assoc['COMPENSATION']:,.2f}")
                        if assoc['ROLE_DESCRIPTION']:
                            st.write(f"**Description:** {assoc['ROLE_DESCRIPTION']}")
                    
                    # Actions
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if st.button("🗑️ Remove", key=f"del_assoc_{assoc['ASSOCIATION_ID']}"):
                            if execute_query("DELETE FROM RGC_CAST_CREW WHERE ASSOCIATION_ID = %s", 
                                           (assoc['ASSOCIATION_ID'],), commit=True):
                                st.success("✅ Association removed!")
                                time.sleep(1)
                                st.rerun()
                    
                    with act_col2:
                        if assoc['STATUS'] == 'ACTIVE' and st.button("✅ Mark Complete", key=f"complete_{assoc['ASSOCIATION_ID']}"):
                            if execute_query("UPDATE RGC_CAST_CREW SET STATUS = 'COMPLETED' WHERE ASSOCIATION_ID = %s",
                                           (assoc['ASSOCIATION_ID'],), commit=True):
                                st.success("✅ Status updated!")
                                time.sleep(1)
                                st.rerun()
        else:
            st.info("No associations found")
    
    with tab2:
        st.subheader("Add New Association")
        
        with st.form("add_association"):
            col1, col2 = st.columns(2)
            
            with col1:
                assoc_id = st.text_input("Association ID", placeholder="ASSOC001")
                
                series_opts = execute_query("SELECT SERIES_ID, SERIES_NAME FROM RGC_WEB_SERIES ORDER BY SERIES_NAME")
                if series_opts:
                    series_dict = {s['SERIES_NAME']: s['SERIES_ID'] for s in series_opts}
                    selected_series = st.selectbox("Series", list(series_dict.keys()))
                    series_id = series_dict[selected_series]
                else:
                    st.error("No series available")
                    series_id = None
                
                person_name = st.text_input("Person Name")
                role_type = st.selectbox("Role Type", 
                                        ["ACTOR", "DIRECTOR", "WRITER", "PRODUCER", 
                                         "CINEMATOGRAPHER", "EDITOR", "OTHER"])
                character_name = st.text_input("Character Name (if applicable)")
            
            with col2:
                role_description = st.text_area("Role Description")
                start_date = st.date_input("Start Date", value=date.today())
                end_date = st.date_input("End Date (optional)", value=None)
                compensation = st.number_input("Compensation ($)", min_value=0.0, step=1000.0)
                status = st.selectbox("Status", ["ACTIVE", "COMPLETED", "TERMINATED"])
            
            if st.form_submit_button("Add Association", use_container_width=True):
                if assoc_id and series_id and person_name:
                    query = """
                    INSERT INTO RGC_CAST_CREW 
                    (ASSOCIATION_ID, SERIES_ID, PERSON_NAME, ROLE_TYPE, CHARACTER_NAME, 
                     ROLE_DESCRIPTION, START_DATE, END_DATE, COMPENSATION, STATUS)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    if execute_query(query, (assoc_id, series_id, person_name, role_type, 
                                           character_name or None, role_description or None,
                                           start_date, end_date, compensation, status), commit=True):
                        st.success("✅ Association added successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to add association")
                else:
                    st.warning("⚠️ Please fill in required fields")

# ============================================================================
# PRODUCER MANAGEMENT
# ============================================================================
def create_producer_table():
    """Create producers table"""
    query = """
    CREATE TABLE IF NOT EXISTS RGC_PRODUCERS (
        PRODUCER_ID VARCHAR(30) PRIMARY KEY,
        PRODUCER_NAME VARCHAR(100) NOT NULL,
        EMAIL VARCHAR(100),
        PHONE VARCHAR(20),
        COMPANY_NAME VARCHAR(100),
        ADDRESS TEXT,
        SPECIALIZATION VARCHAR(100),
        YEARS_EXPERIENCE INT,
        STATUS ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE',
        CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_name (PRODUCER_NAME)
    )
    """
    execute_query(query, commit=True)

def show_producers():
    """Manage producers"""
    st.title("🎥 Producer Management")
    
    create_producer_table()
    
    tab1, tab2 = st.tabs(["📋 Producer List", "➕ Add Producer"])
    
    with tab1:
        st.subheader("All Producers")
        
        producers = execute_query("""
            SELECT p.*,
                   COUNT(DISTINCT c.CONTRACT_ID) as contract_count,
                   SUM(c.CONTRACT_VALUE) as total_contract_value
            FROM RGC_PRODUCERS p
            LEFT JOIN RGC_PRODUCTION_HOUSE ph ON p.COMPANY_NAME = ph.HOUSE_NAME
            LEFT JOIN RGC_CONTRACTS c ON ph.HOUSE_ID = c.HOUSE_ID
            GROUP BY p.PRODUCER_ID
            ORDER BY p.PRODUCER_NAME
        """)
        
        if producers:
            for prod in producers:
                status_emoji = '🟢' if prod['STATUS'] == 'ACTIVE' else '🔴'
                
                with st.expander(f"{status_emoji} {prod['PRODUCER_NAME']} - {prod['COMPANY_NAME'] or 'Independent'}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Producer ID:** {prod['PRODUCER_ID']}")
                        st.write(f"**Email:** {prod['EMAIL'] or 'N/A'}")
                        st.write(f"**Phone:** {prod['PHONE'] or 'N/A'}")
                    
                    with col2:
                        st.write(f"**Company:** {prod['COMPANY_NAME'] or 'Independent'}")
                        st.write(f"**Specialization:** {prod['SPECIALIZATION'] or 'N/A'}")
                        st.write(f"**Experience:** {prod['YEARS_EXPERIENCE'] or 0} years")
                    
                    with col3:
                        st.metric("Contracts", prod['contract_count'] or 0)
                        st.metric("Total Value", f"${prod['total_contract_value'] or 0:,.2f}")
                        st.write(f"**Status:** {prod['STATUS']}")
                    
                    if prod['ADDRESS']:
                        st.write(f"**Address:** {prod['ADDRESS']}")
                    
                    # Actions
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if st.button("🗑️ Delete", key=f"del_prod_{prod['PRODUCER_ID']}"):
                            if execute_query("DELETE FROM RGC_PRODUCERS WHERE PRODUCER_ID = %s",
                                           (prod['PRODUCER_ID'],), commit=True):
                                st.success("✅ Producer deleted!")
                                time.sleep(1)
                                st.rerun()
                    
                    with act_col2:
                        new_status = 'INACTIVE' if prod['STATUS'] == 'ACTIVE' else 'ACTIVE'
                        if st.button(f"Toggle Status", key=f"toggle_{prod['PRODUCER_ID']}"):
                            if execute_query("UPDATE RGC_PRODUCERS SET STATUS = %s WHERE PRODUCER_ID = %s",
                                           (new_status, prod['PRODUCER_ID']), commit=True):
                                st.success(f"✅ Status changed to {new_status}!")
                                time.sleep(1)
                                st.rerun()
        else:
            st.info("No producers found")
    
    with tab2:
        st.subheader("Add New Producer")
        
        with st.form("add_producer"):
            col1, col2 = st.columns(2)
            
            with col1:
                prod_id = st.text_input("Producer ID", placeholder="PROD001")
                prod_name = st.text_input("Producer Name *")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            
            with col2:
                company = st.text_input("Company Name")
                specialization = st.text_input("Specialization", placeholder="e.g., Drama, Action")
                years_exp = st.number_input("Years of Experience", min_value=0, max_value=50, value=0)
                status = st.selectbox("Status", ["ACTIVE", "INACTIVE"])
            
            address = st.text_area("Address")
            
            if st.form_submit_button("Add Producer", use_container_width=True):
                if prod_id and prod_name:
                    query = """
                    INSERT INTO RGC_PRODUCERS 
                    (PRODUCER_ID, PRODUCER_NAME, EMAIL, PHONE, COMPANY_NAME, 
                     ADDRESS, SPECIALIZATION, YEARS_EXPERIENCE, STATUS)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    if execute_query(query, (prod_id, prod_name, email, phone, company,
                                           address, specialization, years_exp, status), commit=True):
                        st.success("✅ Producer added successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to add producer")
                else:
                    st.warning("⚠️ Please fill in required fields (ID and Name)")

# ============================================================================
# ENHANCED SCHEDULE MANAGEMENT - CORRECTED
# ============================================================================
def show_schedule_management():
    """Enhanced airing schedule management"""
    st.title("📅 Airing Schedule Management")
    
    tab1, tab2 = st.tabs(["📋 Current Schedule", "➕ Add Schedule"])
    
    with tab1:
        st.subheader("Airing Schedule")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            date_filter = st.date_input("Filter by Date", value=date.today())
        with col2:
            series_opts = execute_query("SELECT DISTINCT SERIES_NAME FROM RGC_WEB_SERIES ORDER BY SERIES_NAME")
            series_names = ["All Series"] + [s['SERIES_NAME'] for s in series_opts] if series_opts else ["All Series"]
            series_filter = st.selectbox("Filter by Series", series_names)
        with col3:
            status_filter = st.selectbox("Status", ["All", "Upcoming", "Aired", "Today"])
        
        # Build query - CORRECTED COLUMN NAMES
        base_query = """
            SELECT sch.*, e.EPISODE_TITLE, ws.SERIES_NAME, p.PLATFORM_NAME,
                   DATE(sch.START_TS) as air_date,
                   TIME(sch.START_TS) as air_time
            FROM RGC_AIRING_SCHEDULE sch
            JOIN RGC_EPISODE e ON sch.EPISODE_ID = e.EPISODE_ID
            JOIN RGC_WEB_SERIES ws ON e.SERIES_ID = ws.SERIES_ID
            LEFT JOIN RGC_PLATFORM p ON sch.PLATFORM_ID = p.PLATFORM_ID
        """
        
        where_clauses = []
        params = []
        
        if status_filter == "Today":
            where_clauses.append("DATE(sch.START_TS) = CURDATE()")
        elif status_filter == "Upcoming":
            where_clauses.append("sch.START_TS > NOW()")
        elif status_filter == "Aired":
            where_clauses.append("sch.START_TS < NOW()")
        
        if series_filter != "All Series":
            where_clauses.append("ws.SERIES_NAME = %s")
            params.append(series_filter)
        
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
        
        base_query += " ORDER BY sch.START_TS DESC LIMIT 50"
        
        schedules = execute_query(base_query, tuple(params) if params else None)
        
        if schedules:
            st.write(f"**Showing {len(schedules)} schedule entries**")
            
            for sch in schedules:
                air_datetime = sch['START_TS']
                is_upcoming = air_datetime > datetime.now()
                status_emoji = '🔜' if is_upcoming else '✅'
                
                platform_name = sch.get('PLATFORM_NAME') or 'Not Specified'
                
                with st.expander(f"{status_emoji} {sch['SERIES_NAME']} - {sch['EPISODE_TITLE']} - {air_datetime.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Schedule ID:** {sch['AIRING_SCHEDULE_ID']}")
                        st.write(f"**Series:** {sch['SERIES_NAME']}")
                        st.write(f"**Episode:** {sch['EPISODE_TITLE']}")
                        st.write(f"**Platform:** {platform_name}")
                    
                    with col2:
                        st.write(f"**Air Date:** {sch['air_date']}")
                        st.write(f"**Air Time:** {sch['air_time']}")
                        st.write(f"**Status:** {'Upcoming' if is_upcoming else 'Aired'}")
                        
                        if is_upcoming:
                            time_until = air_datetime - datetime.now()
                            days = time_until.days
                            hours = time_until.seconds // 3600
                            st.info(f"⏰ Airs in {days} days, {hours} hours")
                    
                    if st.button("🗑️ Delete Schedule", key=f"del_sch_{sch['AIRING_SCHEDULE_ID']}"):
                        if execute_query("DELETE FROM RGC_AIRING_SCHEDULE WHERE AIRING_SCHEDULE_ID = %s",
                                       (sch['AIRING_SCHEDULE_ID'],), commit=True):
                            st.success("✅ Schedule deleted!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("No schedules found")
    
    with tab2:
        st.subheader("Add New Schedule")
        
        with st.form("add_schedule"):
            col1, col2 = st.columns(2)
            
            with col1:
                schedule_id = st.text_input("Schedule ID", placeholder="AS016")
                
                # Get series and episodes
                series_opts = execute_query("SELECT SERIES_ID, SERIES_NAME FROM RGC_WEB_SERIES ORDER BY SERIES_NAME")
                if series_opts:
                    series_dict = {s['SERIES_NAME']: s['SERIES_ID'] for s in series_opts}
                    selected_series = st.selectbox("Series", list(series_dict.keys()))
                    series_id = series_dict[selected_series]
                    
                    # Get episodes for selected series
                    episodes = execute_query("""
                        SELECT EPISODE_ID, EPISODE_TITLE 
                        FROM RGC_EPISODE 
                        WHERE SERIES_ID = %s 
                        ORDER BY EPISODE_ID
                    """, (series_id,))
                    
                    if episodes:
                        ep_dict = {f"{e['EPISODE_ID']} - {e['EPISODE_TITLE']}": e['EPISODE_ID'] for e in episodes}
                        selected_ep = st.selectbox("Episode", list(ep_dict.keys()))
                        episode_id = ep_dict[selected_ep]
                    else:
                        st.error("No episodes available for this series")
                        episode_id = None
                else:
                    st.error("No series available")
                    series_id = None
                    episode_id = None
            
            with col2:
                platforms = execute_query("SELECT PLATFORM_ID, PLATFORM_NAME FROM RGC_PLATFORM ORDER BY PLATFORM_NAME")
                if platforms:
                    platform_dict = {p['PLATFORM_NAME']: p['PLATFORM_ID'] for p in platforms}
                    selected_platform = st.selectbox("Platform", list(platform_dict.keys()))
                    platform_id = platform_dict[selected_platform]
                else:
                    st.warning("No platforms available - will create without platform")
                    platform_id = None
                
                air_date = st.date_input("Air Date", value=date.today())
                air_time = st.time_input("Air Time", value=datetime.now().time())
                
                duration = st.number_input("Duration (minutes)", min_value=10, max_value=180, value=60)
            
            if st.form_submit_button("Schedule Episode", use_container_width=True):
                if schedule_id and episode_id:
                    # Combine date and time
                    start_datetime = datetime.combine(air_date, air_time)
                    end_datetime = start_datetime + timedelta(minutes=duration)
                    
                    if platform_id:
                        query = """
                        INSERT INTO RGC_AIRING_SCHEDULE 
                        (AIRING_SCHEDULE_ID, EPISODE_ID, PLATFORM_ID, START_TS, END_TS)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        params = (schedule_id, episode_id, platform_id, start_datetime, end_datetime)
                    else:
                        query = """
                        INSERT INTO RGC_AIRING_SCHEDULE 
                        (AIRING_SCHEDULE_ID, EPISODE_ID, START_TS, END_TS)
                        VALUES (%s, %s, %s, %s)
                        """
                        params = (schedule_id, episode_id, start_datetime, end_datetime)
                    
                    if execute_query(query, params, commit=True):
                        st.success("✅ Schedule added successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to add schedule")
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
        
        with col2:
            # Schedule timeline
            timeline_data = execute_query("""
                SELECT DATE(START_TS) as date, COUNT(*) as count
                FROM RGC_AIRING_SCHEDULE
                WHERE START_TS BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(START_TS)
                ORDER BY date
            """)
            
            if timeline_data:
                df = pd.DataFrame(timeline_data)
                fig = px.line(df, x='date', y='count',
                            title='Upcoming Schedule Timeline (30 days)',
                            labels={'count': 'Episodes', 'date': 'Date'})
                fig.update_layout(plot_bgcolor='#0a1628', paper_bgcolor='#0a1628',
                                font_color='#e5e5e5')
                st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# DASHBOARD - ANALYTICS & STATISTICS
# ============================================================================
def show_dashboard():
    """Analytics dashboard with visualizations"""
    st.title("📊 Analytics Dashboard")
    st.write(f"Welcome, **{st.session_state.username}** ({st.session_state.user_type})")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        result = execute_query("SELECT COUNT(*) as c FROM RGC_WEB_SERIES")
        count = result[0]['c'] if result else 0
        st.metric("Total Series", count, delta="Active")
    
    with col2:
        result = execute_query("SELECT COUNT(*) as c FROM RGC_EPISODE")
        count = result[0]['c'] if result else 0
        st.metric("Total Episodes", count)
    
    with col3:
        result = execute_query("SELECT COUNT(*) as c FROM RGC_VIEWER")
        count = result[0]['c'] if result else 0
        st.metric("Viewers", count)
    
    with col4:
        result = execute_query("SELECT AVG(RATING) as a FROM RGC_FEEDBACK")
        avg = result[0]['a'] if result and result[0]['a'] else 0
        st.metric("Avg Rating", f"{avg:.2f}⭐")
    
    st.markdown("---")

    # Contract Expiry Warnings (for Producers/Admins)
    if st.session_state.user_type in ['PRODUCER', 'ADMIN']:
        expiring = execute_query("""
            SELECT c.*, ws.SERIES_NAME, DATEDIFF(c.END_DATE, CURDATE()) as days_left
            FROM RGC_CONTRACTS c
            LEFT JOIN RGC_WEB_SERIES ws ON c.SERIES_ID = ws.SERIES_ID
            WHERE c.STATUS = 'ACTIVE' 
            AND c.END_DATE IS NOT NULL
            AND DATEDIFF(c.END_DATE, CURDATE()) BETWEEN 0 AND 30
            ORDER BY days_left
        """)
        
        if expiring:
            st.warning(f"⚠️ {len(expiring)} contract(s) expiring within 30 days!")
            with st.expander("View Expiring Contracts"):
                for e in expiring:
                    days = e['days_left']
                    color = "🔴" if days < 7 else "🟡"
                    st.write(f"{color} **{e['CONTRACT_ID']}** - {e['SERIES_NAME'] or 'N/A'} - Expires in {days} days")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Genre Distribution", "🌍 Geographic Reach", "⭐ Top Rated", "🎬 Production Analytics"])
    
    with tab1:
        st.subheader("Series by Genre")
        data = execute_query("""
            SELECT st.SERIES_TYPE_NAME as genre, COUNT(*) as count
            FROM RGC_WEB_SERIES_SERIES_TYPE wst
            JOIN RGC_SERIES_TYPE st ON wst.SERIES_TYPE_ID = st.SERIES_TYPE_ID
            GROUP BY genre ORDER BY count DESC
        """)
        if data:
            df = pd.DataFrame(data)
            fig = px.bar(df, x='genre', y='count', 
                        title='Web Series Distribution by Genre',
                        color='count', color_continuous_scale='Blues')
            fig.update_layout(plot_bgcolor='#0a1628', paper_bgcolor='#0a1628', 
                            font_color='#e5e5e5')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No genre data available")
    
    with tab2:
        st.subheader("Viewer Distribution by Country")
        data = execute_query("""
            SELECT c.COUNTRY_NAME as country, COUNT(*) as viewers
            FROM RGC_VIEWER v
            JOIN RGC_COUNTRY c ON v.COUNTRY_CODE = c.COUNTRY_CODE
            GROUP BY country ORDER BY viewers DESC LIMIT 10
        """)
        if data:
            df = pd.DataFrame(data)
            fig = px.pie(df, values='viewers', names='country',
                        title='Global Viewer Distribution (Top 10)',
                        color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(plot_bgcolor='#0a1628', paper_bgcolor='#0a1628',
                            font_color='#e5e5e5')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No viewer data available")
    
    with tab3:
        st.subheader("Top Rated Series")
        data = execute_query("""
            SELECT ws.SERIES_NAME as series, AVG(f.RATING) as rating,
                   COUNT(f.FEEDBACK_ID) as reviews
            FROM RGC_WEB_SERIES ws
            LEFT JOIN RGC_FEEDBACK f ON ws.SERIES_ID = f.SERIES_ID
            GROUP BY ws.SERIES_ID, ws.SERIES_NAME
            HAVING reviews > 0
            ORDER BY rating DESC LIMIT 10
        """)
        if data:
            df = pd.DataFrame(data)
            fig = px.bar(df, x='series', y='rating', hover_data=['reviews'],
                        title='Top 10 Highest Rated Series',
                        color='rating', color_continuous_scale='Purples')
            fig.update_layout(plot_bgcolor='#0a1628', paper_bgcolor='#0a1628',
                            font_color="#e5e5e5", xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No rating data available")
    
    with tab4:
        st.subheader("Production House Performance")
        data = execute_query("""
            SELECT ph.HOUSE_NAME as house,
                   COUNT(DISTINCT ws.SERIES_ID) as series_count,
                   COALESCE(SUM(e.TOTAL_VIEWERS), 0) as total_viewers
            FROM RGC_PRODUCTION_HOUSE ph
            LEFT JOIN RGC_WEB_SERIES ws ON ph.HOUSE_ID = ws.HOUSE_ID
            LEFT JOIN RGC_EPISODE e ON ws.SERIES_ID = e.SERIES_ID
            GROUP BY ph.HOUSE_ID, ph.HOUSE_NAME
            HAVING series_count > 0
            ORDER BY total_viewers DESC LIMIT 10
        """)
        if data:
            df = pd.DataFrame(data)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['house'],
                y=df['total_viewers'],
                name='Total Views',
                marker_color='#3895d3',
                hovertemplate='<b>%{x}</b><br>Views: %{y:,.0f}<extra></extra>'
            ))
            fig.update_layout(
                title='Top Production Houses by Total Viewership',
                plot_bgcolor='#141414',
                paper_bgcolor='#141414',
                font_color='#e5e5e5',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No production data available")

# ============================================================================
# PRODUCER DASHBOARD - CORRECTED AND ENHANCED
# ============================================================================
def show_producer_dashboard():
    """Producer-specific dashboard with contract and series management"""
    st.title("🎬 Producer Dashboard")
    st.write(f"Welcome, **{st.session_state.username}**")
    
    # Initialize tables
    create_contract_table()
    create_payment_table()
    
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📜 My Contracts", "💰 Payments"])
    
    with tab1:
        st.subheader("Production Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            contracts = execute_query("SELECT COUNT(*) as c FROM RGC_CONTRACTS WHERE STATUS = 'ACTIVE'")
            count = contracts[0]['c'] if contracts and contracts[0]['c'] is not None else 0
            st.metric("Active Contracts", count)
        
        with col2:
            value = execute_query("SELECT SUM(CONTRACT_VALUE) as v FROM RGC_CONTRACTS WHERE STATUS = 'ACTIVE'")
            val = value[0]['v'] if value and value[0]['v'] is not None else 0
            st.metric("Active Contract Value", f"${val:,.2f}")
        
        with col3:
            pending_payments = execute_query("""
                SELECT SUM(AMOUNT) as total FROM RGC_CONTRACT_PAYMENTS 
                WHERE PAYMENT_STATUS = 'PENDING'
            """)
            pending = pending_payments[0]['total'] if pending_payments and pending_payments[0]['total'] is not None else 0
            st.metric("Pending Payments", f"${pending:,.2f}")
        
        with col4:
            overdue = execute_query("""
                SELECT COUNT(*) as c FROM RGC_CONTRACT_PAYMENTS 
                WHERE PAYMENT_STATUS = 'OVERDUE'
            """)
            overdue_count = overdue[0]['c'] if overdue and overdue[0]['c'] is not None else 0
            delta_text = "⚠️" if overdue_count > 0 else None
            st.metric("Overdue Payments", overdue_count, delta=delta_text)
    
    with tab2:
        st.subheader("Contract Management")
        show_producer_contracts()
    
    with tab3:
        st.subheader("Payment Tracking")
        show_producer_payments()

def show_producer_contracts():
    """Show contracts for producers"""
    contracts = execute_query("""
        SELECT c.*, ws.SERIES_NAME, ph.HOUSE_NAME,
               DATEDIFF(c.END_DATE, CURDATE()) as days_remaining
        FROM RGC_CONTRACTS c
        LEFT JOIN RGC_WEB_SERIES ws ON c.SERIES_ID = ws.SERIES_ID
        LEFT JOIN RGC_PRODUCTION_HOUSE ph ON c.HOUSE_ID = ph.HOUSE_ID
        ORDER BY c.STATUS, c.START_DATE DESC
    """)
    
    if contracts:
        for c in contracts:
            status_emoji = {'ACTIVE': '🟢', 'PENDING': '🟡', 'EXPIRED': '🔴', 'TERMINATED': '⚫'}.get(c['STATUS'], '⚪')
            
            series_name = c['SERIES_NAME'] if c['SERIES_NAME'] else 'General Contract'
            contract_val = c['CONTRACT_VALUE'] if c['CONTRACT_VALUE'] is not None else 0
            
            with st.expander(f"{status_emoji} {c['CONTRACT_ID']} - {series_name} - ${contract_val:,.2f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type:** {c['CONTRACT_TYPE']}")
                    st.write(f"**Status:** {c['STATUS']}")
                    st.write(f"**House:** {c['HOUSE_NAME'] or 'N/A'}")
                with col2:
                    st.write(f"**Start:** {c['START_DATE']}")
                    st.write(f"**End:** {c['END_DATE'] or 'Ongoing'}")
                    if c['days_remaining'] and c['days_remaining'] < 30 and c['STATUS'] == 'ACTIVE':
                        st.warning(f"⚠️ Expires in {c['days_remaining']} days")
    else:
        st.info("No contracts found")

def show_producer_payments():
    """Show payment tracking for producers"""
    payments = execute_query("""
        SELECT p.*, c.CONTRACT_ID, ws.SERIES_NAME
        FROM RGC_CONTRACT_PAYMENTS p
        JOIN RGC_CONTRACTS c ON p.CONTRACT_ID = c.CONTRACT_ID
        LEFT JOIN RGC_WEB_SERIES ws ON c.SERIES_ID = ws.SERIES_ID
        ORDER BY p.PAYMENT_DATE DESC
        LIMIT 50
    """)
    
    if payments:
        df = pd.DataFrame(payments)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_completed = df[df['PAYMENT_STATUS'] == 'COMPLETED']['AMOUNT'].sum()
            st.metric("Completed Payments", f"${total_completed:,.2f}")
        with col2:
            total_pending = df[df['PAYMENT_STATUS'] == 'PENDING']['AMOUNT'].sum()
            st.metric("Pending", f"${total_pending:,.2f}")
        with col3:
            total_overdue = df[df['PAYMENT_STATUS'] == 'OVERDUE']['AMOUNT'].sum()
            st.metric("Overdue", f"${total_overdue:,.2f}")
        
        st.markdown("---")
        
        # Payment table
        display_df = df[['PAYMENT_DATE', 'SERIES_NAME', 'AMOUNT', 'PAYMENT_STATUS', 'PAYMENT_METHOD']].copy()
        display_df.columns = ['Date', 'Series', 'Amount', 'Status', 'Method']
        display_df['Amount'] = display_df['Amount'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00")
        display_df['Series'] = display_df['Series'].fillna('General')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No payment records found")

# ============================================================================
# WEB SERIES CATALOG
# ============================================================================
def show_catalog():
    st.title("🎬 Web Series Catalog")
    
    # CAROUSEL - Convert images to file:// URLs for proper rendering
    carousel_html = '<div class="carousel-container"><div class="carousel-track">'
    for _ in range(2):  # Duplicate for seamless loop
        for item in CAROUSEL_SERIES:
            # Convert relative path to absolute file:// URL
                image_path = item["image"]            
                carousel_html += (
                f'<div class="carousel-item">'
                f'<img src="{image_path}" alt="{item["name"]}">'
                f'<div class="carousel-overlay">'
                f'<div class="carousel-title">{item["name"]}</div>'
                f'<div style="color: #9933ff; font-weight: bold;">⭐ {item["rating"]}/5.0</div>'
                f'</div></div>'
            )
    carousel_html += '</div></div>'
    st.markdown(carousel_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Search and filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Enter series name...", key="search_box")
    with col2:
        genres = execute_query("SELECT DISTINCT SERIES_TYPE_NAME FROM RGC_SERIES_TYPE ORDER BY SERIES_TYPE_NAME")
        genre_opts = ["All Genres"] + [g['SERIES_TYPE_NAME'] for g in genres] if genres else ["All Genres"]
        genre_filter = st.selectbox("Genre", genre_opts)
    with col3:
        sort_opt = st.selectbox("Sort", ["Name", "Rating", "Episodes"])
    
    # Query with subtitles and dubbings
    base_query = """
        SELECT ws.*, ph.HOUSE_NAME,
               AVG(f.RATING) as rating,
               COUNT(DISTINCT e.EPISODE_ID) as ep_count,
               GROUP_CONCAT(DISTINCT st.SERIES_TYPE_NAME) as genres,
               GROUP_CONCAT(DISTINCT sl.S_LANGUAGE_NAME SEPARATOR ', ') as subtitles,
               GROUP_CONCAT(DISTINCT dl.D_LANGUAGE_NAME SEPARATOR ', ') as dubbings
        FROM RGC_WEB_SERIES ws
        JOIN RGC_PRODUCTION_HOUSE ph ON ws.HOUSE_ID = ph.HOUSE_ID
        LEFT JOIN RGC_FEEDBACK f ON ws.SERIES_ID = f.SERIES_ID
        LEFT JOIN RGC_EPISODE e ON ws.SERIES_ID = e.SERIES_ID
        LEFT JOIN RGC_WEB_SERIES_SERIES_TYPE wst ON ws.SERIES_ID = wst.SERIES_ID
        LEFT JOIN RGC_SERIES_TYPE st ON wst.SERIES_TYPE_ID = st.SERIES_TYPE_ID
        LEFT JOIN RGC_WEBSERIES_SUBTITLE wsub ON ws.SERIES_ID = wsub.SERIES_ID
        LEFT JOIN RGC_SUBTITLE_LANGUAGE sl ON wsub.S_LANGUAGE_ID = sl.S_LANGUAGE_ID
        LEFT JOIN RGC_WEBSERIES_DUBBING wdub ON ws.SERIES_ID = wdub.SERIES_ID
        LEFT JOIN RGC_DUBBING_LANGUAGE dl ON wdub.D_LANGUAGE_ID = dl.D_LANGUAGE_ID
    """
    
    where_clauses = []
    params = []
    
    if search:
        where_clauses.append("ws.SERIES_NAME LIKE %s")
        params.append(f"%{search}%")
    
    if genre_filter != "All Genres":
        where_clauses.append("st.SERIES_TYPE_NAME = %s")
        params.append(genre_filter)
    
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    
    base_query += " GROUP BY ws.SERIES_ID"
    
    if sort_opt == "Name":
        base_query += " ORDER BY ws.SERIES_NAME"
    elif sort_opt == "Rating":
        base_query += " ORDER BY rating DESC"
    else:
        base_query += " ORDER BY ep_count DESC"
    
    series = execute_query(base_query, tuple(params) if params else None)
    
    if series:
        st.write(f"**Found {len(series)} series**")
        
        for i in range(0, len(series), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(series):
                    s = series[i + j]
                    with col:
                        # Language badges
                        lang_badges = ""
                        if s['subtitles']:
                            for lang in s['subtitles'].split(', ')[:3]:
                                lang_badges += f'<span class="language-badge">SUB: {lang}</span>'
                        if s['dubbings']:
                            for lang in s['dubbings'].split(', ')[:3]:
                                lang_badges += f'<span class="language-badge">DUB: {lang}</span>'
                        
                        st.markdown(f"""
                        <div class="series-card">
                            <h3 style="color: #3895d3; margin-bottom: 0.5rem;">{s['SERIES_NAME']}</h3>
                            <p style="color: #7dd3fc; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                {s['HOUSE_NAME']}
                            </p>
                            <p style="font-size: 0.85rem;">
                                <strong>Episodes:</strong> {s['ep_count']}/{s['NUM_EPISODES']}<br>
                                <strong>Genre:</strong> {s['genres'] if s['genres'] else 'N/A'}<br>
                                <strong>Rating:</strong> {'⭐' * int(s['rating'] or 0)} {f"{s['rating']:.1f}" if s['rating'] else "No ratings"}
                            </p>
                            <div style="margin-top: 0.8rem;">{lang_badges}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("View Details", key=f"view_{s['SERIES_ID']}"):
                            st.session_state.selected_series = s['SERIES_ID']
                            st.rerun()
    else:
        st.info("No series found matching your criteria")

# ============================================================================
# SERIES DETAILS PAGE
# ============================================================================
def show_series_details():
    """Show detailed information about a specific series"""
    if 'selected_series' not in st.session_state:
        st.warning("No series selected")
        if st.button("← Back to Catalog"):
            st.rerun()
        return
    
    sid = st.session_state.selected_series
    
    query = """
        SELECT ws.*, ph.HOUSE_NAME, ph.ADDRESS_CITY,
               AVG(f.RATING) as avg_rating,
               COUNT(DISTINCT f.FEEDBACK_ID) as review_count,
               GROUP_CONCAT(DISTINCT st.SERIES_TYPE_NAME) as genres
        FROM RGC_WEB_SERIES ws
        JOIN RGC_PRODUCTION_HOUSE ph ON ws.HOUSE_ID = ph.HOUSE_ID
        LEFT JOIN RGC_FEEDBACK f ON ws.SERIES_ID = f.SERIES_ID
        LEFT JOIN RGC_WEB_SERIES_SERIES_TYPE wst ON ws.SERIES_ID = wst.SERIES_ID
        LEFT JOIN RGC_SERIES_TYPE st ON wst.SERIES_TYPE_ID = st.SERIES_TYPE_ID
        WHERE ws.SERIES_ID = %s
        GROUP BY ws.SERIES_ID
    """
    series = execute_query(query, (sid,))
    
    if not series:
        st.error("Series not found")
        if st.button("← Back"):
            del st.session_state.selected_series
            st.rerun()
        return
    
    s = series[0]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(s['SERIES_NAME'])
        st.write(f"**Production House:** {s['HOUSE_NAME']} ({s['ADDRESS_CITY']})")
        st.write(f"**Genre:** {s['genres'] if s['genres'] else 'N/A'}")
        st.write(f"**Language:** {s['LANGUAGE']} | **Origin:** {s['COUNTRY_OF_ORIGIN']}")
        st.write(f"**Episodes:** {s['NUM_EPISODES']} | **Released:** {s['RELEASE_DATE']}")
    
    with col2:
        if s['avg_rating']:
            st.metric("Average Rating", f"{s['avg_rating']:.1f}⭐", 
                     delta=f"{s['review_count']} reviews")
        else:
            st.info("No ratings yet")
    
    if st.button("← Back to Catalog"):
        del st.session_state.selected_series
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("📺 Episodes")
    eps_query = """
        SELECT e.EPISODE_ID, e.EPISODE_TITLE, e.TOTAL_VIEWERS, 
               e.TECHNICAL_INTERRUPTION
        FROM RGC_EPISODE e
        WHERE e.SERIES_ID = %s
        ORDER BY e.EPISODE_ID
    """
    episodes = execute_query(eps_query, (sid,))
    
    if episodes:
        df = pd.DataFrame(episodes)
        df_display = df[['EPISODE_TITLE', 'TOTAL_VIEWERS']].copy()
        df_display.columns = ['Title', 'Viewers']
        if st.session_state.user_type in ['PRODUCER', 'ADMIN']:
            df_display['Tech Issues'] = df['TECHNICAL_INTERRUPTION']
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("No episodes available yet")
    
    st.markdown("---")
    
    st.subheader("💬 User Reviews")
    
    reviews = execute_query("""
        SELECT f.*, v.ACC_FNAME, v.ACC_LNAME
        FROM RGC_FEEDBACK f
        LEFT JOIN RGC_VIEWER v ON f.ACCOUNT_ID = v.ACCOUNT_ID
        WHERE f.SERIES_ID = %s
        ORDER BY f.FEEDBACK_DATE DESC
    """, (sid,))
    
    if reviews:
        for r in reviews:
            name = f"{r.get('ACC_FNAME', 'Anonymous')} {r.get('ACC_LNAME', '')}"
            with st.expander(f"⭐ {r['RATING']}/5 - {name.strip()} ({r['FEEDBACK_DATE']})"):
                st.write(r['FEEDBACK_TEXT'])
    else:
        st.info("No reviews yet. Be the first to review!")

# ============================================================================
# FEEDBACK MANAGEMENT
# ============================================================================
def show_feedback():
    """View and submit feedback"""
    st.title("💬 Feedback & Reviews")
    
    tab1, tab2 = st.tabs(["📖 View Reviews", "✏️ Submit Review"])
    
    with tab1:
        st.subheader("Recent Reviews")
        reviews = execute_query("""
            SELECT f.*, ws.SERIES_NAME, 
                   COALESCE(v.ACC_FNAME, 'Anonymous') as fname,
                   COALESCE(v.ACC_LNAME, '') as lname
            FROM RGC_FEEDBACK f
            JOIN RGC_WEB_SERIES ws ON f.SERIES_ID = ws.SERIES_ID
            LEFT JOIN RGC_VIEWER v ON f.ACCOUNT_ID = v.ACCOUNT_ID
            ORDER BY f.FEEDBACK_DATE DESC
            LIMIT 20
        """)
        
        if reviews:
            for r in reviews:
                name = f"{r['fname']} {r['lname']}".strip()
                with st.expander(f"{r['SERIES_NAME']} - ⭐{r['RATING']}/5 by {name}"):
                    st.write(f"**Date:** {r['FEEDBACK_DATE']}")
                    st.write(f"**Review:** {r['FEEDBACK_TEXT']}")
        else:
            st.info("No reviews yet")
    
    with tab2:
        st.subheader("Submit Your Review")
        with st.form("feedback_form"):
            all_series = execute_query("SELECT SERIES_ID, SERIES_NAME FROM RGC_WEB_SERIES ORDER BY SERIES_NAME")
            if all_series:
                series_opts = {s['SERIES_NAME']: s['SERIES_ID'] for s in all_series}
                selected_series = st.selectbox("Select Series", list(series_opts.keys()))
                series_id = series_opts[selected_series]
            else:
                st.error("No series available")
                series_id = None
            
            rating = st.slider("Rating", 1, 5, 3)
            feedback_text = st.text_area("Your Review", placeholder="Share your thoughts...")
            
            submit = st.form_submit_button("Submit Review", use_container_width=True)
            
            if submit and series_id:
                if not feedback_text.strip():
                    st.warning("⚠️ Please write a review")
                else:
                    feedback_id = f"F{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    account_id = st.session_state.linked_account or 'A001'
                    
                    query = """
                    INSERT INTO RGC_FEEDBACK 
                    (FEEDBACK_ID, ACCOUNT_ID, SERIES_ID, RATING, FEEDBACK_TEXT, FEEDBACK_DATE)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    if execute_query(query, (feedback_id, account_id, series_id, 
                                           rating, feedback_text, date.today()), commit=True):
                        st.success("✅ Review submitted successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to submit review")

# ============================================================================
# ADMIN PANEL
# ============================================================================
def show_admin():
    """Admin panel for database management"""
    st.title("⚙️ Admin Panel")
    
    if st.session_state.user_type not in ['PRODUCER', 'ADMIN']:
        st.error("❌ Access Denied: Admin/Producer privileges required")
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎬 Manage Series", "📺 Manage Episodes", "🏢 Production Houses", "👥 Manage Viewers", "📜 Contracts"])
    
    with tab1:
        st.subheader("Web Series Management")
        
        series = execute_query("""
            SELECT ws.SERIES_ID, ws.SERIES_NAME, ws.NUM_EPISODES, 
                   ws.RELEASE_DATE, ph.HOUSE_NAME
            FROM RGC_WEB_SERIES ws
            JOIN RGC_PRODUCTION_HOUSE ph ON ws.HOUSE_ID = ph.HOUSE_ID
            ORDER BY ws.SERIES_NAME
        """)
        
        if series:
            df = pd.DataFrame(series)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("✏️ Update Series"):
                    with st.form("update_series"):
                        series_to_update = st.selectbox("Select Series", 
                                                       [s['SERIES_NAME'] for s in series],
                                                       key="upd_series")
                        series_id = next(s['SERIES_ID'] for s in series if s['SERIES_NAME'] == series_to_update)
                        
                        new_name = st.text_input("New Name", value=series_to_update)
                        new_eps = st.number_input("Episodes", 1, 200, 10)
                        
                        if st.form_submit_button("Update"):
                            query = "UPDATE RGC_WEB_SERIES SET SERIES_NAME = %s, NUM_EPISODES = %s WHERE SERIES_ID = %s"
                            if execute_query(query, (new_name, new_eps, series_id), commit=True):
                                st.success("✅ Series updated!")
                                time.sleep(1)
                                st.rerun()
            
            with col2:
                with st.expander("🗑️ Delete Series"):
                    with st.form("delete_series"):
                        series_to_delete = st.selectbox("Select Series", 
                                                       [s['SERIES_NAME'] for s in series],
                                                       key="del_series")
                        series_id = next(s['SERIES_ID'] for s in series if s['SERIES_NAME'] == series_to_delete)
                        
                        st.warning("⚠️ This will delete all related episodes, feedback, and schedules!")
                        confirm = st.checkbox("I understand this cannot be undone")
                        
                        if st.form_submit_button("Delete", type="primary"):
                            if confirm:
                                try:
                                    #deadlock - delete in a specific order to avoid locks
                                    #parameterised queries to prevent SQL injection
                                    with transaction() as cursor:
                                        cursor.execute("DELETE FROM RGC_FEEDBACK WHERE SERIES_ID = %s", (series_id,))
                                        cursor.execute("DELETE FROM RGC_AIRING_SCHEDULE WHERE EPISODE_ID IN (SELECT EPISODE_ID FROM RGC_EPISODE WHERE SERIES_ID = %s)", (series_id,))
                                        cursor.execute("DELETE FROM RGC_EPISODE WHERE SERIES_ID = %s", (series_id,))
                                        cursor.execute("DELETE FROM RGC_WEB_SERIES_SERIES_TYPE WHERE SERIES_ID = %s", (series_id,))
                                        cursor.execute("DELETE FROM RGC_WEB_SERIES WHERE SERIES_ID = %s", (series_id,))
                                    st.success("✅ Series deleted!")
                                    time.sleep(1)
                                    st.rerun()
                                except:
                                    st.error("❌ Delete failed")
                            else:
                                st.warning("⚠️ Please confirm deletion")
        else:
            st.info("No series found")
    
    with tab2:
        st.subheader("Episode Management")
        
        all_series = execute_query("SELECT SERIES_ID, SERIES_NAME FROM RGC_WEB_SERIES ORDER BY SERIES_NAME")
        if all_series:
            selected = st.selectbox("Filter by Series", 
                                   ["All"] + [s['SERIES_NAME'] for s in all_series])
            
            if selected == "All":
                episodes = execute_query("""
                    SELECT e.*, ws.SERIES_NAME
                    FROM RGC_EPISODE e
                    JOIN RGC_WEB_SERIES ws ON e.SERIES_ID = ws.SERIES_ID
                    ORDER BY ws.SERIES_NAME, e.EPISODE_ID
                    LIMIT 50
                """)
            else:
                series_id = next(s['SERIES_ID'] for s in all_series if s['SERIES_NAME'] == selected)
                episodes = execute_query("""
                    SELECT e.*, ws.SERIES_NAME
                    FROM RGC_EPISODE e
                    JOIN RGC_WEB_SERIES ws ON e.SERIES_ID = ws.SERIES_ID
                    WHERE e.SERIES_ID = %s
                    ORDER BY e.EPISODE_ID
                """, (series_id,))
            
            if episodes:
                df = pd.DataFrame(episodes)
                st.dataframe(df[['SERIES_NAME', 'EPISODE_ID', 'EPISODE_TITLE', 
                               'TOTAL_VIEWERS', 'TECHNICAL_INTERRUPTION']], 
                           use_container_width=True)
            else:
                st.info("No episodes found")
            
            with st.expander("➕ Add Episode"):
                with st.form("add_episode"):
                    ep_series = st.selectbox("Series", [s['SERIES_NAME'] for s in all_series])
                    ep_series_id = next(s['SERIES_ID'] for s in all_series if s['SERIES_NAME'] == ep_series)
                    
                    ep_id = st.text_input("Episode ID", placeholder="E001")
                    ep_title = st.text_input("Title")
                    ep_viewers = st.number_input("Initial Viewers", 0, 10000000, 0)
                    ep_tech = st.checkbox("Technical Interruption")
                    
                    if st.form_submit_button("Add Episode"):
                        if ep_id and ep_title:
                            query = """
                            INSERT INTO RGC_EPISODE 
                            (EPISODE_ID, SERIES_ID, EPISODE_TITLE, TOTAL_VIEWERS, TECHNICAL_INTERRUPTION)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            if execute_query(query, (ep_id, ep_series_id, ep_title, 
                                                   ep_viewers, ep_tech), commit=True):
                                st.success("✅ Episode added!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("⚠️ Fill all fields")
    
    with tab3:
        st.subheader("Production Houses")
        
        houses = execute_query("""
            SELECT ph.*, COUNT(ws.SERIES_ID) as series_count
            FROM RGC_PRODUCTION_HOUSE ph
            LEFT JOIN RGC_WEB_SERIES ws ON ph.HOUSE_ID = ws.HOUSE_ID
            GROUP BY ph.HOUSE_ID
            ORDER BY ph.HOUSE_NAME
        """)
        
        if houses:
            df = pd.DataFrame(houses)
            st.dataframe(df, use_container_width=True)
            
            with st.expander("➕ Add Production House"):
                with st.form("add_house"):
                    h_id = st.text_input("House ID", placeholder="PH016")
                    h_name = st.text_input("Name")
                    h_city = st.text_input("City")
                    h_country = st.text_input("Country")
                    
                    if st.form_submit_button("Add House"):
                        if h_id and h_name:
                            query = """
                            INSERT INTO RGC_PRODUCTION_HOUSE 
                            (HOUSE_ID, HOUSE_NAME, ADDRESS_CITY, ADDRESS_COUNTRY)
                            VALUES (%s, %s, %s, %s)
                            """
                            if execute_query(query, (h_id, h_name, h_city, h_country), commit=True):
                                st.success("✅ Production house added!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("⚠️ Fill required fields")
        else:
            st.info("No production houses found")
    
    with tab4:
        st.subheader("Viewer Accounts")
        
        viewers = execute_query("""
            SELECT v.*, c.COUNTRY_NAME,
                   COUNT(DISTINCT f.FEEDBACK_ID) as reviews
            FROM RGC_VIEWER v
            LEFT JOIN RGC_COUNTRY c ON v.COUNTRY_CODE = c.COUNTRY_CODE
            LEFT JOIN RGC_FEEDBACK f ON v.ACCOUNT_ID = f.ACCOUNT_ID
            GROUP BY v.ACCOUNT_ID
            ORDER BY v.ACC_FNAME
            LIMIT 50
        """)
        
        if viewers:
            df = pd.DataFrame(viewers)
            st.dataframe(df[['ACCOUNT_ID', 'ACC_FNAME', 'ACC_LNAME', 
                           'COUNTRY_NAME', 'reviews']], use_container_width=True)
            
            st.metric("Total Viewers", len(viewers))
        else:
            st.info("No viewers found")
    
    with tab5:
        st.subheader("📜 Contract Management")
        
        # Initialize contract tables
        create_contract_table()
        create_payment_table()
        
        # Contract Analytics - WITH NULL HANDLING
        analytics = get_contract_analytics()
        if analytics:
            a = analytics[0]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total = a.get('total_contracts') or 0
                st.metric("Total Contracts", total)
            with col2:
                active = a.get('active_contracts') or 0
                active_val = a.get('active_value') or 0
                st.metric("Active", active, delta=f"${active_val:,.2f}")
            with col3:
                pending = a.get('pending_contracts') or 0
                st.metric("Pending", pending)
            with col4:
                total_val = a.get('total_value') or 0
                st.metric("Total Value", f"${total_val:,.2f}")
        
        st.markdown("---")
        
        # View Contracts
        contracts = execute_query("""
            SELECT c.*, ws.SERIES_NAME, ph.HOUSE_NAME,
                   DATEDIFF(c.END_DATE, CURDATE()) as days_remaining
            FROM RGC_CONTRACTS c
            LEFT JOIN RGC_WEB_SERIES ws ON c.SERIES_ID = ws.SERIES_ID
            LEFT JOIN RGC_PRODUCTION_HOUSE ph ON c.HOUSE_ID = ph.HOUSE_ID
            ORDER BY c.CREATED_DATE DESC
        """)
        
        if contracts:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", 
                                            ["All", "ACTIVE", "PENDING", "EXPIRED", "TERMINATED"])
            with col2:
                type_filter = st.selectbox("Filter by Type",
                                          ["All", "PRODUCTION", "DISTRIBUTION", "LICENSING", "TALENT"])
            with col3:
                house_opts = execute_query("SELECT DISTINCT HOUSE_NAME FROM RGC_PRODUCTION_HOUSE ORDER BY HOUSE_NAME")
                house_names = ["All"] + [h['HOUSE_NAME'] for h in house_opts] if house_opts else ["All"]
                house_filter = st.selectbox("Filter by House", house_names)
            
            # Apply filters
            filtered_contracts = contracts
            if status_filter != "All":
                filtered_contracts = [c for c in filtered_contracts if c['STATUS'] == status_filter]
            if type_filter != "All":
                filtered_contracts = [c for c in filtered_contracts if c['CONTRACT_TYPE'] == type_filter]
            if house_filter != "All":
                filtered_contracts = [c for c in filtered_contracts if c['HOUSE_NAME'] == house_filter]
            
            st.write(f"**Showing {len(filtered_contracts)} contracts**")
            
            # Display contracts
            for c in filtered_contracts:
                status_color = {
                    'ACTIVE': '🟢',
                    'PENDING': '🟡',
                    'EXPIRED': '🔴',
                    'TERMINATED': '⚫'
                }.get(c['STATUS'], '⚪')
                
                days_left = c.get('days_remaining', 0)
                expiry_warning = ""
                if days_left and days_left < 30 and c['STATUS'] == 'ACTIVE':
                    expiry_warning = f" ⚠️ Expires in {days_left} days"
                
                with st.expander(f"{status_color} {c['CONTRACT_ID']} - {c['SERIES_NAME'] or 'N/A'} - ${c['CONTRACT_VALUE']:,.2f}{expiry_warning}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {c['CONTRACT_TYPE']}")
                        st.write(f"**Status:** {c['STATUS']}")
                        st.write(f"**Production House:** {c['HOUSE_NAME'] or 'N/A'}")
                        st.write(f"**Value:** ${c['CONTRACT_VALUE']:,.2f}")
                    with col2:
                        st.write(f"**Start Date:** {c['START_DATE']}")
                        st.write(f"**End Date:** {c['END_DATE'] or 'Ongoing'}")
                        st.write(f"**Payment Terms:** {c['PAYMENT_TERMS'] or 'N/A'}")
                        st.write(f"**Created:** {c['CREATED_DATE'].strftime('%Y-%m-%d')}")
                    
                    # Contract actions
                    act_col1, act_col2, act_col3 = st.columns(3)
                    with act_col1:
                        if st.button("📝 Edit", key=f"edit_{c['CONTRACT_ID']}"):
                            st.session_state[f"edit_contract_{c['CONTRACT_ID']}"] = True
                    with act_col2:
                        if c['STATUS'] == 'PENDING':
                            if st.button("✅ Activate", key=f"activate_{c['CONTRACT_ID']}"):
                                query = "UPDATE RGC_CONTRACTS SET STATUS = 'ACTIVE' WHERE CONTRACT_ID = %s"
                                if execute_query(query, (c['CONTRACT_ID'],), commit=True):
                                    st.success("Contract activated!")
                                    time.sleep(1)
                                    st.rerun()
                    with act_col3:
                        if st.button("🗑️ Delete", key=f"del_{c['CONTRACT_ID']}"):
                            query = "DELETE FROM RGC_CONTRACTS WHERE CONTRACT_ID = %s"
                            if execute_query(query, (c['CONTRACT_ID'],), commit=True):
                                st.success("Contract deleted!")
                                time.sleep(1)
                                st.rerun()
                    
                    # View payments
                    payments = execute_query("""
                        SELECT * FROM RGC_CONTRACT_PAYMENTS 
                        WHERE CONTRACT_ID = %s 
                        ORDER BY PAYMENT_DATE DESC
                    """, (c['CONTRACT_ID'],))
                    
                    if payments:
                        st.write("**Payment History:**")
                        payment_df = pd.DataFrame(payments)
                        st.dataframe(payment_df[['PAYMENT_DATE', 'AMOUNT', 'PAYMENT_STATUS', 'PAYMENT_METHOD']], 
                                   use_container_width=True)
        
        else:
            st.info("No contracts found")
        
        st.markdown("---")
        
        # Add New Contract
        with st.expander("➕ Add New Contract", expanded=False):
            with st.form("add_contract"):
                col1, col2 = st.columns(2)
                
                with col1:
                    contract_id = st.text_input("Contract ID", placeholder="CONT001")
                    
                    series_opts = execute_query("SELECT SERIES_ID, SERIES_NAME FROM RGC_WEB_SERIES ORDER BY SERIES_NAME")
                    series_dict = {s['SERIES_NAME']: s['SERIES_ID'] for s in series_opts} if series_opts else {}
                    selected_series = st.selectbox("Series", ["None"] + list(series_dict.keys()))
                    series_id = series_dict.get(selected_series) if selected_series != "None" else None
                    
                    house_opts = execute_query("SELECT HOUSE_ID, HOUSE_NAME FROM RGC_PRODUCTION_HOUSE ORDER BY HOUSE_NAME")
                    house_dict = {h['HOUSE_NAME']: h['HOUSE_ID'] for h in house_opts} if house_opts else {}
                    selected_house = st.selectbox("Production House", list(house_dict.keys()))
                    house_id = house_dict.get(selected_house)
                    
                    contract_type = st.selectbox("Contract Type", 
                                                ["PRODUCTION", "DISTRIBUTION", "LICENSING", "TALENT"])
                    contract_value = st.number_input("Contract Value ($)", min_value=0.0, step=1000.0)
                
                with col2:
                    start_date = st.date_input("Start Date", value=date.today())
                    end_date = st.date_input("End Date", value=date.today() + timedelta(days=365))
                    status = st.selectbox("Status", ["PENDING", "ACTIVE", "EXPIRED", "TERMINATED"])
                    payment_terms = st.text_area("Payment Terms", 
                                                 placeholder="e.g., 30% upfront, 70% on completion")
                
                if st.form_submit_button("Create Contract", use_container_width=True):
                    if contract_id and house_id:
                        query = """
                        INSERT INTO RGC_CONTRACTS 
                        (CONTRACT_ID, SERIES_ID, HOUSE_ID, CONTRACT_TYPE, CONTRACT_VALUE, 
                         START_DATE, END_DATE, STATUS, PAYMENT_TERMS, CREATED_BY)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        if execute_query(query, (contract_id, series_id, house_id, contract_type, 
                                               contract_value, start_date, end_date, status, 
                                               payment_terms, st.session_state.user_id), commit=True):
                            st.success("✅ Contract created successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to create contract")
                    else:
                        st.warning("⚠️ Please fill in required fields")
        
        # Add Payment
        with st.expander("💰 Add Payment", expanded=False):
            with st.form("add_payment"):
                all_contracts = execute_query("""
                    SELECT c.CONTRACT_ID, ws.SERIES_NAME, ph.HOUSE_NAME
                    FROM RGC_CONTRACTS c
                    LEFT JOIN RGC_WEB_SERIES ws ON c.SERIES_ID = ws.SERIES_ID
                    LEFT JOIN RGC_PRODUCTION_HOUSE ph ON c.HOUSE_ID = ph.HOUSE_ID
                    WHERE c.STATUS = 'ACTIVE'
                    ORDER BY c.CONTRACT_ID
                """)
                
                if all_contracts:
                    contract_dict = {
                        f"{c['CONTRACT_ID']} - {c['SERIES_NAME'] or c['HOUSE_NAME']}": c['CONTRACT_ID'] 
                        for c in all_contracts
                    }
                    selected_contract = st.selectbox("Select Contract", list(contract_dict.keys()))
                    contract_id = contract_dict[selected_contract]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        payment_id = st.text_input("Payment ID", placeholder="PAY001")
                        amount = st.number_input("Amount ($)", min_value=0.0, step=100.0)
                        payment_date = st.date_input("Payment Date", value=date.today())
                    
                    with col2:
                        payment_status = st.selectbox("Payment Status", 
                                                     ["PENDING", "COMPLETED", "OVERDUE", "CANCELLED"])
                        payment_method = st.selectbox("Payment Method",
                                                     ["Bank Transfer", "Check", "Wire", "Credit Card", "PayPal"])
                        notes = st.text_area("Notes", placeholder="Additional payment details...")
                    
                    if st.form_submit_button("Add Payment", use_container_width=True):
                        if payment_id:
                            query = """
                            INSERT INTO RGC_CONTRACT_PAYMENTS 
                            (PAYMENT_ID, CONTRACT_ID, PAYMENT_DATE, AMOUNT, PAYMENT_STATUS, PAYMENT_METHOD, NOTES)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                            if execute_query(query, (payment_id, contract_id, payment_date, amount,
                                                   payment_status, payment_method, notes), commit=True):
                                st.success("✅ Payment added successfully!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("⚠️ Please fill in payment ID")
                else:
                    st.info("No active contracts available")
        
        # Contract Reports
        st.markdown("---")
        st.subheader("📊 Contract Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Contracts by Type**")
            type_data = execute_query("""
                SELECT CONTRACT_TYPE, COUNT(*) as count, SUM(CONTRACT_VALUE) as total_value
                FROM RGC_CONTRACTS
                GROUP BY CONTRACT_TYPE
            """)
            if type_data:
                df = pd.DataFrame(type_data)
                fig = px.pie(df, values='count', names='CONTRACT_TYPE',
                           title='Distribution by Contract Type')
                fig.update_layout(plot_bgcolor='#0a1628', paper_bgcolor='#0a1628',
                                font_color='#e5e5e5')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Contract Value by Production House**")
            house_data = execute_query("""
                SELECT ph.HOUSE_NAME, SUM(c.CONTRACT_VALUE) as total_value
                FROM RGC_CONTRACTS c
                JOIN RGC_PRODUCTION_HOUSE ph ON c.HOUSE_ID = ph.HOUSE_ID
                GROUP BY ph.HOUSE_ID, ph.HOUSE_NAME
                ORDER BY total_value DESC
                LIMIT 10
            """)
            if house_data:
                df = pd.DataFrame(house_data)
                fig = px.bar(df, x='HOUSE_NAME', y='total_value',
                           title='Top 10 Houses by Contract Value')
                fig.update_layout(plot_bgcolor='#0a1628', paper_bgcolor='#0a1628',
                                font_color='#e5e5e5', xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

# User Settings Page
def show_settings():
    st.title("⚙️ User Settings")
    
    # Get user info
    if st.session_state.linked_account:
        user_data = execute_query("""
            SELECT v.*, c.COUNTRY_NAME,
                   COUNT(DISTINCT f.FEEDBACK_ID) as review_count
            FROM RGC_VIEWER v
            LEFT JOIN RGC_COUNTRY c ON v.COUNTRY_CODE = c.COUNTRY_CODE
            LEFT JOIN RGC_FEEDBACK f ON v.ACCOUNT_ID = f.ACCOUNT_ID
            WHERE v.ACCOUNT_ID = %s
            GROUP BY v.ACCOUNT_ID
        """, (st.session_state.linked_account,))
        
        if user_data:
            user = user_data[0]
            
            # Create tabs for different settings sections
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Profile", "💳 Billing", "🗣️ Languages", "🎬 Preferences", "📊 Activity"])
            
            # ============= TAB 1: PROFILE =============
            with tab1:
                st.subheader("📋 Account Overview")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Account ID", user['ACCOUNT_ID'])
                with col2:
                    st.metric("Member Since", user['DATE_OPENED'].strftime('%Y-%m-%d'))
                with col3:
                    account_age = (date.today() - user['DATE_OPENED']).days
                    st.metric("Member For", f"{account_age} days")
                
                st.markdown("---")
                
                st.subheader("🏠 Address Information")
                with st.expander("📝 Edit Address", expanded=False):
                    with st.form("update_address"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_fname = st.text_input("First Name", value=user['ACC_FNAME'])
                            new_street = st.text_input("Street Address", value=user['ADDRESS_STREET'])
                            new_city = st.text_input("City", value=user['ADDRESS_CITY'])
                        with col2:
                            new_lname = st.text_input("Last Name", value=user.get('ACC_LNAME', ''))
                            new_zip = st.text_input("ZIP Code", value=user['ADDRESS_ZIP'])
                            new_country = st.selectbox("Country", ["United States", "Canada", "United Kingdom", "India", "Australia", "Other"], 
                                                       index=0)
                        
                        if st.form_submit_button("Update Address", use_container_width=True):
                            query = """
                            UPDATE RGC_VIEWER 
                            SET ACC_FNAME = %s, ACC_LNAME = %s,
                                ADDRESS_STREET = %s, ADDRESS_CITY = %s, 
                                ADDRESS_ZIP = %s
                            WHERE ACCOUNT_ID = %s
                            """
                            if execute_query(query, (new_fname, new_lname, new_street, new_city, new_zip, 
                                                   user['ACCOUNT_ID']), commit=True):
                                st.success("✅ Address updated successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Update failed")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**📛 Full Name:** {user['ACC_FNAME']} {user.get('ACC_LNAME', '')}")
                    st.write(f"**📍 Street:** {user['ADDRESS_STREET']}")
                with col2:
                    st.write(f"**🌍 Country:** {user['COUNTRY_NAME']}")
                    st.write(f"**🏙️ City, ZIP:** {user['ADDRESS_CITY']}, {user['ADDRESS_ZIP']}")
                
                st.markdown("---")
                st.subheader("📊 Account Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Reviews", user['review_count'])
                with col2:
                    # Get most watched series
                    most_watched = execute_query("""
                        SELECT COUNT(f.FEEDBACK_ID) as count
                        FROM RGC_FEEDBACK f
                        WHERE f.ACCOUNT_ID = %s AND f.RATING >= 4
                    """, (st.session_state.linked_account,))
                    high_ratings = most_watched[0]['count'] if most_watched else 0
                    st.metric("High Ratings (4+⭐)", high_ratings)
                with col3:
                    avg_rating = execute_query("""
                        SELECT AVG(f.RATING) as avg
                        FROM RGC_FEEDBACK f
                        WHERE f.ACCOUNT_ID = %s
                    """, (st.session_state.linked_account,))
                    avg = avg_rating[0]['avg'] if avg_rating and avg_rating[0]['avg'] else 0
                    st.metric("Average Rating", f"{avg:.2f}⭐")
                with col4:
                    # Get favorite genre
                    favorite_gen = execute_query("""
                        SELECT st.SERIES_TYPE_NAME, COUNT(*) as count
                        FROM RGC_FEEDBACK f
                        JOIN RGC_WEB_SERIES ws ON f.SERIES_ID = ws.SERIES_ID
                        JOIN RGC_WEB_SERIES_SERIES_TYPE wst ON ws.SERIES_ID = wst.SERIES_ID
                        JOIN RGC_SERIES_TYPE st ON wst.SERIES_TYPE_ID = st.SERIES_TYPE_ID
                        WHERE f.ACCOUNT_ID = %s
                        GROUP BY st.SERIES_TYPE_ID
                        ORDER BY count DESC
                        LIMIT 1
                    """, (st.session_state.linked_account,))
                    fav_genre = favorite_gen[0]['SERIES_TYPE_NAME'] if favorite_gen else "N/A"
                    st.metric("Favorite Genre", fav_genre)
            
            # ============= TAB 2: BILLING =============
            with tab2:
                st.subheader("💳 Subscription & Billing")
                
                # Current subscription details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div>', unsafe_allow_html=True)
                    st.write("**Current Plan**")
                    st.metric("Monthly Charge", f"${user['MONTHLY_CHARGE']:.2f}")
                    
                    # Calculate next billing date
                    next_billing = user['DATE_OPENED'] + timedelta(days=30)
                    days_until = (next_billing - date.today()).days
                    if days_until < 0:
                        days_since = (date.today() - user['DATE_OPENED']).days
                        cycles = (days_since // 30) + 1
                        next_billing = user['DATE_OPENED'] + timedelta(days=30 * cycles)
                        days_until = (next_billing - date.today()).days
                    
                    st.metric("Next Billing Date", next_billing.strftime('%Y-%m-%d'), 
                             delta=f"{days_until} days remaining")
                    
                    st.metric("Status", "🟢 Active")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div>', unsafe_allow_html=True)
                    st.write("**Billing Summary**")
                    annual_charge = user['MONTHLY_CHARGE'] * 12
                    st.metric("Annual Cost (est.)", f"${annual_charge:.2f}")
                    
                    # Total spent
                    months_active = (date.today() - user['DATE_OPENED']).days // 30 + 1
                    total_spent = user['MONTHLY_CHARGE'] * months_active
                    st.metric("Total Spent", f"${total_spent:.2f}")
                    
                    # Savings info
                    st.info("💡 Pro Tip: Annual plans save 15% compared to monthly!")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("📋 Billing History")
                
                billing_history = []
                months_active = (date.today() - user['DATE_OPENED']).days // 30 + 1
                for i in range(min(months_active, 12)):
                    billing_date = user['DATE_OPENED'] + timedelta(days=30 * (i + 1))
                    status = "Paid" if billing_date <= date.today() else "Upcoming"
                    billing_history.append({
                        'Billing Date': billing_date.strftime('%Y-%m-%d'),
                        'Amount': f"${user['MONTHLY_CHARGE']:.2f}",
                        'Status': status,
                        'Type': 'Monthly Subscription'
                    })
                
                if billing_history:
                    for bill in billing_history[:6]:  # Show last 6 months
                        status_color = "🟢" if bill['Status'] == "Paid" else "🟡"
                        with st.container():
                            st.markdown(f"""
                            <div class="billing-card {bill['Status'].lower()}">
                                <strong>{status_color} {bill['Billing Date']}</strong> | 
                                {bill['Amount']} | 
                                <span style="color: #3895d3;">{bill['Status']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("💰 Payment Methods")
                
                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("💳 Add Payment Method"):
                        with st.form("add_payment"):
                            payment_type = st.selectbox("Payment Type", ["Credit Card", "Debit Card", "PayPal", "Apple Pay"])
                            if payment_type == "Credit Card" or payment_type == "Debit Card":
                                st.text_input("Card Number", placeholder="•••• •••• •••• 1234")
                                col_exp, col_cvv = st.columns(2)
                                with col_exp:
                                    st.text_input("Expiry (MM/YY)")
                                with col_cvv:
                                    st.text_input("CVV", type="password")
                            else:
                                st.text_input("Email")
                            
                            st.checkbox("Set as default payment method")
                            
                            if st.form_submit_button("Add Payment Method"):
                                st.success("✅ Payment method added successfully!")
                
                with col2:
                    st.write("**Current Payment Method**")
                    st.markdown("""
                    <div class="settings-card">
                        <strong>💳 Visa •••• 4242</strong><br/>
                        Expires: 12/26<br/>
                        <span style="color: #3895d3; font-weight: bold;">Default</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("⚙️ Billing Preferences")
                
                col1, col2 = st.columns(2)
                with col1:
                    auto_renew = st.checkbox("Auto-renew subscription", value=True)
                    billing_email = st.text_input("Billing Email", value="user@example.com")
                
                with col2:
                    receipt_frequency = st.selectbox("Receipt Frequency", ["Monthly", "Quarterly", "Annually"])
                    currency = st.selectbox("Currency", ["USD ($)", "EUR (€)", "GBP (£)", "INR (₹)"])
                
                if st.button("Save Billing Preferences", use_container_width=True):
                    st.success("✅ Billing preferences updated!")
            
            # ============= TAB 3: LANGUAGES =============
            with tab3:
                st.subheader("🗣️ Language Preferences")
                
                st.write("Customize your subtitle and dubbing preferences for a better viewing experience.")
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**📝 Preferred Subtitle Language**")
                    subtitle_lang = st.selectbox("Subtitles", 
                                                ["English", "Spanish", "French", "German", "Hindi", "Japanese", "Korean", "Mandarin", "None"])
                    
                    st.write("**🎬 Preferred Dubbing Language**")
                    dubbing_lang = st.selectbox("Dubbing",
                                               ["English", "Spanish", "French", "German", "Hindi", "Japanese", "Korean", "Mandarin", "Original"])
                
                with col2:
                    st.write("**Additional Subtitle Languages**")
                    st.multiselect("Select up to 3 additional languages:",
                                   ["English", "Spanish", "French", "German", "Hindi", "Japanese", "Korean", "Mandarin"],
                                   max_selections=3)
                    
                    st.write("**Accessibility Options**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.checkbox("Closed Captions (CC)")
                    with col_b:
                        st.checkbox("Hearing Impaired (HI)")
                
                st.markdown("---")
                st.write("**Available Languages for Series**")
                
                # Get available languages across all series
                subtitles_available = execute_query("""
                    SELECT DISTINCT sl.S_LANGUAGE_NAME
                    FROM RGC_SUBTITLE_LANGUAGE sl
                    ORDER BY sl.S_LANGUAGE_NAME
                """)
                
                dubbings_available = execute_query("""
                    SELECT DISTINCT dl.D_LANGUAGE_NAME
                    FROM RGC_DUBBING_LANGUAGE dl
                    ORDER BY dl.D_LANGUAGE_NAME
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Subtitles Available:**")
                    if subtitles_available:
                        for sub in subtitles_available:
                            st.write(f"  • {sub['S_LANGUAGE_NAME']}")
                    else:
                        st.info("No subtitles available")
                
                with col2:
                    st.write("**Dubbing Available:**")
                    if dubbings_available:
                        for dub in dubbings_available:
                            st.write(f"  • {dub['D_LANGUAGE_NAME']}")
                    else:
                        st.info("No dubbing available")
                
                st.markdown("---")
                if st.button("Save Language Preferences", use_container_width=True, key="save_lang"):
                    st.success("✅ Language preferences saved!")
            
            # ============= TAB 4: PREFERENCES =============
            with tab4:
                st.subheader("🎬 Viewing Preferences")
                
                st.write("Customize how you want to watch content on RGC Stream.")
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**📺 Playback Settings**")
                    video_quality = st.selectbox("Video Quality", 
                                                ["Auto", "4K Ultra HD", "Full HD", "HD", "Standard"])
                    st.write(f"Selected: **{video_quality}**")
                    
                    auto_play = st.checkbox("Auto-play next episode", value=True)
                    subtitles_default = st.checkbox("Show subtitles by default", value=True)
                
                with col2:
                    st.write("**🔔 Notification Settings**")
                    new_series = st.checkbox("Notify about new series", value=True)
                    episode_release = st.checkbox("Notify when new episodes release", value=True)
                    recommendations = st.checkbox("Personalized recommendations", value=True)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**📊 Privacy Settings**")
                    public_profile = st.checkbox("Make my profile public", value=False)
                    share_watch_history = st.checkbox("Share watch history with friends", value=False)
                
                with col2:
                    st.write("**🛡️ Parental Controls**")
                    enable_parental = st.checkbox("Enable parental controls", value=False)
                    if enable_parental:
                        rating_limit = st.selectbox("Content Rating Limit", 
                                                    ["G", "PG", "PG-13", "R", "No Limit"])
                        st.write(f"Content limit: **{rating_limit}**")
                
                st.markdown("---")
                if st.button("Save Preferences", use_container_width=True, key="save_pref"):
                    st.success("✅ Preferences updated successfully!")
            
            # ============= TAB 5: ACTIVITY =============
            with tab5:
                st.subheader("📊 Your Activity")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Reviews", user['review_count'])
                with col2:
                    watched_series = execute_query("""
                        SELECT COUNT(DISTINCT SERIES_ID) as count
                        FROM RGC_FEEDBACK
                        WHERE ACCOUNT_ID = %s
                    """, (st.session_state.linked_account,))
                    watched_count = watched_series[0]['count'] if watched_series else 0
                    st.metric("Series Watched", watched_count)
                with col3:
                    avg_rating = execute_query("""
                        SELECT AVG(f.RATING) as avg
                        FROM RGC_FEEDBACK f
                        WHERE f.ACCOUNT_ID = %s
                    """, (st.session_state.linked_account,))
                    avg = avg_rating[0]['avg'] if avg_rating and avg_rating[0]['avg'] else 0
                    st.metric("Avg Rating Given", f"{avg:.1f}⭐")
                with col4:
                    last_review = execute_query("""
                        SELECT MAX(FEEDBACK_DATE) as last_date
                        FROM RGC_FEEDBACK
                        WHERE ACCOUNT_ID = %s
                    """, (st.session_state.linked_account,))
                    last_date = last_review[0]['last_date'] if last_review and last_review[0]['last_date'] else None
                    if last_date:
                        days_ago = (date.today() - last_date).days
                        st.metric("Last Review", f"{days_ago} days ago")
                    else:
                        st.metric("Last Review", "Never")
                
                st.markdown("---")
                st.subheader("📋 Recent Activity")
                
                recent_reviews = execute_query("""
                    SELECT f.*, ws.SERIES_NAME
                    FROM RGC_FEEDBACK f
                    JOIN RGC_WEB_SERIES ws ON f.SERIES_ID = ws.SERIES_ID
                    WHERE f.ACCOUNT_ID = %s
                    ORDER BY f.FEEDBACK_DATE DESC
                    LIMIT 5
                """, (st.session_state.linked_account,))
                
                if recent_reviews:
                    for review in recent_reviews:
                        with st.expander(f"⭐ {review['RATING']}/5 - {review['SERIES_NAME']} ({review['FEEDBACK_DATE'].strftime('%Y-%m-%d')})"):
                            st.write(f"**Review:** {review['FEEDBACK_TEXT']}")
                else:
                    st.info("No reviews yet. Start rating series to build your activity history!")
                
                st.markdown("---")
                st.subheader("🎯 Achievements")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write("⭐ **5 Star Critic**")
                    st.caption("Left 5 reviews")
                    if user['review_count'] >= 5:
                        st.write("✅ Earned")
                    else:
                        st.write(f"Progress: {user['review_count']}/5")
                
                with col2:
                    st.write("🎬 **Series Binge**")
                    st.caption("Watched 10 series")
                    if watched_count >= 10:
                        st.write("✅ Earned")
                    else:
                        st.write(f"Progress: {watched_count}/10")
                
                with col3:
                    st.write("💯 **Rating Master**")
                    st.caption("Avg rating > 4.0")
                    if avg and avg >= 4.0:
                        st.write("✅ Earned")
                    else:
                        st.write(f"Progress: {avg:.1f}/4.0")
                
                with col4:
                    st.write("🏆 **Loyal Member**")
                    st.caption("Member for 365 days")
                    account_age = (date.today() - user['DATE_OPENED']).days
                    if account_age >= 365:
                        st.write("✅ Earned")
                    else:
                        st.write(f"Progress: {account_age}/365 days")
        
        else:
            st.warning("No viewer account linked to this user")
    else:
        st.info("ℹ️ No viewer account linked. Link an account during registration to access settings.")

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    """Main application logic"""
    
    if not st.session_state.logged_in:
        show_auth()
        return
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown('<div style="font-family: Poppins; font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, #0099ff 0%, #3895d3 50%, #9933ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-align: center; margin-bottom: 2rem;">🎬 RGC STREAM</div>', unsafe_allow_html=True)
        
        st.write(f"<p style='margin: 0.3rem 0; font-weight: 600; color: #f0f4f9;'>👤 {st.session_state.username}</p>", unsafe_allow_html=True)
        st.write(f"<p style='margin: 0.3rem 0; font-size: 0.85rem; color: #b0b8c5;'>{st.session_state.user_type}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.write("<p style='font-weight: 600; font-size: 0.95rem; color: #f0f4f9; margin-bottom: 1rem;'>Navigation</p>", unsafe_allow_html=True)
        
        menu_options = {
            "📊 Dashboard": "dashboard",
            "🎬 Catalog": "catalog",
            "💬 Feedback": "feedback",
            "⚙️ Settings": "settings"
        }
        
        if st.session_state.user_type == 'PRODUCER':
            menu_options["🎬 Producer Portal"] = "producer"
            menu_options["🎭 Cast & Crew"] = "associations"
            menu_options["📅 Schedule"] = "schedule"
        
        if st.session_state.user_type in ['PRODUCER']:
            menu_options["🎥 Producers"] = "producers"        
        if st.session_state.user_type in ['ADMIN']:
            menu_options["🔧 Admin Panel"] = "admin"

        
        selected = st.radio("", list(menu_options.keys()), label_visibility="collapsed")
        page = menu_options[selected]
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            for key in ['logged_in', 'user_type', 'user_id', 'username', 'linked_account', 'selected_series']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; font-size: 0.75rem; color: var(--text-secondary); margin-top: 2rem;">
        <p style="margin: 0.3rem 0; font-weight: 500;">RGC Stream v1.0</p>
        <p style="margin: 0.3rem 0;">CS-GY 6083 Project</p>
        <p style="margin: 0.3rem 0; margin-top: 0.5rem;">© 2025 Team RGC</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Area
    if 'selected_series' in st.session_state and page == "catalog":
        show_series_details()
    elif page == "dashboard":
        show_dashboard()
    elif page == "catalog":
        show_catalog()
    elif page == "feedback":
        show_feedback()
    elif page == "settings":
        show_settings()
    elif page == "producer":
        show_producer_dashboard()
    elif page == "associations":
        show_associations()
    elif page == "producers":
        show_producers()
    elif page == "schedule":
        show_schedule_management()
    elif page == "admin":
        show_admin()

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()