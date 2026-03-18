import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from google.api_core import exceptions
import base64

# --- CONFIGURATION & SETUP ---
load_dotenv()

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:    
    api_key = os.getenv("GEMINI_API_KEY")
    
    
FILE_NAME = "chat_memory.json"

st.set_page_config(page_title="Chef AI-Xora", page_icon="👨‍🍳", layout="wide")

# --- UI THEME LOGIC ---
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# --- IMAGE ENCODING FUNCTION ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Laptop se image load karne ke liye
try:
    # Aapki file ka sahi naam yahan hona chahiye
    img_base64 = get_base64("gradient_sidebar.jpg")
    sidebar_img = f"data:image/png;base64,{img_base64}"
except Exception as e:
    # Agar file na mile to koi online image ya khali chor dein
    sidebar_img = "" 

# --- SMART DYNAMIC CSS ---
if st.session_state.theme == "dark":
    bg_color = "#0E1117"
    text_color = "#FFFFFF"
    sidebar_overlay = "rgba(26, 28, 36, 0.2)" 
    btn_bg = "#262730"
    btn_text = "#FFFFFF"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    sidebar_overlay = "rgba(240, 242, 246, 0.2)" 
    btn_bg = "#FFFFFF"
    btn_text = "#000000"

st.markdown(f"""
    <style>
        .stApp {{ 
            background-color: {bg_color}; 
            color: {text_color}; 
        }}
        
        [data-testid="stSidebar"] {{
            background-image: linear-gradient({sidebar_overlay}, {sidebar_overlay}), url("{sidebar_img}");
            background-size: cover; /* '100% 100%' se image khinch sakti hai, 'cover' best hai */
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] span {{ 
            color: {text_color} !important; 
        }}
        
        .stMarkdown, p, h1, h2, h3, label, li {{ 
            color: {text_color} !important; 
        }}

        [data-testid="stSidebar"] .stButton > button {{
            background-color: {btn_bg} !important;
            color: {btn_text} !important;
            border: 1px solid #4B4B4B !important;
            width: 100%;
            border-radius: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)

# --- DATA PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []

def save_data(chat_history):
    new_memory = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in chat_history]
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
- Strictly avoid non-food topics (politics, sports, study , weather etc.).

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
- and also ask for any food item allergies and remember them to avoid in future
- use table where neccessary
- make sure answer is not too long make it concise as much as possible.

note: Provide the recipe first, then ask for the budget to optimize the shopping list.
"""
model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=instructions)

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("images-removebg-preview.png", width=200) 
    except:
        st.header("👨‍🍳 Chef AI-Xora")
    
    st.title("Chef AI-Xora")
    st.subheader("Your Strategic Kitchen Mentor")
    st.write("Developed by: [Shifa Saeed]")
    st.markdown("---")
    st.write("Ready to transform your kitchen into a 5-star studio? I handle the strategy, you handle the heat! 🔥")
    
    theme_label = "☀️ Switch to Light Mode" if st.session_state.theme == "dark" else "🌙 Switch to Dark Mode"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()
    
    if st.button("🗑️ Reset Kitchen Memory", use_container_width=True):
        if os.path.exists(FILE_NAME): os.remove(FILE_NAME)
        st.session_state.messages = []
        st.rerun()

# --- MAIN UI ---
st.title("👨‍🍳 Kitchen Strategy Hub")
st.caption("Turning ingredients into masterpieces, one step at a time.")

if "messages" not in st.session_state:
    saved_history = load_data()
    st.session_state.messages = []
    if not saved_history:
        # Initial Welcome Message from Chef
        st.session_state.messages.append({"role": "assistant", "content": "Welcome to my kitchen! 🍳 I'm Chef AI-Xora. What delicious masterpiece are we whipping up today?"})
    else:
        for msg in saved_history:
            st.session_state.messages.append({"role": "assistant" if msg["role"] == "model" else "user", "content": msg["parts"][0]["text"]})

for message in st.session_state.messages:
    avatar = "👨‍🍳" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("Tell me a dish or an ingredient..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="👨‍🍳"):
        with st.spinner("Chef AI-Xora is sharpening the knives... 🔪"):
            history_for_gemini = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in st.session_state.messages[:-1]]
            try:
                chat_session = model.start_chat(history=history_for_gemini)
                response = chat_session.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                save_data(st.session_state.messages)
            except Exception as e:
                st.error(f"Kitchen Error: {e}")