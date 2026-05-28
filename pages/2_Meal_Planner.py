import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#from utils.gemini_helper import generate_meal_plan
from utils.auth import ensure_authenticated, get_current_user, render_auth_status
from utils.groq_helper import generate_meal_plan
from utils.storage import append_to_user_bucket_list, load_user_bucket, update_user_bucket
from utils.ui import apply_base_theme

st.set_page_config(page_title="AI Meal Planner", page_icon="🍛", layout="centered")
apply_base_theme()
ensure_authenticated()
render_auth_status()

active_user = get_current_user()

st.title("🍛 AI Meal Planner")
st.caption("Get a personalized 7-day Indian meal plan just for you!")

st.divider()

# --- Check if profile exists ---
if not st.session_state.get('profile'):
    saved_profile = load_user_bucket(active_user).get('profile')
    if saved_profile:
        st.session_state['profile'] = saved_profile

if not st.session_state.get('profile'):
    st.warning("⚠️ Please fill your profile first!")
    st.page_link("pages/1_Profile.py", label="👉 Go to My Profile", icon="👤")
    st.stop()

profile = st.session_state['profile']

# --- Show Profile Summary ---
st.subheader(f"👋 Hello, {profile['name']}!")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 Goal", profile['goal'].split()[-1])
col2.metric("⚖️ Weight", f"{profile['weight']} kg")
col3.metric("📏 BMI", profile['bmi'])
col4.metric("🥗 Diet", profile['diet_type'])

st.divider()

# --- Generate Meal Plan ---
st.subheader("🤖 Generate Your Meal Plan")

col5, col6 = st.columns(2)
with col5:
    days = st.selectbox("Plan Duration", ["7 Days (Full Week)", "3 Days (Short Plan)", "1 Day (Today's Plan)"])
with col6:
    cuisine_focus = st.selectbox("Cuisine Focus", [
        "Mixed Indian",
        "North Indian",
        "South Indian",
        "Gujarati / Rajasthani",
        "Bengali"
    ])

special_notes = st.text_area(
    "Any special instructions? (optional)",
    placeholder="e.g. I don't like bitter gourd, prefer less spicy food, have diabetes..."
)

if st.button("✨ Generate My Meal Plan", type="primary", use_container_width=True):
    with st.spinner("🤖 AI is preparing your personalized meal plan... Please wait!"):

        # Add extra context to profile
        enhanced_profile = profile.copy()
        enhanced_profile['days'] = days
        enhanced_profile['cuisine_focus'] = cuisine_focus
        enhanced_profile['special_notes'] = special_notes if special_notes else "None"

        meal_plan = generate_meal_plan(enhanced_profile)

        st.session_state['meal_plan'] = meal_plan
        update_user_bucket(active_user, {"meal_plan": meal_plan})
        append_to_user_bucket_list(
            active_user,
            "meal_plan_history",
            {
                "saved_at": datetime.now().strftime("%d %b %Y, %H:%M"),
                "name": profile.get("name", "User"),
                "goal": profile.get("goal", ""),
                "plan_duration": days,
                "cuisine_focus": cuisine_focus,
                "plan": meal_plan,
            },
            limit=20,
        )
        st.success("✅ Your meal plan is ready!")

# --- Display Meal Plan ---
if 'meal_plan' in st.session_state:
    st.divider()
    st.subheader("📋 Your Personalized Meal Plan")

    st.markdown(st.session_state['meal_plan'])

    st.divider()

    # Download button
    st.download_button(
        label="📥 Download Meal Plan",
        data=st.session_state['meal_plan'],
        file_name=f"meal_plan_{profile['name']}.txt",
        mime="text/plain",
        use_container_width=True
    )

st.divider()
st.subheader("🗂️ Recent Meal Plans")
plan_history = load_user_bucket(active_user).get("meal_plan_history", [])

if plan_history:
    labels = [
        f"{idx + 1}. {item.get('saved_at', 'Unknown')} - {item.get('plan_duration', 'Plan')}"
        for idx, item in enumerate(reversed(plan_history))
    ]
    selected_label = st.selectbox("Choose a saved plan", labels)
    selected_index = labels.index(selected_label)
    selected_plan = list(reversed(plan_history))[selected_index]
    with st.expander("View Selected Plan", expanded=False):
        st.caption(
            f"Goal: {selected_plan.get('goal', '-')}, Cuisine: {selected_plan.get('cuisine_focus', '-')}"
        )
        st.markdown(selected_plan.get("plan", "No content available."))
else:
    st.info("No saved meal plans yet. Generate one to build your history.")
