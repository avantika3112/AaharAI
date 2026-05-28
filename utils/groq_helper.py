import streamlit as st
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_groq(prompt: str, system: str = "You are a helpful Indian dietician assistant.") -> str:
    """Call Groq API with a prompt"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ Groq API key not found! Please check your .env file.")
        return "Error: API key not found."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


def generate_meal_plan(profile: dict) -> str:
    """Generate a personalized weekly meal plan based on user profile"""

    system = "You are an expert Indian dietician with 10+ years of experience. You specialize in creating practical, delicious Indian meal plans."

    prompt = f"""
Create a detailed {profile.get('days', '7 Days')} meal plan for:

Name: {profile.get('name')}
Age: {profile.get('age')} years | Gender: {profile.get('gender')}
Weight: {profile.get('weight')} kg | Height: {profile.get('height')} cm | BMI: {profile.get('bmi')}
Health Goal: {profile.get('goal')}
Diet Type: {profile.get('diet_type')}
Activity Level: {profile.get('activity_level')}
Cuisine Focus: {profile.get('cuisine_focus', 'Mixed Indian')}
Food Allergies: {', '.join(profile.get('allergies', ['None']))}
Special Instructions: {profile.get('special_notes', 'None')}

Instructions:
- Use only Indian foods (dal, sabzi, roti, rice, idli, dosa, poha, upma, etc.)
- Include Breakfast, Lunch, Evening Snack, and Dinner for each day
- Mention approximate calories for each meal
- Keep it practical, tasty and easy to prepare at home
- Format clearly day by day with emojis
"""
    return call_groq(prompt, system)


def analyze_nutrition(food_item: str, quantity: str) -> str:
    """Analyze nutrition of a given Indian food item"""

    system = "You are an expert nutritionist specializing in Indian cuisine and food science."

    prompt = f"""
Analyze the nutritional content of: {quantity} of {food_item}

Provide a detailed breakdown:
1. 🔥 Calories
2. 💪 Protein (g)
3. 🍚 Carbohydrates (g)
4. 🫙 Fats (g)
5. 🌾 Fiber (g)
6. 💊 Key vitamins & minerals
7. ✅ Health benefits
8. ⚠️ Any important notes

Format clearly with sections and emojis.
"""
    return call_groq(prompt, system)


def chat_with_dietician(user_message: str, chat_history: list, profile: dict = None) -> str:
    """Chat with AI dietician"""

    profile_context = ""
    if profile:
        profile_context = f"""
User Profile:
- Name: {profile.get('name', 'User')}
- Age: {profile.get('age')}, Gender: {profile.get('gender')}
- Weight: {profile.get('weight')} kg, Height: {profile.get('height')} cm, BMI: {profile.get('bmi')}
- Goal: {profile.get('goal')} | Diet: {profile.get('diet_type')}
"""

    system = f"""You are a friendly, knowledgeable Indian dietician assistant. 
You specialize in Indian cuisine and nutrition. Give practical, personalized advice.
Always suggest Indian food alternatives. Be encouraging and concise.
{profile_context}"""

    # Build messages with history
    messages = [{"role": "system", "content": system}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: API key not found."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"
