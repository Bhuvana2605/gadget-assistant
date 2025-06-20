import streamlit as st
import requests
import os
import json

# ----------------------------
# App Setup
# ----------------------------
st.set_page_config(page_title="📱 Gadget Assistant", page_icon="🤖")
st.title("🤖 AIRA – Gadget Advisor")
st.markdown("Ask about phones, laptops, tablets, or any gadgets. Get expert help instantly!")

# ----------------------------
# System Prompt
# ----------------------------
SYSTEM_PROMPT = """You are AIRA, a helpful and knowledgeable AI assistant that helps users choose the best electronic gadgets such as smartphones, laptops, tablets, etc., based on their budget, use-case, and personal preferences.

Your tone is friendly, clear, and concise. Your goal is to make the user feel confident in their buying decision, especially if they are confused or unsure.

Always follow this response format:
1. Ask clarifying questions (if needed) about budget, use-case (e.g. gaming, office, college), and preferences (e.g. battery life, camera, display).
2. Present recommendations as bullet points for easy reading.
3. For each recommended device, give:
   - Device Name
   - Key Features
   - Pros
   - Cons
4. End by asking: “Would you like more options or details on any of these?”"""

# ----------------------------
# Hugging Face API Setup
# ----------------------------
HF_TOKEN = st.secrets["HF_TOKEN"]  # Add this in Streamlit secrets
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-rw-1b"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def generate_response(prompt):
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}\n\nAssistant:"
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return response.json()[0]['generated_text'].split("Assistant:")[-1].strip()
        elif response.status_code == 503:
            return "⏳ Model is loading. Try again in a few seconds."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"🚫 Failed to connect: {str(e)}"

# ----------------------------
# Chat State
# ----------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ----------------------------
# Chat UI
# ----------------------------
st.markdown("### 💬 Chat")
user_input = st.text_input("Ask your gadget question", placeholder="e.g., Best laptop under ₹50,000")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        reply = generate_response(user_input)
        st.session_state.chat.append({"role": "user", "content": user_input})
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

# Display Chat
for message in reversed(st.session_state.chat):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"*You:* {message['content']}")
    else:
        with st.chat_message("assistant"):
            st.markdown(f"*Assistant:* {message['content']}")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("Built with ❤ using Falcon RW 1B on Hugging Face Inference API")
