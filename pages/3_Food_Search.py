import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import ensure_authenticated, render_auth_status
from utils.groq_helper import analyze_nutrition
from utils.ui import apply_base_theme

st.set_page_config(page_title="Food Nutrition Search", page_icon="🔍", layout="centered")
apply_base_theme()
ensure_authenticated()
render_auth_status()

st.title("🔍 Food Nutrition Search")
st.caption("Search nutrition info for any Indian food item!")

st.divider()

# --- Search Section ---
st.subheader("🍛 Search Any Indian Food")

col1, col2 = st.columns([2, 1])

with col1:
    food_item = st.text_input(
        "Food Item",
        placeholder="e.g. Dal Makhani, Idli, Samosa, Paneer Butter Masala..."
    )

with col2:
    quantity = st.text_input(
        "Quantity",
        placeholder="e.g. 1 bowl, 2 pieces, 100g",
        value="1 serving"
    )

# --- Quick Select Popular Foods ---
st.markdown("**⚡ Quick Select Popular Foods:**")

popular_foods = [
    "🍚 Dal Rice", "🫓 Roti", "🥘 Paneer Butter Masala",
    "🫔 Samosa", "🍳 Poha", "🥞 Dosa",
    "🍲 Rajma Chawal", "🥣 Upma", "🧆 Chole Bhature"
]

cols = st.columns(3)
for i, food in enumerate(popular_foods):
    with cols[i % 3]:
        if st.button(food, use_container_width=True):
            food_item = food.split(" ", 1)[1]  # Remove emoji
            st.session_state['quick_food'] = food_item

# Use quick selected food
if 'quick_food' in st.session_state and not food_item:
    food_item = st.session_state['quick_food']

st.divider()

# --- Analyze Button ---
if st.button("🔬 Analyze Nutrition", type="primary", use_container_width=True):
    if not food_item:
        st.error("Please enter a food item!")
    else:
        with st.spinner(f"🤖 Analyzing nutrition for {food_item}..."):
            result = analyze_nutrition(food_item, quantity)
            st.session_state['nutrition_result'] = result
            st.session_state['searched_food'] = food_item

# --- Display Results ---
if 'nutrition_result' in st.session_state:
    st.divider()
    st.subheader(f"📊 Nutrition Analysis: {st.session_state.get('searched_food', '')}")
    st.markdown(st.session_state['nutrition_result'])

    st.divider()

    # Compare two foods
    st.subheader("⚖️ Want to compare with another food?")
    compare_food = st.text_input("Enter another food to compare", placeholder="e.g. Brown Rice, Quinoa...")

    if st.button("🔄 Compare", use_container_width=True):
        if compare_food:
            with st.spinner(f"Analyzing {compare_food}..."):
                compare_result = analyze_nutrition(compare_food, quantity)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {st.session_state.get('searched_food', 'Food 1')}")
                st.markdown(st.session_state['nutrition_result'])
            with col2:
                st.markdown(f"### {compare_food}")
                st.markdown(compare_result)
        else:
            st.error("Please enter a food to compare!")
