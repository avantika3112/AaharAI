import google.generativeai as genai
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_gemini():
    """Initialize Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ Gemini API key not found! Please check your .env file.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")

def generate_meal_plan(profile: dict) -> str:
    """Generate a personalized weekly meal plan based on user profile"""
    model = initialize_gemini()
    if not model:
        return "Error: Could not initialize AI model."

    prompt = f"""
You are an expert Indian dietician. Create a detailed 7-day meal plan for the following person:

Name: {profile.get('name')}
Age: {profile.get('age')} years
Gender: {profile.get('gender')}
Weight: {profile.get('weight')} kg
Height: {profile.get('height')} cm
BMI: {profile.get('bmi')}
Health Goal: {profile.get('goal')}
Diet Type: {profile.get('diet_type')}
Activity Level: {profile.get('activity_level')}
Food Allergies: {', '.join(profile.get('allergies', ['None']))}

Instructions:
- Use only Indian foods (dal, sabzi, roti, rice, idli, dosa, poha, etc.)
- Include breakfast, lunch, evening snack, and dinner for each day
- Mention approximate calories for each meal
- Keep it practical and easy to prepare
- Format it clearly day by day

Provide the meal plan in a clean, readable format.
"""
    response = model.generate_content(prompt)
    return response.text

def analyze_nutrition(food_item: str, quantity: str) -> str:
    """Analyze nutrition of a given Indian food item"""
    model = initialize_gemini()
    if not model:
        return "Error: Could not initialize AI model."

    prompt = f"""
You are an expert nutritionist specializing in Indian food.
Analyze the nutritional content of: {quantity} of {food_item}

Provide:
1. Calories
2. Protein (g)
3. Carbohydrates (g)
4. Fats (g)
5. Fiber (g)
6. Key vitamins/minerals
7. Health benefits
8. Any important notes

Format the response clearly with sections.
"""
    response = model.generate_content(prompt)
    return response.text

def chat_with_dietician(user_message: str, chat_history: list, profile: dict = None) -> str:
    """Chat with AI dietician"""
    model = initialize_gemini()
    if not model:
        return "Error: Could not initialize AI model."

    profile_context = ""
    if profile:
        profile_context = f"""
User Profile:
- Name: {profile.get('name', 'User')}
- Age: {profile.get('age')}, Gender: {profile.get('gender')}
- Weight: {profile.get('weight')} kg, Height: {profile.get('height')} cm
- Goal: {profile.get('goal')}
- Diet Type: {profile.get('diet_type')}
"""

    system_prompt = f"""You are a friendly and knowledgeable Indian dietician assistant. 
You specialize in Indian cuisine and nutrition. Give practical, personalized advice.
Always be encouraging and suggest Indian food alternatives.
Keep responses concise and helpful.
{profile_context}"""

    # Build conversation
    full_prompt = system_prompt + "\n\nConversation so far:\n"
    for msg in chat_history[-6:]:  # last 6 messages for context
        role = "User" if msg["role"] == "user" else "Dietician"
        full_prompt += f"{role}: {msg['content']}\n"
    full_prompt += f"User: {user_message}\nDietician:"

    response = model.generate_content(full_prompt)
    return response.text
