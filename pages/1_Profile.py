import streamlit as st
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import ensure_authenticated, get_current_user, render_auth_status
from utils.storage import load_user_bucket, update_user_bucket
from utils.ui import apply_base_theme

st.set_page_config(page_title="My Profile", page_icon="👤", layout="centered")
apply_base_theme()
ensure_authenticated()
render_auth_status()

active_user = get_current_user()

def save_profile(profile):
    update_user_bucket(active_user, {"profile": profile})

st.title("👤 My Profile")
st.caption("Tell us about yourself so we can personalize your diet plan")
st.divider()

# Pre-fill if profile exists
p = st.session_state.get('profile', {})
if not p:
    p = load_user_bucket(active_user).get('profile', {})
    if p:
        st.session_state['profile'] = p

st.subheader("📋 Basic Information")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Your Name", value=p.get('name', ''), placeholder="e.g. Rahul")
    age = st.number_input("Age", min_value=10, max_value=100, value=p.get('age', 25))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male","Female","Other"].index(p.get('gender','Male')))
with col2:
    weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=float(p.get('weight', 65.0)), step=0.5)
    height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(p.get('height', 165.0)), step=0.5)

st.divider()
st.subheader("🎯 Your Health Goal")
goals = ["⚖️ Lose Weight", "💪 Gain Muscle", "🧘 Maintain Weight", "❤️ Eat Healthy"]
goal_idx = goals.index(p.get('goal', "⚖️ Lose Weight")) if p.get('goal') in goals else 0
goal = st.radio("What do you want to achieve?", goals, index=goal_idx, horizontal=True)

st.divider()
st.subheader("🍽️ Diet Preferences")
col3, col4 = st.columns(2)
diet_options = ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"]
activity_options = [
    "Sedentary (Office job, no exercise)",
    "Lightly Active (Light exercise 1-3 days)",
    "Moderately Active (Exercise 3-5 days)",
    "Very Active (Hard exercise 6-7 days)"
]
with col3:
    diet_idx = diet_options.index(p.get('diet_type', 'Vegetarian')) if p.get('diet_type') in diet_options else 0
    diet_type = st.selectbox("Diet Type", diet_options, index=diet_idx)
with col4:
    act_idx = activity_options.index(p.get('activity_level', activity_options[0])) if p.get('activity_level') in activity_options else 0
    activity_level = st.selectbox("Activity Level", activity_options, index=act_idx)

allergies = st.multiselect(
    "Any Food Allergies?",
    ["Dairy", "Gluten", "Nuts", "Soy", "Eggs", "Seafood", "None"],
    default=p.get('allergies', ["None"])
)

if "None" in allergies and len(allergies) > 1:
    allergies = [item for item in allergies if item != "None"]

st.divider()
st.subheader("📊 Your BMI")
bmi = weight / ((height / 100) ** 2)
col5, col6, col7 = st.columns(3)
col5.metric("BMI", f"{bmi:.1f}")
col6.metric("Weight", f"{weight} kg")
col7.metric("Height", f"{height} cm")

if bmi < 18.5:
    st.warning("⚠️ Underweight — Focus on gaining healthy weight")
elif 18.5 <= bmi < 25:
    st.success("✅ Normal Weight — Keep it up!")
elif 25 <= bmi < 30:
    st.warning("⚠️ Overweight — Consider balanced diet and exercise")
else:
    st.error("❗ Obese — Please consult a doctor")

st.divider()
if st.button("💾 Save Profile", type="primary", use_container_width=True):
    if not name:
        st.error("Please enter your name!")
    else:
        profile = {
            "name": name, "age": age, "gender": gender,
            "weight": weight, "height": height, "bmi": round(bmi, 1),
            "goal": goal, "diet_type": diet_type,
            "activity_level": activity_level, "allergies": allergies
        }
        st.session_state['profile'] = profile
        save_profile(profile)
        st.success(f"✅ Profile saved! Welcome, {name}! 🎉")
        st.balloons()

if st.button("📥 Reload Saved Profile", use_container_width=True):
    saved_profile = load_user_bucket(active_user).get("profile")
    if saved_profile:
        st.session_state['profile'] = saved_profile
        st.success("Saved profile loaded successfully.")
        st.rerun()
    else:
        st.info("No saved profile found yet.")
