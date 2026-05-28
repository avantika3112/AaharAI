import streamlit as st
import plotly.graph_objects as go
import os, sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import ensure_authenticated, get_current_user, render_auth_status
from utils.storage import load_user_bucket, update_user_bucket
from utils.ui import apply_base_theme

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
apply_base_theme()
ensure_authenticated()
render_auth_status()

active_user = get_current_user()

def save_bmi_history(history):
    update_user_bucket(active_user, {"bmi_history": history})

st.title("📊 My Dashboard")
st.caption("Track your health progress over time")
st.divider()

if not st.session_state.get('profile'):
    saved_profile = load_user_bucket(active_user).get('profile')
    if saved_profile:
        st.session_state['profile'] = saved_profile

if not st.session_state.get('profile'):
    st.warning("⚠️ Please fill your profile first!")
    st.page_link("pages/1_Profile.py", label="👉 Go to My Profile", icon="👤")
    st.stop()

profile = st.session_state['profile']

# --- Profile Summary ---
st.subheader(f"👋 {profile['name']}'s Health Overview")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🎯 Goal", profile['goal'].split()[-1])
col2.metric("⚖️ Weight", f"{profile['weight']} kg")
col3.metric("📏 Height", f"{profile['height']} cm")
col4.metric("🧮 BMI", profile['bmi'])
col5.metric("🥗 Diet", profile['diet_type'])

st.divider()

# --- BMI Gauge Chart ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎯 BMI Gauge")
    bmi = profile['bmi']

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=bmi,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Your BMI", 'font': {'size': 20, 'color': 'white'}},
        gauge={
            'axis': {'range': [10, 45], 'tickcolor': "white"},
            'bar': {'color': "#6c63ff"},
            'bgcolor': "#1e1e3a",
            'bordercolor': "#3d3d6e",
            'steps': [
                {'range': [10, 18.5], 'color': '#3b82f6'},
                {'range': [18.5, 25], 'color': '#22c55e'},
                {'range': [25, 30], 'color': '#f59e0b'},
                {'range': [30, 45], 'color': '#ef4444'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': bmi
            }
        },
        number={'font': {'color': 'white', 'size': 40}}
    ))

    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=300,
        margin=dict(t=50, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # BMI Category
    if bmi < 18.5:
        st.info("🔵 Underweight (BMI < 18.5)")
    elif 18.5 <= bmi < 25:
        st.success("🟢 Normal Weight (18.5 - 24.9)")
    elif 25 <= bmi < 30:
        st.warning("🟡 Overweight (25 - 29.9)")
    else:
        st.error("🔴 Obese (BMI ≥ 30)")

with col_right:
    st.subheader("📈 BMI History Tracker")

    # Initialize BMI history
    if 'bmi_history' not in st.session_state:
        st.session_state['bmi_history'] = load_user_bucket(active_user).get('bmi_history', [])

    # Add today's BMI
    col_w, col_h = st.columns(2)
    with col_w:
        new_weight = st.number_input("Log Today's Weight (kg)", min_value=20.0, max_value=200.0,
                                      value=float(profile['weight']), step=0.5)
    with col_h:
        new_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0,
                                      value=float(profile['height']), step=0.5)

    if st.button("➕ Log Today's BMI", type="primary", use_container_width=True):
        new_bmi = round(new_weight / ((new_height / 100) ** 2), 1)
        entry = {
            "date": datetime.now().strftime("%d %b"),
            "bmi": new_bmi,
            "weight": new_weight
        }
        st.session_state['bmi_history'].append(entry)
        save_bmi_history(st.session_state['bmi_history'])
        st.success(f"✅ Logged! BMI: {new_bmi}")
        st.rerun()

    # Plot BMI history
    if st.session_state['bmi_history']:
        dates = [e['date'] for e in st.session_state['bmi_history']]
        bmis = [e['bmi'] for e in st.session_state['bmi_history']]
        weights = [e['weight'] for e in st.session_state['bmi_history']]

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=dates, y=bmis,
            mode='lines+markers',
            name='BMI',
            line=dict(color='#6c63ff', width=3),
            marker=dict(size=8, color='#6c63ff')
        ))
        fig_line.add_hline(y=18.5, line_dash="dash", line_color="#3b82f6", annotation_text="Underweight")
        fig_line.add_hline(y=25, line_dash="dash", line_color="#22c55e", annotation_text="Normal")
        fig_line.add_hline(y=30, line_dash="dash", line_color="#f59e0b", annotation_text="Overweight")

        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(30,30,58,0.5)',
            font={'color': 'white'},
            height=280,
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(gridcolor='#2d2d4e'),
            yaxis=dict(gridcolor='#2d2d4e', title="BMI")
        )
        st.plotly_chart(fig_line, use_container_width=True)

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state['bmi_history'] = []
            save_bmi_history([])
            st.rerun()
    else:
        st.info("📝 Log your BMI daily to see your progress chart!")

st.divider()

# --- Daily Calorie Needs ---
st.subheader("🔥 Your Daily Calorie Needs")

age = profile['age']
weight = profile['weight']
height = profile['height']
gender = profile['gender']
activity = profile['activity_level']

# BMR using Mifflin-St Jeor
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

activity_multipliers = {
    "Sedentary": 1.2,
    "Lightly": 1.375,
    "Moderately": 1.55,
    "Very": 1.725
}
multiplier = 1.2
for key, val in activity_multipliers.items():
    if key.lower() in activity.lower():
        multiplier = val
        break

tdee = round(bmr * multiplier)

goal = profile['goal']
if "Lose" in goal:
    target = tdee - 500
    label = "Weight Loss Target"
elif "Gain" in goal:
    target = tdee + 300
    label = "Muscle Gain Target"
else:
    target = tdee
    label = "Maintenance"

col1, col2, col3 = st.columns(3)
col1.metric("🔥 BMR (Base)", f"{round(bmr)} kcal")
col2.metric("⚡ TDEE (Daily Need)", f"{tdee} kcal")
col3.metric(f"🎯 {label}", f"{target} kcal")

# Macro breakdown chart
protein = round(target * 0.30 / 4)
carbs = round(target * 0.45 / 4)
fats = round(target * 0.25 / 9)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 🥗 Recommended Macro Split")

col_chart, col_info = st.columns([1, 1])

with col_chart:
    fig_pie = go.Figure(go.Pie(
        labels=['🍗 Protein', '🍚 Carbs', '🫙 Fats'],
        values=[30, 45, 25],
        hole=0.5,
        marker=dict(colors=['#6c63ff', '#43e97b', '#ff6584']),
        textfont=dict(color='white', size=14)
    ))
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=280,
        margin=dict(t=20, b=20),
        showlegend=True,
        legend=dict(font=dict(color='white'))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_info:
    st.markdown(f"""
    <br><br>
    <div style="background: linear-gradient(135deg, #1e1e3a, #2d2d4e); border: 1px solid #3d3d6e; border-radius: 12px; padding: 20px;">
        <h4 style="color: white;">Daily Targets</h4>
        <p style="color: #6c63ff; font-size: 1.1rem;">💪 Protein: <b>{protein}g</b></p>
        <p style="color: #43e97b; font-size: 1.1rem;">🍚 Carbs: <b>{carbs}g</b></p>
        <p style="color: #ff6584; font-size: 1.1rem;">🫙 Fats: <b>{fats}g</b></p>
        <hr style="border-color: #3d3d6e;">
        <p style="color: #a0a0c0; font-size: 0.85rem;">Based on your goal: <b>{goal}</b></p>
    </div>
    """, unsafe_allow_html=True)
