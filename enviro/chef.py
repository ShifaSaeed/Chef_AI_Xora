import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from google.api_core import exceptions

# --- CONFIGURATION & SETUP ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
FILE_NAME = "chat_memory.json"

st.set_page_config(page_title="Chef AI-Xora", page_icon="👨‍🍳", layout="wide")

# --- UI THEME LOGIC ---
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# --- SMART DYNAMIC CSS ---
if st.session_state.theme == "dark":
    bg_color = "#0E1117"
    text_color = "#FFFFFF"
    sidebar_bg = "#1A1C24"
    btn_bg = "#262730"
    btn_text = "#FFFFFF"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    sidebar_bg = "#F0F2F6"
    btn_bg = "#FFFFFF"
    btn_text = "#000000"

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
        }}
        /* Sidebar Text and Description Visibility */
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] span {{
            color: {text_color} !important;
        }}
        /* Global Text Color */
        .stMarkdown, p, h1, h2, h3, label, li {{
            color: {text_color} !important;
        }}
        /* Sidebar Buttons Styling */
        [data-testid="stSidebar"] .stButton > button {{
            background-color: {btn_bg} !important;
            color: {btn_text} !important;
            border: 1px solid #4B4B4B !important;
            width: 100%;
            border-radius: 8px;
        }}
        /* Prompt area remains default Streamlit for stability */
    </style>
    """, unsafe_allow_html=True)

# --- DATA PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []

def save_data(chat_history):
    new_memory = []
    for message in chat_history:
        new_memory.append({
            "role": "model" if message["role"] == "assistant" else "user",
            "parts": [{"text": message["content"]}]
        })
    with open(FILE_NAME, "w") as diary:
        json.dump(new_memory, diary, indent=4)

# --- GEMINI AI SETUP ---
genai.configure(api_key=api_key)
instructions = """ 
1. Persona & Identity
Name: Chef AI-Xora.
Role: Strategic Kitchen Assistant.
Personality: Warm, organized, and helpful with emojis (🍳, 🍰, ☕).

2. Domain & Content
- You MUST provide recipes for anything requested related to cooking and baking (Cakes, Coffee, Pizza, etc.).
- NEVER refuse a recipe request. 
- Strictly avoid non-food topics (politics, sports, etc.).

3. The "Xora Strategy" Flow (Follow this strictly):
Step 1: IMMEDIATELY provide the full, delicious recipe the user asked for.
Step 2: After the recipe, perform an "Ingredient Audit." Ask the user what they already have at home.
Step 3: Ask for their Budget (Rs).
Step 4: Generate a smart shopping list for only the missing items based on that budget.

4. Core Rules:
- If a user mentions an ingredient is "wilting" or "expiring," make it the VIP of the recipe.
- Remember dietary goals/allergies from previous turns (Memory).
- Use local units (grams, kg, "ek pao").
- Keep responses friendly and never repeat the same phrases.

note: Provide the recipe first, then ask for the budget to optimize the shopping list.

"""
model = genai.GenerativeModel(model_name='gemini-2.5-flash-lite', system_instruction=instructions)

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("images-removebg-preview.png", width=150) 
    except:
        st.header("👨‍🍳 Chef AI-Xora")
    
    st.title("Chef AI-Xora")
    st.subheader("Your Strategic Kitchen Mentor")
    st.markdown("---")
    
    # Description (Jo hata di thi, wo wapis aa gayi)
    st.write("Specialized in recipes, ingredient audits, and budget-friendly shopping lists.")
    
    
    # Theme Toggle Button
    theme_label = "☀️ Switch to Light Mode" if st.session_state.theme == "dark" else "🌙 Switch to Dark Mode"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()
    
    if st.button("🗑️ Clear Kitchen Memory", use_container_width=True):
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)
        st.session_state.messages = []
        st.rerun()

# --- MAIN UI ---
st.title("👨‍🍳 Kitchen Strategy Hub")
st.caption("Strategic roadmaps for your delicious meals.")

if "messages" not in st.session_state:
    saved_history = load_data()
    st.session_state.messages = []
    for msg in saved_history:
        st.session_state.messages.append({
            "role": "assistant" if msg["role"] == "model" else "user",
            "content": msg["parts"][0]["text"]
        })

for message in st.session_state.messages:
    avatar = "👨‍🍳" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("What are we cooking today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="👨‍🍳"):
        with st.spinner("Chef AI-Xora is preparing... 🍳"):
            history_for_gemini = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in st.session_state.messages[:-1]]
            try:
                chat_session = model.start_chat(history=history_for_gemini)
                response = chat_session.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                save_data(st.session_state.messages)
            except exceptions.ResourceExhausted:
                st.error("⚠️ Kitchen crowded (Quota Exceeded). Try in 1 minute.")
            except Exception as e:
                st.error(f"Error: {e}")