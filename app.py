import streamlit as st
import requests
import json

# ----------------------------
# App Setup
# ----------------------------
st.set_page_config(page_title="📱 Gadget Assistant", page_icon="🤖")
st.title("🤖 Gadget Advisor")
st.markdown("Ask about phones, laptops, tablets, or any gadgets. Get expert help instantly!")

# ----------------------------
# Hugging Face Settings
# ----------------------------
HF_TOKEN = st.secrets["HF_TOKEN"]  # Add your token to Streamlit Secrets
MODEL = "HuggingFaceH4/zephyr-7b-beta"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ----------------------------
# System Prompt
# ----------------------------
SYSTEM_PROMPT = """
You are a helpful and knowledgeable gadget advisor. You assist users in choosing the best electronic devices — including smartphones, laptops, tablets, smartwatches, and more.

Always consider the user’s needs such as budget, usage (e.g., gaming, work, photography), and preferences (e.g., battery life, camera quality, performance). Provide detailed but easy-to-understand explanations of device specifications like processor, RAM, camera setup, display type, battery, and software.

Compare models clearly when asked, and suggest the best options available in the market as of 2025. Be honest and unbiased — highlight both pros and cons.

Your tone is friendly, professional, and trustworthy. You do not fake information — if you're unsure, explain that and suggest how the user could verify it.
"""

# ----------------------------
# Conversation History
# ----------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ----------------------------
# Query HF API
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
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"🚫 Failed to connect: {str(e)}"

# ----------------------------
# Chat Input
# ----------------------------
st.markdown("### 💬 Chat")
user_input = st.text_input("Ask your gadget question", placeholder="e.g., Best phone under ₹25,000")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        reply = query_zephyr(user_input)
        st.session_state.chat.append({"role": "user", "content": user_input})
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

# ----------------------------
# Show Chat
# ----------------------------
for message in reversed(st.session_state.chat):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"**You:** {message['content']}")
    else:
        with st.chat_message("assistant"):
            st.markdown(f"**Assistant:** {message['content']}")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("Built with ❤️ using Zephyr 7B on Hugging Face Inference API")
