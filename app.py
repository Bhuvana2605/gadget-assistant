import streamlit as st
import requests
import json

# ----------------------------
# App Setup
# ----------------------------
st.set_page_config(page_title="📱 Gadget Assistant", page_icon="🤖")
st.title("🤖 AIRA – Gadget Advisor")
st.markdown("Ask about phones, laptops, tablets, or any gadgets. Get expert help instantly!")

# ----------------------------
# Hugging Face API Settings
# ----------------------------
HF_TOKEN = st.secrets["HF_TOKEN"]  # Add this in Streamlit secrets
MODEL = "HuggingFaceH4/zephyr-7b-beta"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ----------------------------
# System Prompt
# ----------------------------
SYSTEM_PROMPT = """You are AIRA, a helpful and knowledgeable AI assistant that helps users choose the best electronic gadgets such as smartphones, laptops, tablets, etc., based on their budget, use-case, and personal preferences.

Your tone is friendly, clear, and concise. Your goal is to make the user feel confident in their buying decision, especially if they are confused or unsure.

Always follow this response format:
1. Ask clarifying questions (if needed) about budget, use-case (e.g. gaming, office, college), and preferences (e.g. battery life, camera, display).
2. Present recommendations as **bullet points** for easy reading.
3. For each recommended device, give:
   - Device Name
   - Key Features
   - Pros
   - Cons
4. End by asking: “Would you like more options or details on any of these?”"""

# ----------------------------
# Chat State
# ----------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ----------------------------
# HF Query Function
# ----------------------------
def query_zephyr(prompt):
    formatted = f"<|system|>\n{SYSTEM_PROMPT.strip()}\n<|user|>\n{prompt.strip()}\n<|assistant|>\n"
    payload = {
        "inputs": formatted,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 512,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result[0]["generated_text"].strip()
        elif response.status_code == 503:
            return "⏳ The model is still loading, try again in a few seconds."
        elif response.status_code == 401:
            return "🔒 Invalid or missing Hugging Face token."
        elif response.status_code == 402:
            return "❌ You’ve run out of HF inference credits. Use a smaller model or upgrade."
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"🚫 Failed to connect: {str(e)}"

# ----------------------------
# Chat Input
# ----------------------------
st.markdown("### 💬 Chat")
user_input = st.text_input("Ask your gadget question", placeholder="e.g., Best laptop under ₹50,000")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        reply = query_zephyr(user_input)
        st.session_state.chat.append({"role": "user", "content": user_input})
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

# ----------------------------
# Show Chat History
# ----------------------------
for message in reversed(st.session_state.chat):
    with st.chat_message(message["role"]):
        st.markdown(f"**{message['role'].capitalize()}:** {message['content']}")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("Built with ❤️ using Zephyr 7B on Hugging Face Inference API")
