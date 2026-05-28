import streamlit as st
from utils.auth import ensure_authenticated, get_current_user, is_admin_user, render_auth_status
from utils.storage import load_user_bucket, update_user_bucket
from utils.ui import apply_base_theme

st.set_page_config(
    page_title="AaharAI 🌿",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)
apply_base_theme()

# --- Full CSS Styling ---
st.markdown("""
<style>
    .feature-card {
        background: linear-gradient(135deg, #1e1e3a, #2d2d4e);
        border: 1px solid #3d3d6e;
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: #6c63ff;
    }
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(90deg, #6c63ff, #ff6584, #43e97b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1.35rem;
        color: #a0a0c0;
        text-align: center;
        margin-top: 12px;
    }
    .hero-desc {
        font-size: 1.05rem;
        color: #c0c0d8;
        text-align: center;
        max-width: 700px;
        margin: 18px auto 0 auto;
        line-height: 1.7;
    }
    .stat-box {
        background: linear-gradient(135deg, #6c63ff22, #6c63ff44);
        border: 1px solid #6c63ff66;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        color: #6c63ff;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #a0a0c0;
    }
    .how-step {
        background: linear-gradient(135deg, #1e1e3a, #2d2d4e);
        border: 1px solid #3d3d6e;
        border-radius: 14px;
        padding: 20px 24px;
        margin: 6px 0;
    }
    .how-step h4 { color: #6c63ff; margin-bottom: 6px; }
    .how-step p  { color: #a0a0c0; margin: 0; font-size: 0.95rem; }
    .badge {
        display: inline-block;
        background: #6c63ff33;
        border: 1px solid #6c63ff66;
        border-radius: 20px;
        padding: 4px 14px;
        color: #a0a0ff;
        font-size: 0.85rem;
        margin: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ─── LANDING PAGE (shown before login) ───────────────────────────────────────
if (
    not st.session_state.get("is_authenticated", False)
    and not st.session_state.get("show_login", False)
):

    # Hero
    st.markdown('<div class="hero-title">🌿 AaharAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Aapka Personal Indian Nutrition Saathi — Powered by AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-desc">'
        'AaharAI is your free, AI-powered Indian diet assistant. It understands your body, '
        'your goals, and your love for Indian food — and turns that into personalized meal plans, '
        'nutrition insights, and expert diet advice, all in one place.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="stat-box"><div class="stat-number">500+</div><div class="stat-label">Indian Foods</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="stat-box"><div class="stat-number">7-Day</div><div class="stat-label">Meal Plans</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="stat-box"><div class="stat-number">AI</div><div class="stat-label">Powered</div></div>', unsafe_allow_html=True)
    c4.markdown('<div class="stat-box"><div class="stat-number">Free</div><div class="stat-label">Forever</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # What AaharAI does
    st.markdown("## 🚀 What AaharAI Does for You")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="feature-card"><h3>👤 Personalized Profile</h3><p style="color:#a0a0c0;">Enter your age, weight, height, goal, diet type and activity level. AaharAI tailors everything around you.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><h3>🔍 Food Nutrition Search</h3><p style="color:#a0a0c0;">Get detailed nutrition facts for any Indian dish — calories, protein, carbs, fats and health benefits. Compare two foods side by side.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><h3>📊 Health Dashboard</h3><p style="color:#a0a0c0;">Track your BMI over time. See your BMR, TDEE and daily macro targets based on your goal — visually and clearly.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h3>🍛 AI Meal Planner</h3><p style="color:#a0a0c0;">Get a 1, 3 or 7-day Indian meal plan — North Indian, South Indian, Bengali, Gujarati and more. Download or save plans for later.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><h3>💬 Chat with AaharAI</h3><p style="color:#a0a0c0;">Ask diet questions in Hindi or English. Get instant, personalized advice from your AI dietician — anytime.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><h3>🔐 Secure Accounts</h3><p style="color:#a0a0c0;">Your data is yours. Every account is password-protected with recovery options. All data is stored privately per user.</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # How it works
    st.markdown("## 🧭 How It Works")
    st.markdown("<br>", unsafe_allow_html=True)
    hw1, hw2, hw3, hw4 = st.columns(4)
    with hw1:
        st.markdown('<div class="how-step"><h4>1️⃣ Create Account</h4><p>Sign up in seconds. Your data is stored privately and never shared.</p></div>', unsafe_allow_html=True)
    with hw2:
        st.markdown('<div class="how-step"><h4>2️⃣ Set Your Profile</h4><p>Tell AaharAI about your body, goal, diet and lifestyle.</p></div>', unsafe_allow_html=True)
    with hw3:
        st.markdown('<div class="how-step"><h4>3️⃣ Get Your Plan</h4><p>Receive an AI-generated Indian meal plan tailored to your goals.</p></div>', unsafe_allow_html=True)
    with hw4:
        st.markdown('<div class="how-step"><h4>4️⃣ Track and Improve</h4><p>Log BMI, chat with your AI dietician, and refine your diet over time.</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # Who is this for
    st.markdown("## 👥 Who Is This For?")
    st.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <span class="badge">🏠 Home Cooks</span>
    <span class="badge">💪 Fitness Beginners</span>
    <span class="badge">⚖️ Weight Loss Goals</span>
    <span class="badge">🌱 Vegetarians & Vegans</span>
    <span class="badge">🍱 Indian Cuisine Lovers</span>
    <span class="badge">🩺 Health Conscious Individuals</span>
    <span class="badge">💼 Busy Professionals</span>
    <span class="badge">👨‍👩‍👧 Families</span>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("<br>", unsafe_allow_html=True)

    # CTA
    st.markdown('<div style="text-align:center; font-size:1.5rem; font-weight:700; color:white;">Ready to eat smarter?</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#a0a0c0; margin-bottom:20px;">Create your free account and get your first personalized meal plan in under 2 minutes.</div>', unsafe_allow_html=True)

    btn_col = st.columns([1, 1, 1])
    with btn_col[1]:
        if st.button("🚀 Get Started — It's Free", type="primary", use_container_width=True):
            st.session_state["show_login"] = True
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#a0a0c0; font-size:0.85rem;">AaharAI 🌿 — Swasth Khao, Swasth Raho | Powered by Groq AI & Llama 3.3</div>', unsafe_allow_html=True)
    st.stop()

# ─── LOGIN GATE (after Get Started is clicked) ────────────────────────────────
if st.session_state.get("show_login", False) or not st.session_state.get("is_authenticated", False):
    ensure_authenticated()

render_auth_status()
st.session_state.pop("show_login", None)

# Load saved data into session on startup
active_user = get_current_user()
data_loaded_for = st.session_state.get('data_loaded_for')

if active_user and data_loaded_for != active_user:
    saved = load_user_bucket(active_user)
    st.session_state['profile'] = saved.get('profile', {})
    st.session_state['bmi_history'] = saved.get('bmi_history', [])
    st.session_state['meal_plan'] = saved.get('meal_plan', "")
    st.session_state['chat_history'] = saved.get('chat_history', [])
    st.session_state['data_loaded_for'] = active_user

st.session_state['save_func'] = lambda data: update_user_bucket(active_user, data)
st.session_state['load_func'] = lambda: load_user_bucket(active_user)

# --- Home Dashboard (shown after login) ---
st.markdown('<div class="hero-title">🌿 AaharAI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Aapka Personal Indian Nutrition Saathi — Powered by AI</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="stat-box"><div class="stat-number">500+</div><div class="stat-label">Indian Foods</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stat-box"><div class="stat-number">7-Day</div><div class="stat-label">Meal Plans</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stat-box"><div class="stat-number">AI</div><div class="stat-label">Powered</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="stat-box"><div class="stat-number">Free</div><div class="stat-label">Forever</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

if st.session_state.get('profile'):
    profile = st.session_state['profile']
    st.markdown(f"### 👋 Welcome back, **{profile['name']}**!")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎯 Goal", profile['goal'].split()[-1])
    col2.metric("⚖️ Weight", f"{profile['weight']} kg")
    col3.metric("📏 BMI", profile['bmi'])
    col4.metric("🥗 Diet", profile['diet_type'])
    st.markdown("<br>", unsafe_allow_html=True)

st.markdown("## 🚀 What can I do for you?")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="feature-card"><h3>👤 Personal Profile</h3><p style="color:#a0a0c0;">Set up your health profile with age, weight, height, goals and diet preferences. Get fully personalized recommendations.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-card"><h3>🔍 Food Nutrition Search</h3><p style="color:#a0a0c0;">Search detailed nutrition info for any Indian food. Compare two foods side by side instantly.</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card"><h3>🍛 AI Meal Planner</h3><p style="color:#a0a0c0;">Get a personalized 7-day Indian meal plan based on your health goals, diet type and cuisine preferences.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-card"><h3>💬 Chat with AaharAI</h3><p style="color:#a0a0c0;">Ask any diet or nutrition question in Hindi or English. Get instant, personalized advice from your AI dietician.</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# --- Quick Start ---
st.markdown("## ⚡ Quick Start")
st.markdown("<br>", unsafe_allow_html=True)
is_admin = is_admin_user(active_user)
columns = st.columns(4 if is_admin else 3)
col1, col2, col3 = columns[0], columns[1], columns[2]
with col1:
    st.page_link("pages/1_Profile.py", label="👤 Setup My Profile", icon="1️⃣", use_container_width=True)
with col2:
    st.page_link("pages/2_Meal_Planner.py", label="🍛 Generate Meal Plan", icon="2️⃣", use_container_width=True)
with col3:
    st.page_link("pages/4_Chat.py", label="💬 Chat with AaharAI", icon="3️⃣", use_container_width=True)
if is_admin:
    with columns[3]:
        st.page_link("pages/6_Admin.py", label="🛡️ Open Admin Panel", icon="4️⃣", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#a0a0c0; font-size:0.85rem;">AaharAI 🌿 — Swasth Khao, Swasth Raho | Powered by Groq AI & Llama 3.3</div>', unsafe_allow_html=True)
