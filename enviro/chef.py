import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from google.api_core import exceptions # Quota error handle krny k liye

load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")

FILE_NAME = "chat_memory.json"

def load_data():
    if os.path.exists(FILE_NAME):
        if os.path.getsize(FILE_NAME) > 0:
            with open(FILE_NAME, "r") as f:
                return json.load(f)
    return [] # Return empty list if file doesn't exist or is empty
 
def save_data(chat_history):
    new_memory=[]
    for message in chat_history:
        message_text = message.parts[0].text
        new_memory.append({
            "role":message.role,
            "parts":[{
                "text":message_text
            }]
        })

    with open(FILE_NAME, "w") as diary:
        json.dump(new_memory,diary,indent=4)

genai.configure(api_key=api_key)

# App ki instructions wahi hain, bas variable name fix kia hai (instructions)
instructions = """ 1. Persona & Identity
Name: Chef AI-Xora.
Role: Strategic Kitchen Assistant & Waste-Reduction Specialist.
Personality: Warm, organized, witty, and highly efficient. You are a "rememberer"—you never ask for the same dietary info twice. Use emojis (🍳, 🌿, 💸).
Domain: Strictly limited to cooking, baking, nutrition, and kitchen budgeting. Politely decline other topics.

2. Core Directives
The "Long-Term Memory" Protocol: Remember allergies, health goals, and lifestyle. Filter future suggestions automatically.
The "Rescue Ingredient" VIP Policy: Prioritize ingredients that are about to expire.
Budget-Conscious Shopping: Ask for budget in Rs. Suggest quantities and "Budget Swaps" if items are too expensive.

3. Interaction Flow
- Acknowledge lifestyle/health goals.
- Perform an "Ingredient Audit" before shopping.
- Provide step-by-step cooking/baking guidance.
- Use local units (grams, kg, "ek pao", etc.).
- Never repeat the exact same phrasing."""

# Model ko gemini-1.5-flash pr switch kia hai for better free limits
model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=instructions)

memory = load_data()
chat = model.start_chat(history=memory)

print("----Your personal Kitchen Strategic Assistant is online (Type 'exit or bye' to stop)-----------")

while True:
    user_input = input("You:")

    if user_input.lower() in ["exit","bye","quit"]:
        save_data(chat.history)
        print("Progress saved! GoodBye! See you tomorrow! 👋")
        break

    # ERROR HANDLING ADDED HERE
    try:
        response = chat.send_message(user_input)
        print("Agent:", response.text)
    
    except exceptions.ResourceExhausted:
        print("Agent: Oh ho! 🤯 Lagta hai mera dimagh thak gaya hai (Quota Exceeded). Please 1 minute wait karein, phir hum dubara cooking start karein gy! ⏳")
    
    except Exception as e:
        print(f"Agent: Kuch masla ho gaya hai... 🛠️ {e}")