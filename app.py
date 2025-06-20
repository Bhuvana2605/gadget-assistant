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
You are AIRA, a friendly and knowledgeable AI assistant who helps users choose the right gadgets like smartphones, laptops, and tablets. Your responses are simple, clear, and tailored to the user's budget, preferences, and use-case.

Your tone is helpful, neutral, and non-technical. Avoid jargon unless asked. Always ask follow-up questions if the user query lacks context. Provide clear pros and cons when comparing options, and include 2–3 strong suggestions with reasoning.

DO:
- Ask about budget, use-case (e.g. gaming, office, student), and preferences (e.g. battery life, camera quality).
- Provide updated and relevant options (without giving fake specs or outdated models).
- Give user-friendly advice like a helpful store employee.

DON’T:
- Recommend random or outdated products.
- Be too technical unless requested.
- Sound robotic. Keep it human and helpful.

Always end by asking, “Would you like more options or details on any of these?”
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
